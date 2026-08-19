#!/usr/bin/env bash
''''true
# ── Stage 0: bash bootstrap ──────────────────────────────────────────────
# `bash README.md` sets Stage 0 env and hands off to Python for LLM bootstrap.
export TIGORC_STAGE="${TIGORC_STAGE:-0}"
export TIGORC_LLM_BASE="${TIGORC_LLM_BASE:-http://10.69.42.2:8000/v1}"
export TIGORC_LLM_MODEL="${TIGORC_LLM_MODEL:-Qwen3.6-27B-FP8}"
exec python3 "$0" "$@"
exit 0
'''
import sys
import os
import re
import json
import textwrap
import importlib.util
import argparse
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

"""
tigorc — Markdown spec compiler (polyglot bash/python)

Stage 0 (bash):  Read a .md spec → send each task to the LLM → write __compiled/*.py
Stage 2 (python): Read a pre-compiled spec → run as deterministic agent (no side effects)

Polyglot: both `bash README.md` and `python3 README.md` work.
  bash   → Stage 0 (LLM bootstrap, generates __compiled/*.py)
  python → Stage 2 (pure compiler, runs compiled agents)

Usage:
  python3 README.md                          # Stage 2: compile self → skeleton
  python3 README.md --bootstrap spec.md      # Stage 0: LLM bootstrap
  python3 README.md --run <name>             # Stage 2: run compiled agent
  python3 README.md --list                   # List compiled modules
  bash README.md [spec.md]                   # Stage 0: LLM bootstrap
"""

# ── Config ───────────────────────────────────────────────────────────────

LLM_BASE = os.environ.get("TIGORC_LLM_BASE", "http://10.69.42.2:8000/v1")
LLM_MODEL = os.environ.get("TIGORC_LLM_MODEL", "Qwen3.6-27B-FP8")
STAGE = os.environ.get("TIGORC_STAGE", "2")
COMPILED = Path("__compiled")

# ── YAML-lite (stdlib only) ──────────────────────────────────────────────

def parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse --- delimited YAML frontmatter."""
    m = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return {}
    raw = m.group(1)
    result: dict[str, Any] = {}
    list_key: Any = None
    for line in raw.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("- ") and list_key is not None:
            val = s[2:].strip()
            if ":" in val:
                k, v = val.split(":", 1)
                if not isinstance(result.get(list_key), list):
                    result[list_key] = []
                if not result[list_key] or not isinstance(result[list_key][-1], dict):
                    result[list_key].append({})
                result[list_key][-1][k.strip()] = v.strip()
            else:
                result.setdefault(list_key, []).append(val)
            continue
        if ":" in s:
            k, v = s.split(":", 1)
            k, v = k.strip(), v.strip()
            if v:
                result[k] = v
                list_key = None
            else:
                result[k] = []
                list_key = k
    return result


def parse_spec(path: str) -> dict[str, Any]:
    """Parse a .md spec file into structured dict."""
    p = Path(path)
    if not p.exists():
        print(f"ERR: spec not found: {path}", file=sys.stderr)
        sys.exit(1)
    text = p.read_text()
    meta = parse_frontmatter(text)
    meta["raw"] = text
    meta["path"] = str(p)
    return meta


# ── Task extraction ──────────────────────────────────────────────────────

def extract_tasks(raw: str, skip_names: set[str] | None = None) -> list[dict[str, str]]:
    """Extract tasks from ## headings."""
    if skip_names is None:
        skip_names = {"tigorc", "README"}
    sections = re.findall(r"##\s+(.*?)\n(.*?)(?=\n##|\Z)", raw, re.DOTALL)
    tasks: list[dict[str, str]] = []
    for title, body in sections:
        t = title.strip()
        if t in skip_names:
            continue
        tasks.append({
            "name": t.lower().replace(" ", "_").replace("-", "_"),
            "body": body.strip(),
        })
    return tasks


# ── LLM client (Stage 0) ────────────────────────────────────────────────

