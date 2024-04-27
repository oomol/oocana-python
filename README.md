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

现在发布版本，有 github Action 触发，只需要根据不同的包，打 `@vocana/executor`和`@vocana/sdk-python` 前缀的 tag 即可。

可以参考以下命令，快速发布 tag

```shell
git tag @vocana/sdk-python@0.1.0
git push upstream @vocana/sdk-python@0.1.0
```

## TODO

- [ ] 支持协程穿插执行 block，需要让 stderr 和 stdout 的输出能够对应到正确的 block。
- [ ] 调整项目结构，让 executor 可以写多文件，sdk 导出一份 type hint，executor 不依赖 sdk。
- [ ] 追加日志。出现过发送的 execute 请求，结果没有向 vocana 发起 inputs 请求的情况。