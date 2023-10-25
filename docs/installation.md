# Installation
## Requirements
- [Python](https://www.python.org/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Make](https://www.gnu.org/software/make/manual/make.html)
## Build
```sh
make project/env/up
make project/env/dependencies
make package/build
make cli/build
```
## Install
This receipt installs `./dist/umk` to `~/.local/bin/umk` 
```sh
make cli/install
``` 
## Completions
### Bash
```
# Add this to ~/.bashrc:
eval "$(_UMK_COMPLETE=bash_source umk)"
```
### Zsh
```
# Add this to ~/.zshrc:
eval "$(_UMK_COMPLETE=zsh_source umk)"
```
### Fish
```
# Add this to ~/.config/fish/completions/umk.fish:
_UMK_COMPLETE=fish_source umk | source
```