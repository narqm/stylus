#!/bin/zsh

VENV_PATH="$PWD/.venv"
STYLUS_PATH="$PWD/stylus"

fn_def="
  stylus() {
    source $VENV_PATH/bin/activate
    python $STYLUS_PATH \"\$@\"
    deactivate
}
"

# Check if the virtual env exists
if [ ! -d "$VENV_PATH" ]; then
  echo "Can't find virtual environment..."
  exit 1
fi

# Check if the func is in ~/.zshrc
if grep -q "stylus()" ~/.zshrc; then
  exit 1
else
  # append func to ~/.zshrc
  echo "$fn_def" >> ~/.zshrc
fi
