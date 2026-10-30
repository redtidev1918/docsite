跨仓库导航 CI 在匿名克隆私有 ParaNote、ludum、Graf 时失败，导致根本没有运行 navcheck。本修复通过 gh credential helper 使用仓库现有跨仓库 token，并禁用 checkout 持久化的单仓库凭据，避免认证覆盖。

优先支持权限更窄的 NAVCHECK_REPOS_TOKEN，兼容当前 PROFILE_REPO_TOKEN，最后回落 github.token。未增加或导出凭据，克隆失败仍使检查失败，不跳过目标。同步仓库名大小写并去掉已重命名且重复的 release-infra。

验证：[修复分支完整 workflow_dispatch 成功](https://github.com/redtidev1918/docsite/actions/runs/41081870162)，包含私有仓库克隆与全量导航检查。同步记录 PR #11 已上线的状态。
