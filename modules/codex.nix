{ ... }:
{
  imports = [
    ./dev.nix
  ];
  partitions.dev.module.perSystem =
    { pkgs
    , lib
    , ...
    }: {
      ml-ops.devcontainer.devenvShellModule = {
        packages = [
          pkgs.nixfmt
          pkgs.shellcheck
        ];
        enterShell = ''
          printf "#!%s\nexec %q exec %q %s" \
            "${lib.getExe pkgs.bash}" \
            "${lib.getExe pkgs.direnv}" \
            "$PWD" \
            '"$@"' \
            > .direnv/bin/vscode-codex-direnv-exec-pwd
          chmod +x .direnv/bin/vscode-codex-direnv-exec-pwd
        '';
      };
    };
}
