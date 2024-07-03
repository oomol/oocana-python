#!/bin/bash
set -x

# pnpm 的 bin 是 pnpm 额外创建一个 shell，有那个文件通过 shell 调用当前文件。
# npm 的 bin 则是软链接到当前文件。
# 先使用 readlink 获取真实文件路径，然后获取文件所在目录。这样可以兼容 npm 和 pnpm。readlink 在大多数系统中都存在。
if command -v readlink >/dev/null 2>&1; then
  DIR=$(dirname "$(readlink -f "$0")")
else
  DIR=$(cd $(dirname "$0"); pwd -P)
fi

cd $DIR/..

python -u -m python_executor.executor "$@"