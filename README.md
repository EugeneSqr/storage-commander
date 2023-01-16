## storage-commander
Unified way of managing files in various remote storages.

## setup
- clone the repository
- `pip install .`

## development setup
- clone the repository
- create venv and activate it
- install development dependencies `pip install -r requirements.txt`
- `pip install --editable .`

## bash completion
Copy the `.storcom-complete.bash` from the root of the cloned project repository to some location like `~/.config/storcom`, then source this file in bash.
```bash
. "$HOME/.config/storcom/.storcom-complete.bash"
```
To make this change permanent, add this line to `.bashrc`.
