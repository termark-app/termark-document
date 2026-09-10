# Termark 旧文档域名跳转站

官网、文档和博客已统一到 https://www.termark.app/ ，内容请在 `termark-app/termark-website` 仓库维护。

原文档源码保留供历史参考。此项目部署仅发布 301 跳转规则，不再构建文档正文。

## Cloudflare Pages

继续绑定 `docs.termark.app`。原配置可以保持：

- 构建命令：`npm run docs:build`（或 `yarn docs:build`）
- 输出目录：`.vitepress/dist`

构建脚本仅复制 `redirect-site/_redirects` 和 `404.html`。也可以把构建命令清空，直接使用 `redirect-site` 作为输出目录。

`public/_redirects` 同步保留同一套规则，兼容 Pages 直接执行 `vitepress build` 的既有构建配置。更新跳转时两个文件须保持一致。

具体重定向优先，最后才是保留路径的兜底规则。不要把这些规则部署到 `www.termark.app`。请长期保留旧域名和 HTTPS，部署后检查 301 与目标页面的 200 状态。
