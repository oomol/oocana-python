# vocana-python-sdk

## 开发

本项目使用了 `pdm` 包管理工具进行开发

具体使用请参考 https://github.com/pdm-project/pdm

## 安装依赖

```
pdm install
```

## 构建项目

```
pdm build
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
