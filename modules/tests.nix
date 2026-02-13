{ ... }:
{
  imports = [
    ./dev.nix
    ./lib.nix
  ];
  partitions.dev.module =
    { inputs
    , config
    , ...
    }: {
      perSystem = { system, pkgs, ... }: {
        packages.update-tests-snapshot =
          let
            nixago = inputs.nix-ml-ops.inputs.nixago;

            stdlibDirectory = ../stdlib;

            stdlibMixin = config.flake.lib.compileDirectory {
              directory = stdlibDirectory;
              pathMapping = path:
                builtins.replaceStrings [ (toString stdlibDirectory) ] [ "stdlib" ] (toString path);
            };

            evaluation = (config.flake.lib.evaluate [
              stdlibMixin
              (config.flake.lib.compileDirectory rec {
                directory = ../tests;

                # Replace the hashed path with a relative path
                pathMapping = path:
                  builtins.replaceStrings [ (toString directory) ] [ "tests" ] (toString path);
              })
            ]);
            snapshot = evaluation: {
              ownMixinKeys = builtins.map (mixin: mixin.key) evaluation.ownMixins;
              allMixinKeys = builtins.map (mixin: mixin.key) evaluation.allMixins;
              ${ if evaluation.allPrimitives == [ ] then null else "allPrimitives"} =
                evaluation.allPrimitives;
              ${ if evaluation.allProperties == { } then null else "allPropertySnapshots"} =
                builtins.mapAttrs (propertyName: snapshot) evaluation.allProperties;
            };
          in
          (nixago.lib.${system}.make {
            data = snapshot evaluation;
            output = "tests/snapshot.json";
            hook.mode = "copy";
          }).install;
      };
    };
}
