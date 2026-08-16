{
  description = "Stateless NixOS host and diskless UKI guest images";

  inputs = {
    # 2026-08-14 https://github.com/NixOS/nixpkgs/commits/nixos-26.05/
    nixpkgs.url = "github:NixOS/nixpkgs/02e08985a27c65ffd33d434eeb2e660a2e4dc84d";
  };

  outputs =
    { self, nixpkgs, ... }:
    let
      # For release candidates use r5-rc1 format
      revision = "r11";

      # Public password hash is a tradeoff between usability and security, underlying is high entropy
      yubiSshKey = "sk-ssh-ed25519@openssh.com AAAAGnNrLXNzaC1lZDI1NTE5QG9wZW5zc2guY29tAAAAIMltMQTMSIcxPbZLNCxkAT/MWRqJo1IFOfH95OoscQbCAAAABHNzaDo= enovikov11@novikov.local";
      hermesSshKey = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICIe5VqCNa+TeVMy/7ap/wEUwQV3yBUebCxyahARktVo root@agents-s-1vcpu-2gb-ams3";
      mainPassword = "$6$JsF575e4YV0MxwGU$aDy3BMHg/5lvWZoMvsAV0TL/BIcXMu3ps1DnOf3.o.hQ3IqT/sfCwKJHdMaaRy2exNAEUFxpxPbO966DE5cm./";

      lib = nixpkgs.lib;
      system = "x86_64-linux";

      gnomeModule =
        {
          scalingFactor,
          includeVMManager ? false,
        }:
        { lib, pkgs, ... }: {
          hardware.graphics.enable = true;

          services.xserver.enable = true;
          services.displayManager.gdm.enable = true;
          services.desktopManager.gnome.enable = true;

          environment.gnome.excludePackages = with pkgs; [
            gnome-backgrounds
            gnome-bluetooth
            gnome-color-manager
            gnome-tour
            gnome-user-docs
            gnome-menus
            orca
          ];

          hardware.bluetooth.enable = false;
          services.hardware.bolt.enable = false;
          i18n.inputMethod.enable = false;
          services.avahi.enable = false;
          services.colord.enable = false;
          services.dleyna.enable = false;
          services.geoclue2.enable = false;
          services.power-profiles-daemon.enable = false;
          services.orca.enable = false;
          services.upower.enable = lib.mkForce false;
          services.gnome = {
            core-apps.enable = false;
            evolution-data-server.enable = lib.mkForce false;
            gcr-ssh-agent.enable = false;
            gnome-browser-connector.enable = false;
            gnome-initial-setup.enable = false;
            gnome-keyring.enable = false;
            gnome-online-accounts.enable = false;
            gnome-remote-desktop.enable = false;
            gnome-user-share.enable = false;
            localsearch.enable = false;
            rygel.enable = false;
            tinysparql.enable = false;
          };

          services.pipewire = {
            enable = true;
            alsa.enable = true;
            pulse.enable = true;
          };

          programs.gnome-disks.enable = true;

          environment.systemPackages = with pkgs; [
            nautilus
            gnome-console
          ];

          xdg.mime.defaultApplications = {
            "inode/directory" = [ "org.gnome.Nautilus.desktop" ];
          };

          programs.dconf.profiles = {
            gdm.databases = [
              {
                settings = {
                  "org/gnome/desktop/interface".scaling-factor = lib.gvariant.mkUint32 scalingFactor;
                  "org/gnome/settings-daemon/plugins/power" = {
                    sleep-inactive-ac-type = "nothing";
                    sleep-inactive-battery-type = "nothing";
                  };
                };
              }
            ];

            user.databases = [
              {
                settings = {
                  "org/gnome/desktop/interface".scaling-factor = lib.gvariant.mkUint32 scalingFactor;
                  "org/gnome/desktop/session".idle-delay = lib.gvariant.mkUint32 0;
                  "org/gnome/settings-daemon/plugins/housekeeping".donation-reminder-enabled = false;
                  "org/gnome/settings-daemon/plugins/power" = {
                    sleep-inactive-ac-type = "nothing";
                    sleep-inactive-battery-type = "nothing";
                  };
                  "org/gnome/shell".favorite-apps = [
                    "org.gnome.Nautilus.desktop"
                    "org.gnome.Console.desktop"
                    "org.gnome.DiskUtility.desktop"
                  ]
                  ++ lib.optionals includeVMManager [ "virt-manager.desktop" ];
                };
              }
            ];
          };
        };

      nvidiaModule =
        { gnome }:
        {
          config,
          lib,
          pkgs,
          ...
        }:
        let
          nvidiaSmi = lib.getExe' config.hardware.nvidia.package "nvidia-smi";
        in
        {
          hardware.graphics.enable = true;
          services.xserver.videoDrivers = [ "nvidia" ];
          hardware.nvidia = {
            branch = "production";
            modesetting.enable = gnome;
            open = true;
            nvidiaSettings = gnome;
            nvidiaPersistenced = true;
          };

          systemd.services.nvidia-profile = {
            description = "Configure NVIDIA GPU ECC and power profile";
            wantedBy = [ "multi-user.target" ];
            after = [ "nvidia-persistenced.service" ];
            wants = [ "nvidia-persistenced.service" ];
            serviceConfig = {
              Type = "oneshot";
              RemainAfterExit = true;
              Restart = "on-failure";
              RestartSec = "2s";
            };
            script = ''
              current="$(${nvidiaSmi} --query-gpu=ecc.mode.current --format=csv,noheader 2>&1)" || {
                echo "NVIDIA ECC status unavailable: $current"
                current=
              }
              if [[ -n "$current" ]] &&
                 ${pkgs.gnugrep}/bin/grep -qv '^Enabled$' <<< "$current"; then
                ${nvidiaSmi} --ecc-config=1 ||
                  echo "NVIDIA ECC is not configurable on this GPU in its current mode"
              fi
              ${nvidiaSmi} -pm 1 &&
                ${nvidiaSmi} -pl 450 &&
                ${nvidiaSmi} --lock-gpu-clocks=300,2400
            '';
          };

        };

      containersModule = { pkgs, ... }: {
        virtualisation.podman = {
          enable = true;
          extraRuntimes = [ pkgs.gvisor ];
        };
        environment.systemPackages = with pkgs; [
          podman
          podman-compose
          gvisor
        ];
      };

      nvidiaContainerToolkitModule = { lib, pkgs, ... }: {
        hardware.nvidia-container-toolkit.enable = true;

        environment.etc."nvidia-container-runtime/config.toml".text = ''
          [nvidia-container-runtime-hook]
          path = "${pkgs.nvidia-container-toolkit.tools}/bin/nvidia-container-runtime-hook"

          [nvidia-ctk]
          path = "${pkgs.nvidia-container-toolkit}/bin/nvidia-ctk"

          [features]
          disable-cuda-compat-lib-hook = true
        '';
      };

      stateless =
        {
          vm ? false,
          nvidia ? false,
          containers ? false,
          gnome ? false,
          scalingFactor ? 1,
          firefox ? false,
          vscodium ? false,
          sudo ? false,
          password ? "!",
          authorizedSshKeys ? [ yubiSshKey ],
          netInterface ? "enp4s0",
          staticIP ? null,
          staticIPGateway ? null,
        }:
        let
          hostNvidia = (!vm) && nvidia;
          rtxPassthrough = (!vm) && (!nvidia);
          vfioPciIds =
            # Bind the unused GPU's complete IOMMU group before display drivers probe.
            lib.optionals hostNvidia [
              # 01:00.0 GT 710 and 01:00.1 HDMI audio.
              "10de:128b"
              "10de:0e0f"
            ]
            ++ lib.optionals rtxPassthrough [
              # 41:00.0 RTX PRO 6000 and 41:00.1 HDMI audio.
              "10de:2bb1"
              "10de:22e8"
            ];
          imageName =
            (if vm then "vm-" else "host-")
            + revision
            + lib.optionalString nvidia "-nvda"
            + lib.optionalString containers "-pods"
            + lib.optionalString gnome "-gui"
            + lib.optionalString firefox "-ff"
            + lib.optionalString vscodium "-vs"
            + lib.optionalString sudo "-su";
          ukiName = "${imageName}-BOOTX64";
        in
        lib.nixosSystem {
          inherit system;

          modules = [
            (
              {
                config,
                lib,
                pkgs,
                modulesPath,
                ...
              }:
              {
                imports = [
                  (modulesPath + "/installer/netboot/netboot.nix")
                  (modulesPath + (if vm then "/profiles/qemu-guest.nix" else "/profiles/minimal.nix"))
                ];

                time.timeZone = "Europe/Belgrade";
                i18n.defaultLocale = "en_US.UTF-8";

                nixpkgs.config.allowUnfreePredicate = pkg: lib.hasPrefix "nvidia-" (lib.getName pkg);
                nix.settings = {
                  experimental-features = [
                    "nix-command"
                    "flakes"
                  ];
                  max-jobs = 4;
                  cores = 32;
                };

                networking = {
                  hostName = imageName;
                  hostId = lib.mkIf (!vm) "06e694f9";
                  firewall.enable = false;
                  nftables.enable = true;
                  networkmanager.enable = true;
                  interfaces.${netInterface} = {
                    useDHCP = lib.mkIf staticIP false;
                    ipv4.addresses = lib.mkIf staticIP [ staticIP ];
                  };
                  routes = lib.mkIf staticIPGateway [
                    {
                      destination = staticIPGateway;
                      via = staticIPGateway;
                      interface = netInterface;
                    }
                  ];
                };

                services.openssh = {
                  enable = true;
                  generateHostKeys = true;
                  openFirewall = true;
                  settings = {
                    AuthenticationMethods = "publickey";
                    PasswordAuthentication = false;
                    KbdInteractiveAuthentication = false;
                    PermitEmptyPasswords = false;
                    X11Forwarding = false;
                    PermitRootLogin = "prohibit-password";
                    AllowUsers = [
                      "root"
                      "nixos"
                    ];
                  };
                };

                security.sudo = {
                  enable = sudo;
                }
                // lib.optionalAttrs sudo { wheelNeedsPassword = false; };

                users.mutableUsers = false;
                users.users = {
                  root = {
                    hashedPassword = password;
                    openssh.authorizedKeys.keys = authorizedSshKeys;
                  };

                  nixos = {
                    isNormalUser = true;
                    hashedPassword = password;
                    extraGroups =
                      lib.optionals sudo [ "wheel" ]
                      ++ lib.optionals (!vm) [
                        "kvm"
                        "libvirtd"
                      ]
                      ++ lib.optionals (gnome || nvidia) [
                        "video"
                        "render"
                      ];
                    openssh.authorizedKeys.keys = authorizedSshKeys;
                  };
                };
                users.groups.kvm.members = lib.optionals (!vm) [ "qemu-libvirtd" ];

                boot = {
                  supportedFilesystems = lib.optionals (!vm) [ "zfs" ];

                  initrd.kernelModules =
                    lib.optionals (vfioPciIds != [ ]) [
                      "vfio_pci"
                      "vfio"
                      "vfio_iommu_type1"
                    ]
                    # NVIDIA GeForce GT 710
                    ++ lib.optionals (gnome && !nvidia) [ "nouveau" ];
                  kernelModules = lib.optionals vm [ "virtiofs" ] ++ lib.optionals (!vm) [ "kvm-amd" ];
                  kernelParams = [
                    "nohibernate"
                    "modprobe.blacklist=ast"
                    "transparent_hugepage=madvise"
                  ]
                  ++ lib.optionals (!vm) [
                    "kvm_amd.sev=1"
                    "kvm_amd.sev_es=1"
                    "amd_iommu=on"
                    "iommu=pt"
                    "iommu.strict=1"
                  ]
                  ++ lib.optional (vfioPciIds != [ ]) "vfio-pci.ids=${lib.concatStringsSep "," vfioPciIds}";
                  blacklistedKernelModules =
                    [ "ast" ]
                    # NVIDIA's open driver supports the RTX PRO, not the GT 710.
                    ++ lib.optionals hostNvidia [ "nouveau" ];
                  uki = {
                    name = ukiName;
                    version = null;
                    settings.UKI.Initrd = lib.mkForce "${config.system.build.netbootRamdisk}/initrd";
                  };
                  zfs.forceImportRoot = lib.mkIf (!vm) false;
                };

                services.udev.extraRules = lib.optionalString (!vm) ''
                  SUBSYSTEM=="misc", KERNEL=="sev", GROUP="kvm", MODE="0660"
                '';
                services.xserver.videoDrivers = lib.mkIf (gnome && !nvidia) [ "nouveau" ];

                services.qemuGuest.enable = vm;
                services.spice-vdagentd.enable = vm && gnome;
                systemd.services.mount-virtiofs-shares = lib.mkIf vm {
                  description = "Mount virtiofs path shares";
                  wantedBy = [ "multi-user.target" ];
                  after = [ "systemd-modules-load.service" ];
                  serviceConfig.Type = "oneshot";
                  path = with pkgs; [
                    coreutils
                    util-linux
                  ];
                  script = ''
                    shopt -s nullglob
                    for tagFile in /sys/fs/virtiofs/*/tag; do
                      IFS= read -r path < "$tagFile"
                      mkdir -p -- "$path"
                      mount -t virtiofs -- "$path" "$path"
                    done
                  '';
                };
                services.displayManager.autoLogin = lib.mkIf (vm && gnome) {
                  enable = true;
                  user = "nixos";
                };

                programs.firefox.enable = firefox;
                programs.virt-manager.enable = (!vm);

                systemd.services.autostart = lib.mkIf vm {
                  description = "Run /root/data/autostart.sh";
                  wantedBy = [ "multi-user.target" ];
                  after = [ "mount-virtiofs-shares.service" ];
                  requires = [ "mount-virtiofs-shares.service" ];
                  serviceConfig = {
                    Type = "oneshot";
                    RemainAfterExit = true;
                    ExecStart = [ "/root/data/autostart.sh" ];
                  };
                };

                virtualisation.libvirtd = lib.mkIf (!vm) {
                  enable = true;
                  onBoot = "ignore";
                  onShutdown = "shutdown";
                  firewallBackend = "nftables";
                  qemu = {
                    package = pkgs.qemu_kvm;

                    runAsRoot = false;

                    verbatimConfig = ''
                      namespaces = []
                      seccomp_sandbox = 1
                      spice_auto_unix_socket = 1
                      vnc_auto_unix_socket = 1
                    '';

                    vhostUserPackages = [ pkgs.virtiofsd ];
                  };
                };

                systemd.services.virt-secret-init-encryption = lib.mkIf (!vm) {
                  serviceConfig = {
                    StateDirectory = "libvirt/secrets";
                    StateDirectoryMode = "0700";
                    ExecStart = lib.mkForce [
                      ""
                      (pkgs.writeShellScript "virt-secret-init-encryption" ''
                        umask 0077
                        ${pkgs.coreutils}/bin/chmod 0700 /var/lib/libvirt/secrets
                        ${pkgs.coreutils}/bin/dd if=/dev/random status=none bs=32 count=1 | \
                          ${pkgs.systemd}/bin/systemd-creds encrypt --with-key=tpm2-absent \
                            --name=secrets-encryption-key \
                            - /var/lib/libvirt/secrets/secrets-encryption-key
                      '')
                    ];
                  };
                };

                systemd.tmpfiles.rules = [
                  "w /sys/kernel/mm/transparent_hugepage/defrag - - - - defer"
                ];
                systemd.targets.sleep.enable = false;
                systemd.targets.suspend.enable = false;
                systemd.targets.hibernate.enable = false;
                systemd.targets.hybrid-sleep.enable = false;

                environment.etc."nixos/flake.nix".source = ./flake.nix;
                environment.systemPackages =
                  (with pkgs; [
                    curl
                    git
                    htop
                    python3
                    tmux
                    vim
                    tree
                    wireguard-tools
                    jq
                    pciutils
                    usbutils
                    dmidecode
                    ethtool
                    smartmontools
                    nvme-cli
                    lm_sensors
                    hdparm
                    ipmitool
                    efibootmgr
                    libxslt
                  ])
                  ++ lib.optionals vscodium (with pkgs; [ vscodium ])
                  ++ lib.optionals (!vm) (with pkgs; [ zfs ])
                  ++ lib.optionals (!vm) (
                    with pkgs;
                    [
                      qemu_kvm
                      libvirt
                      openssl
                      virt-manager
                      passt
                      virtiofsd
                    ]
                  );
                environment.sessionVariables = lib.optionalAttrs vscodium { NIXOS_OZONE_WL = "1"; };
                environment.shellAliases = lib.optionalAttrs (!vm) {
                  mnt = "zpool import -a && zfs load-key -a && zfs mount -a";
                };

                system.stateVersion = "26.05";
              }
            )
          ]
          ++ lib.optional gnome (gnomeModule {
            inherit scalingFactor;
            includeVMManager = (!vm);
          })
          ++ lib.optional nvidia (nvidiaModule {
            inherit gnome;
          })
          ++ lib.optional containers containersModule
          ++ lib.optional (containers && nvidia) nvidiaContainerToolkitModule;
        };
    in
    {
      nixosConfigurations = {
        host = stateless {
          containers = true;
          gnome = true;
          scalingFactor = 2;
          sudo = true;
          password = mainPassword;
        };
        vm = stateless {
          vm = true;
          nvidia = true;
          containers = true;
          sudo = true;
          password = "";
          authorizedSshKeys = [ yubiSshKey hermesSshKey ];
          netInterface = "enp4s0";
          staticIP = "10.67.69.2/24";
          staticIPGateway = "10.67.69.1";
        };
      };

      packages.${system} = {
        host = self.nixosConfigurations.host.config.system.build.uki;
        vm = self.nixosConfigurations.vm.config.system.build.uki;
      };
    };
}
