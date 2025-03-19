#!/usr/bin/env bash
set -xeuo pipefail

apt update && apt install -y curl
curl -LsSf https://astral.sh/uv/install.sh | sh

/root/.local/bin/uv python install 3.10
PY_PYTHON=$(/root/.local/bin/uv python find 3.10)
PY_BIN=$(dirname $PY_PYTHON)
echo "export PATH=/root/.local/bin:$PY_BIN:$PATH" >> ~/.zshrc

# make uv python the default python and support use it directly in shell
rm "$($PY_PYTHON -c "import site, sysconfig; print(sysconfig.get_path('stdlib'));")/EXTERNALLY-MANAGED"