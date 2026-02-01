{ ... }:
{
  imports = [
    ./dev.nix
  ];
  partitions.dev.module.perSystem = { pkgs, ... }: {
    ml-ops.devcontainer.devenvShellModule = {
      languages = {
        texlive = {
          enable = true;
          packages = [
            "scheme-small"
            "cjk"
            "xpinyin"
            "geometry"
            "latexmk"
            "pdftex"
            "latex"
            "mathtools"
            "listings"
            "xcolor"
          ];
        };
      };
    };
  };
}
