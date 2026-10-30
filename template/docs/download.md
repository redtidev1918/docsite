# 下载 @@NAME@@

**语言 / Language:** 中文 · [English](/en/download.md)

本页汇总最新安装包与获取方式。完整资产与历史版本见 [Releases](https://github.com/@@REPO@@/releases)。

## 发布产物

| 平台 | 包 | 说明 |
| :-- | :-- | :-- |
| Windows | `@@NAME@@-<version>-windows-x64.zip` | 解压即用 |
| macOS | `@@NAME@@-<version>-macos-arm64.tar.gz` | 首次运行需在「隐私与安全性」中放行 |
| Linux | `@@NAME@@-<version>-linux-x64.tar.gz` | 解压后 `chmod +x` |

校验文件：`SHA256SUMS`。

## 校验下载

```bash
sha256sum -c SHA256SUMS
```

## 其他获取方式

- npm：`npm install @@NAME@@`
- 源码：`git clone https://github.com/@@REPO@@.git`

## 更新日志

见 [CHANGELOG](https://github.com/@@REPO@@/blob/@@BRANCH@@/CHANGELOG.md)。
