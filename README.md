# vocana-python-sdk

## 开发

本项目使用了 `pdm` 包管理工具进行开发

具体安装请参考 https://github.com/pdm-project/pdm

## 安装依赖

```
pdm install
```

## 构建项目

```
pdm build
```

## 测试项目

broker 准备

```shell
(cd example && pnpm install)
# 可以使用 vocana-sdk-node 中 packages/broker 的代码启动 broker
# 或者在安装 pdm 后，使用 Python 启动 broker
python broker/main.py
```

运行 vocana

```shell
node example/demo.js
```

## 发布项目

本项目包含`vocana-sdk-python`和`vocana-executor-python`两个子项目，具体的发布流程，参考[发布](./publish.md)文档。