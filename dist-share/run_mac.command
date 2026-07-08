#!/bin/zsh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

if [ -x "venv/bin/python3" ]; then
  "venv/bin/python3" main.py
elif [ -x "venv/bin/python" ]; then
  "venv/bin/python" main.py
else
  echo "Environment belum siap."
  echo "Jalankan setup_mac.command dulu untuk membuat venv dan install dependency."
fi

read "?Tekan Enter untuk menutup jendela..."
