#!/bin/bash
# set -x

# pnpm 对 bin 的处理：
#   pnpm 在 .bin 额外创建一个 shell，由那个 shell 调用本文件
# npm 对 bin 的处理：
#   在 bin 里直接创建一个到本文件的软链接

# 先尝试使用 readlink 获取真实文件路径，来兼容 npm 和 pnpm。
# readlink 在大多数系统中都存在。
if command -v readlink >/dev/null 2>&1; then
  DIR=$(dirname "$(readlink -f "$0")")
else
  DIR=$(cd $(dirname "$0"); pwd -P)
fi

cd $DIR/..

python -u -m python_executor.executor "$@"