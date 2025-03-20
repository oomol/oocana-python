#!/usr/bin/env bash
set -xeuo pipefail

DIR=$(cd $(dirname "$0"); pwd -P)
cd $DIR/..

echo "current directory: $(pwd)"

mp=merge-$(date -u '+%s')
EXECUTOR=python_executor

# pdm is required to build the wheel
pdm build_all

sudo ovmlayer delete $EXECUTOR
sudo ovmlayer create $EXECUTOR

echo "current directory: $(pwd)"

sudo ovmlayer cp-layer $(pwd)/oocana/dist $EXECUTOR:/python-executor/oocana
sudo ovmlayer cp-layer $(pwd)/executor/dist $EXECUTOR:/python-executor/executor
sudo ovmlayer cp-layer $(pwd)/scripts/install-python.sh $EXECUTOR:/install-python.sh

sudo ovmlayer merge $EXECUTOR : $mp
sudo ovmlayer run --merged-point=$mp -- bash -c -i '/install-python.sh'
sudo ovmlayer run --merged-point=$mp -- zsh -c -i 'pip install /python-executor/oocana/*.whl'
sudo ovmlayer run --merged-point=$mp -- zsh -c -i 'pip install /python-executor/executor/*.whl'
sudo ovmlayer unmerge $mp
