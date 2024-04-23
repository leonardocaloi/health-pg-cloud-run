#!/bin/bash

VENV_NAME="venv"

usage() {
  echo "Uso: $0 [-n|--name <nome_do_ambiente_virtual>]"
  exit 1
}

# Loop para processar argumentos
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -n) # Opção abreviada
      VENV_NAME="$2"
      shift
      ;;
    --name)
      VENV_NAME="$2"
      shift
      ;;
    *)
      usage
      ;;
  esac
  shift
done

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Debian/Ubuntu
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y python3 python3-venv python3-pip sshpass
    PYTHON_PATH=python3

elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    brew update && brew upgrade
    brew install python hudochenkov/sshpass/sshpass
    PYTHON_PATH=$(brew --prefix)/bin/python3

else
    echo "OS not supported."
    exit 1
fi

$PYTHON_PATH -m venv "$VENV_NAME"
source "$VENV_NAME/bin/activate"
pip install --upgrade pip
pip install -r app/requirements.txt
deactivate
sleep 5
source "$VENV_NAME/bin/activate"