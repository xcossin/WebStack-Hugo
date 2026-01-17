#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动抓取网站 Logo 工具

用法:
    python scripts/fetch_logos.py

功能:
    1. 扫描 data/webstack.yml 文件,找出缺少 logo 或 logo 文件不存在的网站
    2. 使用多个 favicon API 自动抓取网站的 logo
    3. 下载并保存到 static/assets/images/logos/ 目录
    4. 更新 webstack.yml 中的 logo 字段

配置:
    在 config.toml 中设置 autoFetchLogos = true/false 来控制是否启用
"""

import os
import re
import sys
import yaml
import json
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from PIL import Image
from io import BytesIO

# 添加项目根目录到路径
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 配置路径
CONFIG_FILE = PROJECT_ROOT / "config.toml"
WEBSTACK_FILE = PROJECT_ROOT / "data" / "webstack.yml"
LOGOS_DIR = PROJECT_ROOT / "static" / "assets" / "images" / "logos"

# Favicon API 列表 (按优先级排序)
FAVICON_APIS = [
    # Google Favicon Service (最可靠)
    lambda domain: f"https://www.google.com/s2/favicons?domain={domain}&sz=128",
    # Favicon.io API
    lambda domain: f"https://favicon.io/api/get?url={domain}",
    # 直接从网站获取
    lambda domain: f"https://{domain}/favicon.ico",
]


def parse_config() -> Dict:
    """解析 config.toml 文件"""
    config = {"autoFetchLogos": True}  # 默认开启
    
    if not CONFIG_FILE.exists():
        print(f"警告: 配置文件 {CONFIG_FILE} 不存在,使用默认配置")
        return config
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            # 简单解析 toml (查找 autoFetchLogos)
            match = re.search(r'autoFetchLogos\s*=\s*(true|false)', content, re.IGNORECASE)
            if match:
                config["autoFetchLogos"] = match.group(1).lower() == "true"
    except Exception as e:
        print(f"解析配置文件时出错: {e},使用默认配置")
    
    return config


def extract_domain(url: str) -> str:
    """从 URL 中提取域名"""
    # 移除协议
    url = re.sub(r'^https?://', '', url)
    # 移除路径
    url = url.split('/')[0]
    # 移除端口
    url = url.split(':')[0]
    return url


def sanitize_filename(title: str) -> str:
    """将网站标题转换为安全的文件名"""
    # 移除特殊字符,保留中文、英文、数字
    filename = re.sub(r'[<>:"/\\|?*]', '', title)
    # 替换空格为下划线(可选,这里保持原样以便识别)
    # filename = filename.replace(' ', '_')
    return filename


def fetch_favicon_from_api(domain: str, api_func) -> Optional[bytes]:
    """从 API 获取 favicon"""
    try:
        url = api_func(domain)
        response = requests.get(url, timeout=10, allow_redirects=True)
        if response.status_code == 200 and len(response.content) > 0:
            # 验证是否为有效图片
            try:
                img = Image.open(BytesIO(response.content))
                img.verify()
                return response.content
            except Exception:
                pass
    except Exception:
        pass
    return None


def fetch_favicon_from_html(url: str) -> Optional[bytes]:
    """从网站 HTML 中解析并获取 favicon"""
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        if response.status_code == 200:
            html = response.text
            # 查找 favicon link
            patterns = [
                r'<link[^>]*rel=["\']icon["\'][^>]*href=["\']([^"\']+)["\']',
                r'<link[^>]*rel=["\']shortcut icon["\'][^>]*href=["\']([^"\']+)["\']',
                r'<link[^>]*rel=["\']apple-touch-icon["\'][^>]*href=["\']([^"\']+)["\']',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    favicon_url = match.group(1)
                    # 处理相对路径
                    if favicon_url.startswith('//'):
                        favicon_url = 'https:' + favicon_url
                    elif favicon_url.startswith('/'):
                        parsed = urllib.parse.urlparse(url)
                        favicon_url = f"{parsed.scheme}://{parsed.netloc}{favicon_url}"
                    elif not favicon_url.startswith('http'):
                        parsed = urllib.parse.urlparse(url)
                        favicon_url = f"{parsed.scheme}://{parsed.netloc}/{favicon_url}"
                    
                    # 下载 favicon
                    try:
                        favicon_response = requests.get(favicon_url, timeout=10)
                        if favicon_response.status_code == 200:
                            img = Image.open(BytesIO(favicon_response.content))
                            img.verify()
                            return favicon_response.content
                    except Exception:
                        continue
    except Exception:
        pass
    return None


def download_and_save_logo(url: str, title: str) -> Optional[str]:
    """下载并保存 logo,返回文件名"""
    domain = extract_domain(url)
    print(f"  正在抓取 {title} ({domain})...")
    
    # 方法1: 尝试使用 API
    for api_func in FAVICON_APIS:
        try:
            favicon_data = fetch_favicon_from_api(domain, api_func)
            if favicon_data:
                return save_logo_image(favicon_data, title, domain)
        except Exception as e:
            continue
    
    # 方法2: 从网站 HTML 解析
    try:
        full_url = url if url.startswith('http') else f"https://{url}"
        favicon_data = fetch_favicon_from_html(full_url)
        if favicon_data:
            return save_logo_image(favicon_data, title, domain)
    except Exception as e:
        pass
    
    # 方法3: 直接尝试 /favicon.ico
    try:
        full_url = url if url.startswith('http') else f"https://{url}"
        favicon_url = f"{full_url.rstrip('/')}/favicon.ico"
        response = requests.get(favicon_url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.verify()
            return save_logo_image(response.content, title, domain)
    except Exception:
        pass
    
    print(f"    ✗ 抓取失败")
    return None


def save_logo_image(image_data: bytes, title: str, domain: str) -> str:
    """保存图片到文件,返回文件名"""
    try:
        # 打开图片
        img = Image.open(BytesIO(image_data))
        
        # 转换为 RGB (如果不是的话)
        if img.mode in ('RGBA', 'LA', 'P'):
            # 保持透明通道
            if img.mode == 'P':
                img = img.convert('RGBA')
        else:
            img = img.convert('RGB')
        
        # 调整大小到合适尺寸 (128x128 或保持比例)
        target_size = (128, 128)
        if img.size != target_size:
            # 使用高质量重采样
            img = img.resize(target_size, Image.Resampling.LANCZOS)
        
        # 生成文件名
        filename = sanitize_filename(title)
        # 尝试多种格式
        extensions = ['webp', 'png', 'jpg']
        
        for ext in extensions:
            logo_path = LOGOS_DIR / f"{filename}.{ext}"
            # 如果文件已存在,使用新的
            if logo_path.exists():
                # 添加时间戳避免冲突
                import time
                timestamp = int(time.time())
                filename = f"{filename}_{timestamp}"
                logo_path = LOGOS_DIR / f"{filename}.{ext}"
            
            try:
                if ext == 'webp':
                    img.save(logo_path, 'WEBP', quality=95, method=6)
                elif ext == 'png':
                    if img.mode == 'RGBA':
                        img.save(logo_path, 'PNG', optimize=True)
                    else:
                        img = img.convert('RGB')
                        img.save(logo_path, 'PNG', optimize=True)
                else:  # jpg
                    if img.mode == 'RGBA':
                        # 创建白色背景
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3] if len(img.split()) == 4 else None)
                        img = background
                    img.save(logo_path, 'JPEG', quality=95, optimize=True)
                
                print(f"    ✓ 成功保存: {logo_path.name}")
                return logo_path.name
            except Exception as e:
                continue
        
        print(f"    ✗ 保存失败: 无法转换为支持的格式")
        return None
        
    except Exception as e:
        print(f"    ✗ 处理图片失败: {e}")
        return None


def collect_sites(data: List[Dict]) -> List[Tuple[str, str, str, Dict]]:
    """收集所有需要处理的网站信息
    返回: [(url, title, current_logo, parent_dict), ...]
    """
    sites = []
    
    def process_links(links):
        for link in links:
            if 'url' in link and 'title' in link:
                url = link['url']
                title = link['title']
                current_logo = link.get('logo', '')
                
                # 检查是否需要抓取
                # logo_stripped = current_logo.strip()
                logo_stripped = str(current_logo or "").strip()
                if not current_logo or logo_stripped == '' or logo_stripped == "''":
                    sites.append((url, title, current_logo, link))
                else:
                    # 检查文件是否存在
                    logo_path = LOGOS_DIR / current_logo
                    if not logo_path.exists():
                        sites.append((url, title, current_logo, link))
    
    for category in data:
        # 处理直接 links
        if 'links' in category:
            process_links(category['links'])
        
        # 处理 list -> term -> links
        if 'list' in category:
            for term_item in category['list']:
                if 'links' in term_item:
                    process_links(term_item['links'])
    
    return sites


def main():
    """主函数"""
    print("=" * 60)
    print("网站 Logo 自动抓取工具")
    print("=" * 60)
    
    # 检查配置
    config = parse_config()
    if not config.get("autoFetchLogos", True):
        print("提示: autoFetchLogos 配置为 false,自动抓取功能已禁用")
        print("如需启用,请在 config.toml 中设置: autoFetchLogos = true")
        return
    
    # 检查文件是否存在
    if not WEBSTACK_FILE.exists():
        print(f"错误: 文件 {WEBSTACK_FILE} 不存在")
        return
    
    # 确保 logos 目录存在
    LOGOS_DIR.mkdir(parents=True, exist_ok=True)
    
    # 读取 webstack.yml
    try:
        with open(WEBSTACK_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"错误: 无法读取 {WEBSTACK_FILE}: {e}")
        return
    
    # 收集需要处理的网站
    sites = collect_sites(data)
    
    if not sites:
        print("\n✓ 所有网站都已配置 logo,无需抓取")
        return
    
    print(f"\n找到 {len(sites)} 个需要抓取 logo 的网站:\n")
    
    # 统计
    success_count = 0
    failed_sites = []
    
    # 处理每个网站
    for url, title, current_logo, link_dict in sites:
        logo_filename = download_and_save_logo(url, title)
        
        if logo_filename:
            # 更新 webstack.yml 中的 logo 字段
            link_dict['logo'] = logo_filename
            success_count += 1
        else:
            failed_sites.append((title, url))
    
    # 保存更新后的 webstack.yml
    if success_count > 0:
        try:
            with open(WEBSTACK_FILE, 'w', encoding='utf-8') as f:
                # 写入 YAML 头部
                f.write('---\n\n')
                # 写入数据
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            print(f"\n✓ 已更新 {WEBSTACK_FILE}")
        except Exception as e:
            print(f"\n✗ 保存文件失败: {e}")
    
    # 输出统计
    print("\n" + "=" * 60)
    print(f"完成! 成功: {success_count}/{len(sites)}")
    
    if failed_sites:
        print(f"\n以下 {len(failed_sites)} 个网站抓取失败,请手动添加:")
        for title, url in failed_sites:
            print(f"  - {title}: {url}")
        print(f"\n请将 logo 文件放到: {LOGOS_DIR}")
        print("然后在 webstack.yml 中更新 logo 字段")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
