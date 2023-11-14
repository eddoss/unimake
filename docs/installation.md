# Installation
The easiest way to install `unimake` is to use `pip`. It will download and install latest stable 
release of the toolkit from official PyPi repositories. 
But if you need latest commit from development branch you can install it manually.
## From PyPi
It will provide latest stable release of the toolkit
```sh
pip install umk
```
## From sources
### Requirements
- [Python 3.10 (or higher)](https://www.python.org/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Make](https://www.gnu.org/software/make/manual/make.html)
### Build
To build a project you need install dependencies at first, and after you can run the build. 
```sh
make dependencies
make build
```
### Install
This receipt will install framework, `umk` and `unimake` binaries 
```sh
make install
```
### Completions
### Bash
```
# Add this to ~/.bashrc:
eval "$(_UMK_COMPLETE=bash_source umk)"
```
#### Zsh
```
# Add this to ~/.zshrc:
eval "$(_UMK_COMPLETE=zsh_source umk)"
```
#### Fish
```
# Add this to ~/.config/fish/completions/umk.fish:
_UMK_COMPLETE=fish_source umk | source
```