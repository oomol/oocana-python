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

需要三个进程

1. 开启 broker
```shell
cd test
pnpm broker
```

2. 开启 executor
```shell
pdm run executor
```

3. 启动测试
```shell
cd test
pnpm start
```