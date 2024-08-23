# Debug

现在 executor 默认有 oocana-rust 进行 spawn。不过在 spawn 前，会先向 broker 发送一个 message，询问当前是否存在 executor 能够响应当前 session。
如果想要在本地进行断点调试，可以在 vscode 的 launch.json 配置好 session id，在 oocana 启动时，传入相同的`--session-id`，即可进行断点调试。