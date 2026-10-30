// docsite: managed file, run `python3 docsite.py update` to refresh. Edits to this file are overwritten.
// 渲染 token:base 由仓库名推导(用户/组织站点 <owner>.github.io 为 '/',其余为 '/<repo>/');
// 其余 token 来自 .docsite.json。侧边栏由 _sidebar.md 生成(sidebar.generated.mjs),不在本文件维护。
import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'zh-CN',
  title: '@@EMOJI@@ @@NAME@@',
  description: '@@DESCRIPTION@@',
  base: '@@BASE@@',
  // 亮暗随系统,右上角可切换(默认主题行为)
  appearance: true,
  // _sidebar.md 是导航源文件,不作为页面发布
  srcExclude: ['**/_sidebar.md'],
  // 首页内容源仍是 docs/README.md(docs/en/README.md),访问 / 与 /en/
  rewrites: {
    'README.md': 'index.md',
    'en/README.md': 'en/index.md',
  },
  head: [
    ['link', {
      rel: 'icon',
      href: "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>@@EMOJI@@</text></svg>",
    }],
  ],
  locales: {
    root: {
      label: '简体中文',
      lang: 'zh-CN',
    },
    en: {
      label: 'English',
      lang: 'en-US',
      link: '/en/',
    },
  },
  themeConfig: {
    search: {
      provider: 'local',
    },
  },
})
