# VM Infrastructure

## Network Topology

```
VPS (hermes user)        Bare metal host          VM (nixos user)
┌──────────────┐         ┌────────────────┐      ┌────────────────┐
│ eth0         │         │ eth0           │      │ enp0s5         │
│ 10.18.0.5/16 │         │ + WG + QEMU    │      │ 10.67.69.2/24  │
│              │────────▶│ wg0            │──────▶│ (via DHCP)     │
│ 178.128.241  │ SSH:22  │ 10.67.69.1/24  │passt  │                │
└──────────────┘         └────────────────┘      └────────────────┘
```

- **Host → VM network**: qemu passt backend, connected via vhostuser socket `/run/hermes-passt.sock` (r17+)
- **VM gets IP via DHCP from passt** — no static IP config needed in flake for modern versions
- **SSH port forwards**: host:2222 → guest:22 (defined in vm.xsl or passt config)
- **vsock**: independent of network config, CID auto on host
- **WG tunnel**: host wg0 at 10.67.69.1/24, VM at 10.67.69.2/24. Server WG config: `AllowedIPs = 0.0.0.0/0` (routes all VM traffic). VM WG config generated via `wg-genkeys.sh`.

## VM Access Points

| Method | Command | Notes |
|--------|---------|-------|
| SSH via host port forward | `ssh -J root@192.168.1.28 root@127.0.0.1 -p 2222` | Requires host SSH |
| SSH via vsock (from host) | `ssh -o ProxyCommand='vsock-sendto %h %p' nixos@3` | Independent of network |
| SSH via vsock (from laptop) | `ssh -o ProxyCommand='ssh root@192.168.1.28 vsock-sendto %h %p' nixos@3` | Jump through host |

## SSH Unreachable — Root Causes

Three distinct bugs that make VM SSH unreachable on TCP:

1. **`ListenAddress vsock:*:22`** (r14) replaces default `0.0.0.0:22` — sshd only binds to vsock. Fix: explicitly set both addresses.
2. **`startWhenNeeded = vm && vsock`** (r17+) — sshd is socket-activated, only starts on vsock connections. It never opens TCP port 22. Fix: remove `startWhenNeeded` entirely.
3. **Missing network params** (r14 only) — if `netInterface`, `staticIP`, `staticIPGateway` params were absent, VM had no IP. In r17+, DHCP from passt handles this automatically.

## VM storage

| Path in VM | Source | Type |
|-----------|--------|------|
| /home/nixos | /ssd/vm/hermes.qcow2 (500G ext4) | Persistent disk |
| /ssd/vm/hermes | virtiofs shared | Read-write, synced with host |
| /ssd/internet | virtiofs shared | Read-only |
| /hdd/internet/kiwix | virtiofs shared | Read-only |
| /hdd/internet/wikipedia | virtiofs shared | Read-only |
| /ssd/telegraf/host | virtiofs shared | Read-write |

## UKI deployment (requires host access — NEVER do this as AI)

```bash
nix build .#vm
mkdir /root/mnt
mount /dev/sde1 /root/mnt
cp /root/result/host-*-BOOTX64.efi /root/mnt/EFI/BOOT/BOOTX64.efi
sync && umount /root/mnt && reboot now
```

## vm.xsl evolution

- **r14**: `<interface type="user">` + `<backend type="passt"/>` with port forwards defined inline
- **r17+**: `<interface type="vhostuser">` with socket `/run/hermes-passt.sock` — passt runs externally, socket path configured in vm.sh on host

## Observed VM behavior (r18-rc1)

- Interface name: `enp0s5` (changed from `enp4s0` in r14)
- IP assigned via DHCP from passt: `10.67.69.2/24`
- SSH on vsock works (`sshd-session` process visible)
- SSH on TCP does NOT work (`ss -tnpl` shows no port 22 listener)
- Root cause: `startWhenNeeded = vm && vsock` in flake.nix

## VM Internet Connectivity

The VM reaches the internet through a two-hop path: WG tunnel to VPS, then NAT to eth0.

### Prerequisites on VPS (one-time, survives reboot)

1. **IP forwarding** (enabled by default): `sysctl net.ipv4.ip_forward=1`
2. **MASQUERADE** — required for outbound traffic from VM subnet:
   ```bash
   iptables -t nat -A POSTROUTING -s 10.67.69.0/24 -o eth0 -j MASQUERADE
   netfilter-persistent save  # persist across reboots
   ```
3. **UFW FORWARD rules** — VPS UFW defaults to `deny (routed)`. Without these, all forwarded packets are dropped:
   ```bash
   ufw route allow in on wg0 out on eth0
   ufw route allow in on eth0 out on wg0
   ```
   (UFW rules are persistent. Verify with `ufw status numbered` — look for `ALLOW FWD` lines.)

### DNS in VM

passt's built-in DHCP server assigns the host's local DNS resolver (`192.168.1.1` — the bare metal router) which is unreachable from the VM.

**Fix in `vm.sh`** — add `--dns-forward` to the passt command:
```bash
        --dns-forward 8.8.8.8 \
```
This maps DNS queries from the VM to a resolver that the VPS can reach.

### Troubleshooting VM internet

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ping 8.8.8.8` fails, curl hangs | No MASQUERADE or UFW blocks FORWARD | Add rules above |
| curl by IP works, DNS fails | resolv.conf points to `192.168.1.1` | `--dns-forward 8.8.8.8` in vm.sh |
| `kex_exchange_identification: Connection closed` on SSH | sshd not listening on TCP port | Pitfall 2 in skill (startWhenNeeded) |

### Verify connectivity

```bash
# From VPS
ssh -o StrictHostKeyChecking=no -p22 nixos@10.67.69.2 "curl -sI --connect-timeout 5 https://google.com"
```
