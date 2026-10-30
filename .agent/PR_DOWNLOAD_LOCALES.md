DAViewer 迁移试点已有 previewFiles.en，用来保留英文安装说明和截图。当前 docsite 模板忽略这个字段，update 后再生成下载页会丢掉这些内容；英文的通用资产标签也会回退为中文。

补齐按语言加载预览片段、英文平台名称与固定 LF 输出。保留默认 previewFile 仅注入首种语言的行为，补充中英文配置说明。同步下载 workflow 的 checkout v7，下载页文案去掉“始终最新”的保证和装饰性 emoji。

另补 packageMode:merge，现有 Node 工程的 update 只添加 docs scripts 与固定 VitePress 依赖，保留业务字段、workspaces 与原 lock，拒绝不同的同名 docs 命令；check 对合并部分和 lock 中版本做校验。默认 managed 模式不变。

下载页新增3个回归用例先对旧实现复现失败；加上2个 Node 工程保留用例后全量65例(1 skip)。此修复是六仓文档站迁移的共同依赖，不合并或发布业务仓库。
