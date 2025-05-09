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

cp -r $(pwd)/oocana/dist /tmp/oocana
cp -r $(pwd)/executor/dist /tmp/executor

sudo ovmlayer cp --mode host2layer /tmp/oocana $EXECUTOR:/python-executor
sudo ovmlayer cp --mode host2layer /tmp/executor $EXECUTOR:/python-executor
sudo ovmlayer cp --mode host2layer $(pwd)/scripts/install-python.sh $EXECUTOR:/

sudo ovmlayer merge -l $EXECUTOR -m $mp
sudo ovmlayer run --all-devices --merged-point=$mp bash -c -i '/install-python.sh'
sudo ovmlayer run --all-devices --merged-point=$mp zsh -c -i 'pip install /python-executor/oocana/*.whl'
sudo ovmlayer run --all-devices --merged-point=$mp zsh -c -i 'pip install /python-executor/executor/*.whl'
sudo ovmlayer unmerge $mp
