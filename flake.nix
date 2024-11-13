{
    description = "nix development shell for kagi full-stack project";
    inputs.nixpkgs.url = "nixpkgs/nixos-unstable";

    outputs = {self, nixpkgs}: let
        system = "aarch64-darwin"; # this should be an input
        pkgs = import nixpkgs { inherit system; };
    in {
        devShells."${system}".default = pkgs.mkShell {
            packages = with pkgs; [
                python313
                sqlite
            ];
            shellHook = ''
                if [ ! -d ".venv" ]; then
                    python -m venv .venv
                fi
                source .venv/bin/activate
                pip install -r requirements.txt
                clear
            '';
        };
    };
}
