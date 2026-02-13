{ inputs, ... }:
{
  imports = [
    inputs.flake-parts.flakeModules.partitions
  ];

  partitionedAttrs.checks = "dev";
  partitionedAttrs.packages = "dev";
  partitionedAttrs.devShells = "dev";
  partitions.dev = {
    extraInputsFlake = ../dev;
    extraInputs.devenv-root = inputs.devenv-root;
    module =
      { inputs
      , ...
      }: {
        imports = [
          inputs.nix-ml-ops.flakeModules.nixIde
          inputs.nix-ml-ops.flakeModules.nixLd
          inputs.nix-ml-ops.flakeModules.ldFallbackManylinux
          inputs.nix-ml-ops.flakeModules.devcontainerNix
        ];
      };
  };
}
