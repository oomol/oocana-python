# oocana-python-sdk

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

参考 [debug](./docs/debug.md) 文档

## 发布项目

现在发布版本，有 github Action 触发，只需要根据不同的包，打 `@oomol/executor`和`@oomol/sdk-python` 前缀的 tag 即可。

可以参考以下命令，快速发布 tag

```shell
git tag @oomol/python-sdk@0.1.0
git push upstream @oomol/python-sdk@0.1.0
```

## TODO

- [ ] 现有 scripts 发布时，npm publish 出现错误时，并不一定会显示失败。需要调整发布脚本，让发布失败时，显示失败。
    - [publish-executor action](https://github.com/oomol/oocana-python/actions/runs/9137881993/job/25128387566) 向没有权限的 scope 发布 npm 库，提示 403 ，但是 action 并没有失败。而发布相同版本号时，会正常提示失败。
- [x] 让 executor 可以编写多文件，目前由于限制，只能写单文件。
- [ ] 支持协程/多进程穿插执行 block，需要让 stderr 和 stdout 的输出能够对应到正确的 block。
- [ ] 调整项目结构，让 executor 可以写多文件，sdk 导出一份 type hint，executor 不依赖 sdk。
- [x] 处理`DeprecationWarning: There is no current event loop`警告。
- [x] 追加日志。出现过发送的 execute 请求，结果没有向 oocana 发起 inputs 请求的情况。
- [ ] 尝试更改项目结构，让 executor 和 sdk 的版本号，有独立的存储关系。现阶段，sdk 版本号在 pyproject.toml 中，而 executor 版本号在 package.json 中。
    - 现阶段 sdk 是在 src 中，executor 是在 executor 根目录中。executor 依赖 sdk，这个关联是通过 pyproject.toml 的 where 来确认。最好遵循 python 中的 monorepo 项目设计结构。