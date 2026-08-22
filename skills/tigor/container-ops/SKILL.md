---
name: container-ops
description: Container image management — pull, save, transfer, load, inspect, and clean up images on podman.
---
# Container Operations

Pull, build, save, transfer, load, inspect, and remove container images. Runtime is **podman** on the host; `docker` CLI is pre-installed on the Hermes container and bridges to the podman socket.

## Architecture (post-migration, 2026-08)

Hermes Agent now runs **inside a rootless Podman container on the VM** (Debian 13 trixie). Neighboring containers on the same host:

| Container | Service | DNS name | Port |
|-----------|---------|----------|------|
| `vllm` | Qwen3.6-27B-FP8 (GPU) | `vllm` | 8000 |
| `forgejo` | Git server | `forgejo` | 3000 |
| `hermes` | Hermes Agent gateway | — | — |

All reachable via **container DNS** (e.g. `http://vllm:8000/v1`), not IP addresses.

Hermes container:
- Runs as `hermes:hermes` user (uid/gid 10000, no root, no --privileged, no sudo)
- Podman socket mounted: `/run/user/1000/podman/podman.sock` (owned `root:root`, mode `660`)
- Hermes home: `/home/nixos/.hermes` mounted to `/opt/data`
- Terminal backend: `local` (commands run inside the container)

### Container management access

To list/manage host containers, use `docker` with `DOCKER_HOST` already set in the environment:

```bash
docker ps
# or explicitly:
DOCKER_HOST=unix:///run/user/1000/podman/podman.sock docker ps
```

**However**, the socket is owned `root:root` with mode `660`, so `hermes` (uid 10000) gets `permission denied`. To fix (run on host as root):

```bash
chmod 666 /run/user/1000/podman/podman.sock
# OR
usermod -aG root hermes
```

## Triggers

- Pulling or pushing container images
- Transferring images between hosts
- Inspecting or cleaning container images
- Running containers on VM
- "No internet" / air-gapped container setup
- Managing services from inside Hermes container

## Quick reference

| Task | Command |
|------|---------|
| Pull image | `podman pull docker.io/library/<name>:<tag>` |
| Save to tar | `podman save -o /tmp/<name>.tar docker.io/library/<name>:<tag>` |
| Load from tar | `podman load -i /tmp/<name>.tar` |
| List images | `podman images` |
| Run and discard | `podman run --rm <image> <command>` |
| Remove image | `podman rmi <image>` |
| List containers | `docker ps` (via DOCKER_HOST env) |
| Stop container | `docker stop <name>` |
| Exec in container | `docker exec <name> <cmd>` |

## Transfer image to air-gapped VM

VM has no outbound internet. Pull on VPS, transfer via scp:

```bash
# On VPS
podman save -o /tmp/<image>.tar docker.io/library/<name>:<tag>
scp /tmp/<image>.tar nixos@10.67.69.2:/tmp/<image>.tar

# Via ssh
ssh nixos@10.67.69.2 "podman load -i /tmp/<image>.tar && podman images <name>"

# Cleanup
rm /tmp/<image>.tar && ssh nixos@10.67.69.2 "rm /tmp/<image>.tar"
```

## Pitfalls

### docker CLI exists, podman binary does not

`docker` IS installed at `/usr/bin/docker`. `podman` binary is NOT installed. Use `docker` with `DOCKER_HOST` for container operations. `podman` commands (pull/save/load) only work on the host, not inside the Hermes container.

### Podman socket permission denied

The socket at `/run/user/1000/podman/podman.sock` is owned `root:root` with mode `660`. Hermes runs as uid 10000 (`hermes:hermes`) and gets `permission denied` when connecting. Fix on host (as nixos): `chmod 666 /run/user/1000/podman/podman.sock`. The socket is auth-gated at the protocol level, so 666 is safe for this use case.

### Cannot use `user: "1000:1000"` to access the podman socket

Setting `user: "1000:1000"` in docker-compose.yml does NOT give access to the podman socket and BREAKS Hermes. Reason: rootless Podman maps container uid 10000 → host uid 109999, so `.hermes` files are owned by host uid 109999. Container uid 1000 maps to host uid 109999 + offset, which cannot write to those files.

### `--privileged` does not work under rootless Podman

`docker run --privileged` returns `500 unable to upgrade to tcp` under rootless Podman. Rootless Podman cannot grant full privileged mode inside a user namespace. GPU management operations (e.g., `nvidia-smi -pl` power limit) that require privileged access will fail from inside the Hermes container.

### Never leave temp tars

Always clean up `/tmp/*.tar` on both VPS and VM after transfer. They are 8-500MB.

### podman save includes all layers

A large multi-stage build can produce a tar that is 10x the runtime image. For large images, consider `podman push` to a local registry instead.

### Hermes is non-root in container

Hermes runs as `hermes:hermes` (uid 10000) inside the container. No sudo, no root. To manage host containers, podman socket must be accessible. Without it, `docker` commands fail with permission denied.

### No SSH keys on VM

The Hermes container has no SSH keys configured. Cannot reach host (10.67.69.1) via SSH — it requires publickey auth. Generate a key with `ssh-keygen` and authorize it on the host if SSH access is needed.

### DOCKER_HOST already set

`DOCKER_HOST=unix:///run/user/1000/podman/podman.sock` is pre-set in the environment. You can just use `docker ps` without setting it. Same for `PODMAN_REMOTE=1`.

## See Also

- `infrastructure/dockerize-python-service` — building Python service images
- `infrastructure/tigor-monorepo` — git workflow for the tigor repos (bare repo permissions)
