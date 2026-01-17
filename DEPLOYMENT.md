# 部署说明

## 关于 Python 脚本和部署

**重要**: 项目中添加的 `scripts/fetch_logos.py` 是一个**可选的辅助工具**,**不会影响**项目的部署和运行。

### 快速回答

1. **添加 Python 脚本后还能部署吗?**  
   ✅ **完全可以!** Python 脚本不影响 Hugo 构建和部署流程。

2. **新电脑需要安装 Python 吗?**  
   ❌ **不需要!** 除非你想使用自动抓取 logo 的功能,否则完全不需要 Python。

3. **如何手动添加 Logo?**  
   只需将 logo 文件放到 `static/assets/images/logos/` 目录,然后在 `data/webstack.yml` 中指定文件名即可。

## 部署方式

### GitHub Actions 自动部署

项目已经包含了一个 GitHub Actions 配置示例 (`.github/workflows/deploy.yml.example`)。

1. **基本部署 (不使用 Python 脚本)**:
   - 将 `.github/workflows/deploy.yml.example` 复制为 `.github/workflows/deploy.yml`
   - 根据你的仓库配置修改分支名称 (main 或 master)
   - 推送到 GitHub 即可自动部署

2. **可选: 在部署前自动抓取 Logo**:
   - 如果启用了自动抓取功能,可以在 GitHub Actions 中运行 Python 脚本
   - 取消注释 `.github/workflows/deploy.yml.example` 中的相关步骤
   - 注意: 这会增加部署时间,但可以帮助自动更新 logo

### 手动部署

1. **本地构建**:
   ```bash
   hugo --minify
   ```

2. **部署到 GitHub Pages**:
   - 将 `public/` 目录的内容推送到 `gh-pages` 分支
   - 或在 GitHub 仓库设置中配置 GitHub Pages

### 其他平台部署

项目支持多种静态网站托管平台:

- **Netlify**: 自动检测 Hugo,无需配置
- **Vercel**: 自动检测 Hugo,无需配置
- **Cloudflare Pages**: 自动检测 Hugo,无需配置
- **Webify**: 支持 Hugo 项目

## 使用 Python 脚本的时机

### 适合使用的场景

- ✅ 你想自动化 logo 抓取流程
- ✅ 你在本地开发,频繁添加新网站
- ✅ 你已经安装了 Python 环境

### 不适合使用的场景

- ❌ 你只是想快速部署网站
- ❌ 你不熟悉 Python
- ❌ 你的电脑没有 Python 环境
- ❌ 你更喜欢手动控制每个 logo

## 手动添加 Logo 的步骤

如果不想使用 Python 脚本,完全可以手动添加:

1. **下载 Logo**:
   - 从网站官网下载
   - 使用浏览器插件提取 favicon
   - 从 favicon 网站下载 (如 favicon.io)

2. **保存文件**:
   - 将文件放到 `static/assets/images/logos/` 目录
   - 建议文件名与网站标题一致 (如 `语雀.webp`)

3. **更新配置**:
   - 在 `data/webstack.yml` 中设置 `logo: 文件名.webp`

## 常见问题

### Q: 部署时需要运行 Python 脚本吗?

A: **不需要!** Python 脚本是可选的。如果你已经在本地手动添加了所有 logo 文件,部署时完全不需要 Python。

### Q: GitHub Actions 会因为缺少 Python 而失败吗?

A: **不会!** 默认的 GitHub Actions 配置只构建 Hugo,不运行 Python 脚本。只有当你明确启用 Python 相关步骤时才会需要 Python。

### Q: 我可以在不同的电脑上使用这个项目吗?

A: **可以!** 
- 如果你想手动添加 logo,完全不需要 Python
- 如果你想使用自动抓取功能,那台电脑才需要 Python

### Q: 如何禁用自动抓取功能?

A: 在 `config.toml` 中设置:
```toml
[params]
    autoFetchLogos = false
```
这个配置只影响 Python 脚本的行为,不影响 Hugo 构建。

## 总结

- ✅ **Python 脚本是可选的**,不影响项目正常使用
- ✅ **部署不依赖 Python**,可以直接部署
- ✅ **新电脑不需要 Python**,除非你想使用自动抓取功能
- ✅ **可以完全手动管理 Logo**,这是完全正常的方式

选择最适合你的工作流程即可!
