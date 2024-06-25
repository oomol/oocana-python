#!/bin/bash
set -x

DIR=$(cd $(dirname "$0"); pwd -P)
# 虽然复制到 bin 里面了，但是执行的时候，是resolve 到当前项目内再执行的。因此相对路径是不变的。
cd $DIR/..

python -m impl.executor "$@"