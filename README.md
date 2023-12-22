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

因为 github registry 并不支持 pypi 所以这里是发布到 npm 的 registry 再执行手动安装 whl 来进行发包和安装

```shell
pdm run publish_npm
```

## 发布 executor

```shell
pdm run publish_executor
```
