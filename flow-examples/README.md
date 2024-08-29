# oocana

本文件夹的内容，是为了在开发当前项目内容时，可以脱离其他项目源码（oocana-rust）即可运行调试 executor 和 src 源码。准备好环境后，查看 [debug](../docs/debug.md) 文档。

> 代码中的事件，可能存在一些更新不及时的问题，仅做源码调试运行用。

## 准备

根据 [oocana-node](https://github.com/oomol/oocana-node) 项目的 README.md，配置好 npmrc 内容。

安装依赖

```shell
cd test
# brew install pnpm 或者用其他 pnpm 安装方式 pnpm
pnpm install
# 因为这里只是调试用，所以默认永远安装最新的 oocana cli，忽略 lock 文件
```

## 启动测试

```shell
# macos 上安装 mosquitto 执行 brew install
# 开启 broker 服务
mosquitto -p 47688 -v
```

```shell
cd test
pnpm start
```

## TODO

- [ ] @oomol/oocana 遇到 flow.oo.yaml 格式有问题时，会直接发出 SessionFinished 事件后直接退出。缺少退出码提示整个文件是否正常运行，导致测试无法覆盖这种情况。
- [ ] 使用 renovate 更新当前项目的 @oomol/oocana 依赖，而不是直接 git ignore 掉 lock 文件。