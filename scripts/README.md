# 自动抓取网站 Logo 工具

## ⚠️ 重要说明

**这个 Python 脚本是完全可选的辅助工具**,不会影响 Hugo 项目的正常构建和部署:

- ✅ **不影响部署**: Hugo 构建和 GitHub Actions 部署不依赖 Python
- ✅ **可选使用**: 如果你不想使用,完全可以手动添加 logo 文件
- ✅ **无需安装**: 在新电脑上使用项目时,**不需要安装 Python** (除非你想使用这个脚本)
- ✅ **手动添加**: Logo 文件可以手动下载并放到 `static/assets/images/logos/` 目录

这个脚本只是一个**可选的便利工具**,帮助你在添加新网站时自动抓取 logo,节省手动查找和下载的时间。

## 功能介绍

这个工具可以自动抓取网站 Logo,当你添加新网站到 `data/webstack.yml` 时,可以自动为它们下载并配置 Logo,无需手动查找和添加 Logo 文件。

## 特性

- ✅ 自动识别缺少 Logo 的网站
- ✅ 使用多个 Favicon API 提高成功率
- ✅ 自动调整 Logo 尺寸为 128x128 像素
- ✅ 支持多种图片格式 (WebP, PNG, JPG)
- ✅ 可配置开关 (默认开启)
- ✅ 失败时提供手动添加提示

## 安装依赖 (仅在使用脚本时需要)

**注意**: 只有在你想使用这个 Python 脚本时才需要安装依赖。Hugo 项目本身不依赖 Python。

如果你不使用这个脚本,完全可以忽略这部分。

```bash
pip install -r scripts/requirements.txt
```

或者手动安装:

```bash
pip install pyyaml requests Pillow
```

## 使用方法

### 1. 配置

在 `config.toml` 中,你可以控制是否启用自动抓取功能:

```toml
[params]
    autoFetchLogos = true   # 默认开启
```

如果设置为 `false`,脚本会跳过自动抓取。

### 2. 运行脚本

在项目根目录运行:

```bash
python scripts/fetch_logos.py
```

### 3. 添加新网站时的流程

1. **在 `data/webstack.yml` 中添加新网站**,可以暂时不填写 `logo` 字段或留空:

```yaml
- title: 新网站
  url: https://example.com/
  logo: ''  # 留空或暂时不填写
  description: 网站描述
```

2. **运行脚本自动抓取 Logo**:

```bash
python scripts/fetch_logos.py
```

脚本会自动:
- 识别缺少 Logo 的网站
- 尝试从多个来源抓取 Logo
- 下载并保存到 `static/assets/images/logos/` 目录
- 自动更新 `webstack.yml` 中的 `logo` 字段

3. **如果抓取失败**,脚本会提示你手动添加:

```
以下 X 个网站抓取失败,请手动添加:
  - 网站名称: https://example.com/
```

此时你需要:
- 手动下载 Logo 文件
- 将文件放到 `static/assets/images/logos/` 目录
- 在 `webstack.yml` 中更新 `logo` 字段

## 使用方法2

在 VS Code 插件市场搜索并安装：Task Explorer (作者: spmeesseman)。
1.安装插件后，你的侧边栏（左侧或底部）会出现一个 "Task Explorer" 图标。
2.点开它，你会看到 📦 1. 一键安装依赖 和 🚀 2. 运行抓取 Logo 脚本。
3.直接点击旁边的 ▶️ 播放按钮即可运行。
4.关于安装检查：pip install 命令本身就是智能的。如果依赖已经安装了，它会显示 Requirement already satisfied，不会重复下载；如果没安装，它会显示进度条。这些都会在 VS Code 下方的终端面板里显示。

## 抓取策略

脚本使用多种方法尝试抓取 Logo,按优先级顺序:

1. **Google Favicon Service** - 最可靠的方法
2. **Favicon.io API** - 备选方案
3. **网站 HTML 解析** - 从网页中解析 favicon 链接
4. **直接访问 `/favicon.ico`** - 标准位置

## 输出示例

```
============================================================
网站 Logo 自动抓取工具
============================================================

找到 3 个需要抓取 logo 的网站:

  正在抓取 新网站 (example.com)...
    ✓ 成功保存: 新网站.webp
  正在抓取 另一个网站 (example.org)...
    ✗ 抓取失败
  正在抓取 第三个网站 (example.net)...
    ✓ 成功保存: 第三个网站.png

✓ 已更新 data/webstack.yml

============================================================
完成! 成功: 2/3

以下 1 个网站抓取失败,请手动添加:
  - 另一个网站: https://example.org/

请将 logo 文件放到: static/assets/images/logos
然后在 webstack.yml 中更新 logo 字段
============================================================
```

## 注意事项

1. **网络访问**: 需要能够访问目标网站和 Favicon API
2. **海外网站**: 如果网站位于海外且无法访问,抓取会失败,需要手动添加
3. **特殊网站**: 某些网站可能没有标准的 favicon,需要手动处理
4. **文件格式**: 脚本会自动选择最合适的格式保存 (优先 WebP,其次是 PNG 或 JPG)
5. **文件大小**: Logo 会被调整为 128x128 像素,保持透明通道(如果支持)

## 故障排除

### 问题: 依赖安装失败

**解决**: 确保已安装 Python 3.7+,然后使用 pip 安装依赖:

```bash
pip install --upgrade pip
pip install pyyaml requests Pillow
```

### 问题: 抓取总是失败

**可能原因**:
- 网络问题或网站无法访问
- 网站没有标准的 favicon
- 目标网站阻止了自动抓取

**解决**: 手动下载 Logo 并添加到 `static/assets/images/logos/` 目录

### 问题: YAML 文件格式被破坏

**解决**: 脚本会保留原有 YAML 格式,但如果出现问题,建议先备份 `data/webstack.yml`

## 建议

- 定期运行脚本更新 Logo (特别是添加新网站后)
- 对于抓取失败的网站,可以手动添加高质量的 Logo
- 保持 Logo 文件格式统一 (建议使用 PNG 或 WebP 格式)
