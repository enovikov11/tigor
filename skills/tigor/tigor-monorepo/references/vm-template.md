# VM Template Generation

## vm.py — XSL-to-bash generator

`vm.py` is a Python template generator (not a runtime launcher). It reads a `vms` dict and outputs per-VM shell scripts (`hermes.sh`, etc.) that launch qemu + passt + virtiofsd.

### Why not Python runtime?

The user asked for Python first, then reverted to: Python generates bash templates, bash scripts run. This avoids subprocess complexity and gives a script that works standalone on bare metal.

### Architecture

```
vm.xsl (source of truth)
    ↓ knobs/values synced
vm.py (generator)
    ↓ outputs
hermes.sh (runtime launcher)
```

### vm.py dict keys (1:1 with vm.xsl `<vm>` attributes)

```python
vms = {
    "hermes": {
        "cpu": 64,
        "ram": 128,
        "kernel": "/ssd/vm/vm-r17-nvda-pods-vsock-BOOTX64.efi",
        "gpu": True,
        "vsock": True,
        "ui": True,
        "net_bus": "0x04",
        "disk": "/ssd/vm/hermes.qcow2",
        "mounts": [
            {"src": "/ssd/internet", "dst": "/ssd/internet", "readonly": True},
            {"src": "/hdd/internet/kiwix", "dst": "/hdd/internet/kiwix", "readonly": True},
            {"src": "/hdd/internet/wikipedia", "dst": "/hdd/internet/wikipedia", "readonly": True},
            {"src": "/ssd/vm/hermes", "dst": "/ssd/vm/hermes"},
            {"src": "/ssd/telegraf/hermes", "dst": "/ssd/telegraf/host"},
        ],
    },
}
```

### Key implementation detail

**NEVER use `str.format()` on strings containing `${VAR}`** — Python treats `{VAR}` as a replacement field and raises `KeyError`. Use `+` concatenation instead. The generator produces strings like:

```python
s += 'ip netns add "ns-${VM_NAME}"\n'    # safe, no .format()
s += '  -smp ' + str(c["cpu"]) + ' \\\n'  # safe concatenation
```

### Generated script structure

- `#!/usr/bin/env bash` + `set -Eeuo pipefail`
- `VM_NAME` variable + `cleanup()` function on EXIT/INT/TERM
- ip commands (netns, wireguard, routing) — direct, no functions
- passt background + socket wait loop
- virtiofsd per mount + socket wait loop each
- `exec qemu-system-x86_64` with all args on separate lines

### Adding new VMs

Add another key to the `vms` dict. Running `python3 vm.py` generates `{name}.sh` for each entry.
