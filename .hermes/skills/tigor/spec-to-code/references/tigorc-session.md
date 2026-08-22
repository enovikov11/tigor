# tigorc session — 2026-08-19

## Context

Built `specs/tigorc/README.md` as a polyglot bash/python spec compiler in the tigor-ai monorepo. LLM on box at `10.69.42.2:8000` (Qwen3.6-27B-FP8, vLLM). Host cannot reach it directly — SSH tunnel via VM at `10.67.69.2:2222` failed, so bootstrap was run directly on VM:

```sh
scp -P 2222 README.md nixos@10.67.69.2:/tmp/tigorc/
ssh nixos@10.67.69.2 -p2222 \
  "cd /tmp/tigorc && TIGORC_LLM_BASE=http://localhost:8000/v1 \
  python3 README.md --bootstrap self.md"
```

## Issues resolved

1. **Polyglot `from __future__`**: Can't put `from __future__` after bash polyglot block — removed it, used `from typing import Any` instead.
2. **LLM generates code with markdown fences**: Added `re.sub(r"```\w*\n", "", code)` to strip inner fences too.
3. **LLM function extraction eats previous function body**: Regex `(def fname.*?)(?=\ndef |if __name__|\Z)` with `\n` before `def` fixes it — previously `\ndef main\(\)` was matching mid-function.
4. **Infinite recursion**: `run_run` loads `__compiled/self.py` → calls `main()` → calls `run_run` → ... Fixed with `_this_file` parameter + guard + skip matching filename.
5. **LLM syntax errors**: Unterminated strings common. Added `compile(code, "<name>", "exec")` validation — on failure, stub function.
6. **Missing imports**: LLM imports scattered in output. Now collected from FULL response before stripping: scan for `import ` / `from ` lines.
7. **Git conflict**: Auto-generated README (from some other AI agent) conflicted with working polyglot. Resolved by keeping working code.

## LLM quality

- ~50% of LLM-generated functions had syntax errors or were incomplete
- `run_run` was the only function that consistently produced working code
- `run_bootstrap` and `run_compile` often failed — stubs were used
- Qwen3.6-27B-FP8 is not reliable for multi-step code generation; validation + fallback is essential

## Files pushed

- `specs/tigorc/README.md` — polyglot compiler, ~440 lines
- `specs/tigorc/self.md` — test spec

## Key pattern for future

When LLM is behind a firewall (VM/box), use `scp + ssh exec` pattern rather than SSH tunnels which are unreliable from host.
