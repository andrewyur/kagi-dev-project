{
    description = "nix development shell for kagi full-stack project";
    inputs = {
        nixpkgs.url = "nixpkgs/nixos-unstable";
        flake-utils.url = "github:numtide/flake-utils";
    };

    outputs = {self, flake-utils, nixpkgs}: 
        flake-utils.lib.eachDefaultSystem (system:
        let
            pkgs = import nixpkgs { inherit system; };
        in {
            devShell = pkgs.mkShell {
                packages = with pkgs; [
                    python313
                    uv
                ];
                shellHook = ''
                '';
            };
        }
    );
}





# {
#     description = "nix flake for kagi full-stack project";
#     inputs = {
#         nixpkgs.url = "nixpkgs/nixos-unstable";
#         flake-utils.url = "github:numtide/flake-utils";

#         pyproject-nix = {
#             url = "github:pyproject-nix/pyproject.nix";
#             inputs.nixpkgs.follows = "nixpkgs";
#         };

#         uv2nix = {
#             url = "github:pyproject-nix/uv2nix";
#             inputs.pyproject-nix.follows = "pyproject-nix";
#             inputs.nixpkgs.follows = "nixpkgs";
#         };
#     };

#     outputs = {self, nixpkgs, flake-utils, uv2nix, pyproject-nix}:
#         flake-utils.lib.eachDefaultSystem (system:
#             let
#                 inherit (nixpkgs) lib;

#                 workspace = uv2nix.lib.workspace.loadWorkspace { workspaceRoot = ./.; };

#                 # nix overlay of python packages to nix packages
#                 overlay = workspace.mkPyprojectOverlay {
#                     sourcePreference = "wheel";
#                 };

#                 pkgs = import nixpkgs { inherit system; };

#                 python = pkgs.python313;

#                 # construct package set
#                 pythonSet =
#                     (pkgs.callPackage pyproject-nix.build.packages {
#                         inherit python;
#                     }).overrideScope
#                         (lib.composeExtensions overlay);
#             in 
#                 {

#                     # Package a virtual environment as our main application.
#                     packages."${system}".default = pythonSet.mkVirtualEnv "hello-world-env" workspace.deps.default;

#                     # dev environment
#                     devShell = pkgs.mkShell {
#                         packages = [
#                             python
#                             pkgs.sqlite
#                             pkgs.uv
#                         ];
#                         shellHook = ''
#                         '';
#                     };

#                 }
#         );
# }

# # if [ -f .env ]; then
# #     export $(cat .env | xargs)
# # fi
# # if [ ! -d ".venv" ]; then
# #     python -m venv .venv
# # fi
# # source .venv/bin/activate
# # pip install -r requirements.txt
# # python3 db/db_init.py
# # gunicorn -w 4 -b 0.0.0.0:8000 app:app