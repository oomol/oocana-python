# oocana-python

This project contains two Python packages: oocana and executor. oocana is a module used by Python blocks, while executor is a runtime for executing all Python Blocks. Both have been published to PyPI.

[![oocana](https://img.shields.io/pypi/v/oocana?label=oocana)](https://pypi.org/project/oocana/) [![python-executor](https://img.shields.io/pypi/v/oocana-python-executor?label=oocana-python-executor)](https://pypi.org/project/oocana-python-executor/)


## How to Use

## Installation

```shell
pip install oocana
pip install oocana-python-executor
```

* oocana

```python
from oocana import Context

def main(props, context: Context):
    return {
        "message": "Hello from Python blk_b"
    }
```


* executor

need to install `oocana-python-executor` package.


## Development

```shell
pdm install
```

## Test
oocana unit tests require an MQTT broker connection. You can start an MQTT broker externally. We recommend using mosquitto.

```shell
# Install mosquitto on macOS, for other systems please refer to the documentation
brew install mosquitto

# Start mosquitto, -d for background running, -p for port number
mosquitto -p 47688
```

Then you can run the tests.

```shell
# need run mqtt broker
pdm run test
```