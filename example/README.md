# vocana

本文件夹的内容，是为了在开发当前项目内容时，可以脱离其他项目源码（Vocana-rust）即可运行调试 executor 和 src 源码。准备好环境后，查看 [debug](../docs/debug.md) 文档。

> 代码中的事件，可能存在一些更新不及时的问题，仅做源码调试运行用。

## 准备

根据 [vocana-sdk-node](https://github.com/oomol/vocana-sdk-node) 项目的 README.md，配置好 npmrc 内容。

安装依赖

```shell
# brew install pnpm 或者用其他 pnpm 安装方式 pnpm
pnpm install
# 因为这里只是调试用，所以默认永远安装最新的 vocana cli，忽略 lock 文件
```