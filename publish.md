# publish

## 版本号

oocana-sdk-python 版本号在`pyproject.toml`中定义。
oocana-executor-python 版本号在`executor/package.json`中定义。

## 发布项目

因为 github registry 并不支持 pypi 所以这里是发布到 npm 的 registry 再执行手动安装 whl 来进行发包和安装

```shell
# 发布 oocana-sdk-python
pdm run publish_oocana
# 发布 executor
pdm run publish_executor
```