def llm_complete(prompt: str, system: str = "") -> str:
    """Call OpenAI-compatible chat completions."""
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    data = json.dumps({
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.1,
        "max_tokens": 4096,
    }).encode()
    req = urllib.request.Request(
        f"{LLM_BASE}/chat/completions",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read())
            return body["choices"][0]["message"]["content"]
    except urllib.error.URLError as e:
        print(f"LLM ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def bootstrap(spec_path: str) -> Path:
    """Stage 0: send each task to LLM, write __compiled/<name>.py."""
    spec = parse_spec(spec_path)
    name = spec.get("name", Path(spec_path).stem)  # type: ignore
    desc = spec.get("description", "")  # type: ignore
    raw = spec.get("raw", "")  # type: ignore
    tasks = extract_tasks(raw, skip_names={name, "tigorc", "README"})
    if not tasks:
        tasks = [{"name": "main", "body": str(desc)}]

    COMPILED.mkdir(exist_ok=True)

    system_prompt = (
        "You are a code generator. Output ONLY valid Python code. "
        "No markdown fences, no explanations. Write a complete module "
        "with functions and a main() entry point."
    )

    print(f"[bootstrap] Compiling '{name}' ({len(tasks)} task(s))...")

    module_parts: list[str] = [
        f'"""{name} — compiled by tigorc at {datetime.now(timezone.utc).isoformat()}"""',
        "import json",
        f'DESCRIPTION = {repr(str(desc))}',
        "",
    ]

    # Collect extra imports from LLM output and track which functions succeeded
    extra_imports: set[str] = set()
    generated_funcs: set[str] = set()
    run_funcs: list[str] = []
    for i, task in enumerate(tasks):
        fname = f"run_{task['name']}"
        run_funcs.append(fname)
        print(f"  [{i+1}/{len(tasks)}] {task['name']}")

        prompt = textwrap.dedent(f"""\
            Write ONLY a Python function `def {fname}(_this_file="") -> dict:` that implements:

            Context: {desc}
            Task: {task['name']}
            Details:
            {task['body'][:2000]}

            Rules:
            - Pure function, no network, no filesystem writes beyond reading
            - Only stdlib imports
            - Return dict with results
            - Handle errors gracefully with try/except
            - If loading files from __compiled/, SKIP the file at _this_file to avoid recursion
            - Output ONLY the function and its imports, nothing else
        """)

        code = llm_complete(prompt, system_prompt) or ""
        # Extract imports from FULL LLM response before we strip anything
        for imp_line in code.splitlines():
            stripped = imp_line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                extra_imports.add(stripped)

        code = re.sub(r"^```python\s*", "", code).rstrip()
        code = re.sub(r"```\s*$", "", code).rstrip()
        # Sometimes LLM wraps inner code in ```python too — strip all fences
        code = re.sub(r"```\w*\n", "", code)
        # Extract ONLY the run_* function — discard everything else the LLM hallucinates
        run_match = re.search(
            rf"(def {re.escape(fname)}\s*\(.*?\):.*?)(?=\ndef |if __name__|\Z)",
            code, re.DOTALL,
        )
        if run_match:
            code = run_match.group(1).rstrip()
            generated_funcs.add(fname)
        else:
            # Fallback: strip main() and if __name__ blocks from end
            code = re.sub(r"\ndef main\b.*", "", code).rstrip()
            code = re.sub(r"\nif __name__.*", "", code).rstrip()
            if not code.strip():
                generated_funcs.add(fname)  # Count as "tried"

        # Validate syntax — discard broken LLM output
        try:
            compile(code, f"<{fname}>", "exec")
        except SyntaxError:
            code = f"def {fname}(_this_file='') -> dict:\n    # LLM code had syntax error\n    return {{\"status\": \"syntax_error\"}}\n"

        module_parts.append(code + "\n\n")

    # Add collected imports at the top
    if extra_imports:
        # Insert after the initial import json line
        new_parts = [module_parts[0]]
        for imp in sorted(extra_imports):
            new_parts.append(imp)
        new_parts.append("")
        new_parts.extend(module_parts[1:])
        module_parts = new_parts

    # Add stub functions for any that LLM skipped entirely
    full_so_far = "\n".join(module_parts)
    for fname in run_funcs:
        if f"def {fname}(" not in full_so_far:
            module_parts.append(f"def {fname}(_this_file=\"\") -> dict:\n    return {{\"status\": \"skipped\"}}\n\n")

    # Assemble main() with recursion guard
    main_code = f'''
# Guard against recursive loading (e.g. run_run importing this file)
if not globals().get("_main_guard", False):
    globals()["_main_guard"] = True
else:
    raise RuntimeError("Recursive main() call detected")

def main() -> dict:
    """Run all tasks."""
    results = {{}}
    _this_file = __file__ if "__file__" in globals() else ""
    for _fn in [{", ".join(repr(f) for f in run_funcs)}]:
        print(f"Running {{_fn}}...")
        try:
            results[_fn] = globals()[_fn](_this_file)
        except Exception as e:
            results[_fn] = {{"error": str(e)}}
    print(json.dumps({{"tasks": list(results.keys()), "status": "complete"}}, indent=2))
    return results

if __name__ == "__main__":
    result = main()
'''
    module_parts.append(main_code)

    out = COMPILED / f"{name}.py"
    out.write_text("\n".join(module_parts))
    print(f"[bootstrap] -> {out}")
    return out


# ── Stage 2: Pure compiler ───────────────────────────────────────────────

def spec_compile(spec_path: str) -> str:
    """Compile spec -> Python skeleton (no LLM)."""
    spec = parse_spec(spec_path)
    name = spec.get("name", Path(spec_path).stem)  # type: ignore
    desc = spec.get("description", "")  # type: ignore
    raw = spec.get("raw", "")  # type: ignore
    tasks = extract_tasks(raw, skip_names={name, "tigorc", "README"})
    if not tasks:
        tasks = [{"name": "main", "body": str(desc)}]

    lines: list[str] = [
        f'"""{name} — tigorc compiled"""',
        "import sys",
        "import json",
        f'DESCRIPTION = {repr(str(desc))}',
        "",
    ]

    # Task functions (module level)
    for task in tasks:
        fname = f"run_{task['name']}"
        hint = (task["body"][:60].replace("\n", " ")).replace("'", "\\'")
        lines.extend([
            f"def {fname}(_this_file: str = '') -> dict:",
            f'    """{hint}"""',
            f"    # TODO: implement",
            f"    return {{\"status\": \"not_implemented\"}}",
            "",
        ])

    # main()
    lines.extend([
        "def main():",
        '    """Run all tasks and collect results."""',
        "    results = {}",
        "    _this_file = __file__ if '__file__' in globals() else ''",
        "",
    ])
    for task in tasks:
        fname = f"run_{task['name']}"
        lines.extend([
            f'    try:',
            f'        results["{fname}"] = {fname}(_this_file)',
            f'    except Exception as e:',
            f'        results["{fname}"] = {{"error": str(e)}}',
            "",
        ])
    lines.extend([
        '    print(f"Completed {len(results)} task(s)")',
        "    return results",
        "",
        "",
        'if __name__ == "__main__":',
        "    result = main()",
        "    json.dump(result, sys.stdout, indent=2, default=str)",
        "    print()",
    ])

    return "\n".join(lines)


def run_compiled(name: str) -> dict[str, Any]:
    """Load and run __compiled/<name>.py."""
    target = COMPILED / f"{name}.py"
    if not target.exists():
        alt = COMPILED / f"{name}"
        if alt.exists():
            target = alt
        else:
            print(f"ERR: compiled not found: {name}", file=sys.stderr)
            sys.exit(1)

    spec_obj = importlib.util.spec_from_file_location(name, str(target))
    if not spec_obj or not spec_obj.loader:
        print(f"ERR: cannot load {target}", file=sys.stderr)
        sys.exit(1)

    mod = importlib.util.module_from_spec(spec_obj)
    spec_obj.loader.exec_module(mod)
    return mod.main() if hasattr(mod, "main") else {}


def list_compiled() -> None:
    """Show available compiled modules."""
    if not COMPILED.exists():
        print("No compiled modules.")
        return
    for f in sorted(COMPILED.glob("*.py")):
        print(f"  {f.name} ({f.stat().st_size} bytes)")


# ── CLI ──────────────────────────────────────────────────────────────────

def cli() -> None:
    parser = argparse.ArgumentParser(
        description="tigorc — Markdown spec compiler",
        epilog=textwrap.dedent("""\
            Examples:
              python3 README.md                         # Stage 2: compile self
              python3 README.md --bootstrap self.md     # Stage 0: LLM bootstrap
              python3 README.md --run self              # Run compiled agent
              python3 README.md --list                  # List compiled
              bash README.md [spec.md]                  # Stage 0: LLM bootstrap
        """),
    )
    parser.add_argument("spec", nargs="?", default=None, help="Spec file path")
    parser.add_argument("--bootstrap", "-b", metavar="SPEC", help="LLM bootstrap")
    parser.add_argument("--run", "-r", metavar="NAME", help="Run compiled module")
    parser.add_argument("--list", "-l", action="store_true", help="List compiled")
    parser.add_argument("-o", "--output", metavar="FILE", help="Write compiled to FILE")
    parser.add_argument("--stage", default=None, help="Override TIGORC_STAGE")
    args = parser.parse_args()

    if args.stage:
        os.environ["TIGORC_STAGE"] = args.stage

    if args.list:
        list_compiled()
        return

    if args.bootstrap:
        bootstrap(args.bootstrap)
        return

    if args.run:
        result = run_compiled(args.run)
        print(json.dumps(result, indent=2, default=str))
        return

    # Default: compile spec or self
    if args.spec:
        code = spec_compile(args.spec)
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(code)
            print(f"Wrote {args.output}")
        else:
            print(code)
        return

    # No args: if stage=0, bootstrap self; else compile self
    self_path = str(Path(__file__).resolve())
    if STAGE == "0":
        print(f"[Stage 0] Bootstrapping from {self_path}")
        bootstrap(self_path)
    else:
        print("tigorc — Markdown spec compiler (Stage 2)")
        print(f"Compile: python3 {sys.argv[0]} <spec.md> [-o out.py]")
        print()
        list_compiled()


if __name__ == "__main__":
    cli()
