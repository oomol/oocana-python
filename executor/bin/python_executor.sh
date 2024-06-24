#!/bin/bash
set -x

DIR=$(cd $(dirname "$0"); pwd -P)
# 这个脚本会被 nodejs 包管理工具放置在 node_modules/.bin 目录下。
# 为了降低对系统的依赖，手动根据 node_modules 文件结构 cd 回 Package 的目录，而不是使用 readlink 或者 stat 等系统调用。
# 因为没有 set -e，所以 cd 失败不会导致脚本退出，而是继续执行 python 命令。
cd $DIR/../@oomol/python-executor

python -m impl.executor "$@"