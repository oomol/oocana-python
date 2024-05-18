# debug

executor 接收 oocana 发给 mqtt broker 信息后，才会执行具体任务。因此整体调试需要准备好以下内容

1. 激活 Python 虚拟环境
1. 启动 mqtt broker
1. 编写好的 flow.oo.yaml 文件以及 blocks

## mqtt broker

可以使用 `根目录文件夹`下的 broker/main.py 启动一个 mqtt broker，也可以使用 [oocana-node](https://github.com/oomol/oocana-sdk-node) 中的 broker，后者的日志更详细。  
broker 端口为 47688。

## oocana 以及对应的 flow.oo.yaml

flow.oo.yaml 可以在根目录文件夹下的 example 文件夹找到。

oocana 可以使用 [oocana-rust](https://github.com/oomol/oocana-rust) 项目里面的 oocana 进行临时编译运行。也可以使用

## 进行调试

按照以下顺序执行：

1. 启动 mqtt broker
2. 启动 executor
3. 调用 oocana 读取 flow.oo.yaml 文件内容，发起运行请求（环境准备需要查看根目录下[oocana](../example/README.md) 文件夹内容）。

```shell
# 在根目录运行以下命令，每个命令需要一个 terminal 窗口
# 1. 启动 mqtt broker
python broker/main.py

# 2. 启动 executor
python executor/bin.py

# 3. 调用 oocana 读取 flow.oo.yaml 文件内容，发起运行请求
node example/demo.js
```
