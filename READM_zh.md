# oocana-python

该项目包含两个Python软件包：oocana和executor。oocana是供Python区块使用的模块，而executor是执行所有Python区块的运行时环境。两者都已发布到PyPI。

[![oocana](https://img.shields.io/pypi/v/oocana?label=oocana)](https://pypi.org/project/oocana/) [![python-executor](https://img.shields.io/pypi/v/oocana-python-executor?label=oocana-python-executor)](https://pypi.org/project/oocana-python-executor/)

## 如何使用

* oocana

```python
from oocana import Context

def main(props, context: Context):
    return {
        "message": "Hello from Python blk_b"
    }
```

* executor

需要安装 `oocana-python-executor` 软件包。

## 开发

```shell
pdm install
```

## 测试

oocana 单元测试需要 MQTT 代理连接。您可以在外部启动 MQTT 代理。我们建议使用 mosquitto。

```shell
# 在 macOS 上安装 mosquitto，其他系统请参考文档
brew install mosquitto

# 启动 mosquitto，-d 为后台运行，-p 为端口号
mosquitto -p 47688
```

然后您可以运行测试。

```shell
# oocana 相关的 cli 测试，需要启动 broker
pdm run test
```
