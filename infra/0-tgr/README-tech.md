# tgr Infrastructure Notes

This directory is the production-facing tgr host area. Current deployed service
config still lives in `docker-compose.yml` and `caddy/Caddyfile`; the NixOS image
pipeline below is a planned direction, not deployed state until configuration
files say so.

## Planned NixOS + OCI Image Model

Goal: one flake should describe the host, its private source inputs, the OCI
images to build, and the containers to run.

Expected shape:

- `flake.lock` pins `nixpkgs` and any private source repositories.
- Private repositories are fetched as Nix inputs by exact commit, not by moving
  branch names alone.
- App packages and Python dependencies are built by Nix.
- OCI images are produced with `pkgs.dockerTools.buildImage` or
  `pkgs.dockerTools.buildLayeredImage`.
- NixOS starts the resulting images through `virtualisation.oci-containers`
  with the Podman backend.

Build/runtime flow:

1. Nix resolves pinned flake inputs.
2. Nix builds app/package derivations.
3. Nix builds OCI image tarballs.
4. NixOS activation loads image files into Podman.
5. systemd starts the configured containers at boot.

This avoids a registry requirement for host-local images: the NixOS container
definition can use `imageFile = <dockerTools image derivation>`.

## Private Repository Inputs

GitHub is not required. A private source can be a generic Git flake input, for
example `git+ssh://...`, `git+https://...`, or `git+file:...`.

Use pinned commits:

```nix
inputs.private-src = {
  url = "git+ssh://git@host/repo.git?rev=<commit>";
  flake = false;
};
```

It is also fine to name the branch for readability while still pinning the exact
commit:

```nix
inputs.private.url = "git+ssh://git@host/repo.git?ref=main&rev=<commit>";
```

Avoid relying on mutable branches as the only selector. `flake.lock` makes later
builds repeatable, but explicit commits make intent obvious and reviewable.

Credentials can be provided to the evaluator/Nix daemon, but they must be:

- read-only
- scoped to the minimum repo or path possible
- stored outside Git
- kept out of derivation outputs and public binary caches

Example shape for hosted Git credentials:

```nix
{
  nix.settings.access-tokens = [
    "github.com=ghp_xxx"
    "gitlab.com=glpat_xxx"
  ];
}
```

This is only the config shape. Do not commit real personal tokens to the repo;
prefer a root-only secret file or secret-management module that feeds Nix config
on the host.

Never put secrets themselves in private Git inputs. Runtime secrets belong in
host-managed secret files or a dedicated secret-management mechanism.

## Reproducibility Boundary

Private input fetching does not violate the normal "no internet during build"
model by itself: source fetching happens before or around evaluation/store
fetching, while derivation builders should remain network-free.

Reproducibility requires:

- pinned flake inputs
- committed `flake.lock`
- Nix-packaged Python/application dependencies, or fixed-output hashed sources
- no `pip install`, `apt-get`, `curl`, or similar network fetches during image
  construction
- external runtime state, such as disks, databases, secrets, DNS, and network,
  handled separately

If a private input contributes source or artifacts to a build, do not push the
resulting store paths to a public binary cache unless that content is safe to
publish.

## Dockerfiles vs dockerTools

Prefer Nix-native image construction with `dockerTools` instead of treating Nix
as a wrapper around `docker build`.

Good direction:

- package the application with Nix
- use `python3.withPackages`, `buildPythonPackage`, `poetry2nix`, `uv2nix`, or
  equivalent pinned packaging for Python dependencies
- assemble the runtime filesystem with `buildLayeredImage`
- run the image with Podman

Risky direction:

- invoking `podman build` or `docker build` inside a Nix derivation
- Dockerfiles that run package managers or network fetches during build
- depending on Docker daemon state

Podman is still the preferred runtime/import layer on NixOS:

```nix
{
  virtualisation.podman.enable = true;
  virtualisation.oci-containers.backend = "podman";
}
```

## Minimal Container Pattern

Small `buildImage` smoke-test style example:

```nix
pkgs.dockerTools.buildImage {
  name = "my-image";
  tag = "latest";

  copyToRoot = pkgs.buildEnv {
    name = "root";
    paths = [ pkgs.curl pkgs.cacert ];
  };

  config = {
    Cmd = [ "${pkgs.curl}/bin/curl" "--version" ];
  };
}
```

Example shape for a NixOS-managed image:

```nix
let
  myImage = pkgs.dockerTools.buildLayeredImage {
    name = "my-app";
    tag = "latest";
    contents = [
      pkgs.cacert
      (pkgs.python3.withPackages (ps: [
        ps.requests
      ]))
      myApp
    ];
    config = {
      Cmd = [ "${myApp}/bin/my-app" ];
      Env = [
        "SSL_CERT_FILE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
      ];
    };
  };
in {
  virtualisation.oci-containers.containers.my-app = {
    image = "my-app:latest";
    imageFile = myImage;
    ports = [ "8080:8080" ];
  };
}
```

## Security Reminders

- Do not mount Docker or Podman sockets into services.
- Keep `no-new-privileges` unless there is a specific, understood reason not to.
- Preserve `internal: true` networks for services that should not have direct
  internet access.
- Caddy should join an existing internal service network rather than creating a
  new non-internal bridge for isolated services.
- Host-mounted secret files must be outside the repo and readable only by the
  intended service/runtime user.
