# oocana-python

本项目有 oocana 和 executor 两个项目，分别为给 Python block 用的 oocana sdk 和用来运行所有 block 的 python-executor。

目前都通过 npm 包发布。在 install 后安装到全局环境。

## 开发准备

本项目使用`pdm`进行环境管理，安装参考[官方文档](https://github.com/pdm-project/pdm)

```shell
pdm install
```

oocana unittest 需要 mqtt broker 连接。可以在外部启动一个 mqtt broker，这里推荐使用[mosquitto](https://mosquitto.org/download/)

```shell
# macos 安装 mosquitto，其他系统请参考链接文档
brew install mosquitto

# 启动 mosquitto， -d 为后台运行，-p 为端口号
mosquitto -p 47688
```

### 发布包

本项目为 monorepo 结构，通过`release-please`在 github Action 上进行生成 changelog，版本更新，打 tag 等逻辑。版本根据 git commit message 进行判断。

发包由 github action 通过 tag 事件触发。


## 调试项目

如果需要断点调试，参考 [debug](./docs/debug.md) 文档。

如果只是想运行本地 executor，可以在对应的 shell 配置文件（`zsh`为`~/.zshrc`，bash 为`~/.bashrc`）中添加`PATH`路径。

```shell
# 替换 <PROJECT_ROOT> 为项目根目录路径
export PATH="<PROJECT_ROOT>/executor/bin:$PATH"
```

或者直接执行以下命令:

```shell
echo "export PATH=\"$(pwd)/executor/bin:\$PATH\"" >> ~/.zshrc
source ~/.zshrc
```

## 测试

### 单元测试

```shell
# oocana 相关的 cli 测试，需要启动 broker
pdm run test
```

## TODO

- [x] 导出一份 type hint
- [x] 增加 mqtt broker 启动，以支持在 action 中开启 cli 启动单测
- [ ] 需要让多进程穿插运行 block 时，将对应 stderr 和 stdout 的输出能够对应到正确的 block。
- [x] session 结束时，清理 sys.modules 导入的 modules。
- [x] 支持协程/多进程穿插执行 block
- [x] 让 executor 可以编写多文件，目前由于限制，只能写单文件。
- [x] 处理`DeprecationWarning: There is no current event loop`警告。
- [x] 追加日志。出现过发送的 execute 请求，结果没有向 oocana 发起 inputs 请求的情况。
- [x] 尝试更改项目结构，让 executor 和 sdk 的版本号，有独立的存储关系。