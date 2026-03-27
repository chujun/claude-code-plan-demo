"""临时诊断脚本：查看豆瓣页面实际 HTML 结构"""
import sys
import requests
import random
from bs4 import BeautifulSoup
from config import USER_AGENTS

# 从本地缓存文件读取（如果有），否则重新抓取
import os
cache_file = "/tmp/douban_top250_page1.html"

if os.path.exists(cache_file):
    print(f"从缓存读取: {cache_file}")
    with open(cache_file, encoding="utf-8") as f:
        html = f.read()
else:
    print("抓取页面...")
    s = requests.Session()
    s.headers["User-Agent"] = random.choice(USER_AGENTS)
    s.headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    s.headers["Accept-Language"] = "zh-CN,zh;q=0.9"
    r = s.get("https://book.douban.com/top250", timeout=15)
    html = r.text
    with open(cache_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已缓存到 {cache_file}")

soup = BeautifulSoup(html, "lxml")

print("\n=== 检查常见元素 ===")
print(f"<tr class='item'>: {len(soup.find_all('tr', class_='item'))}")
print(f"<table width='100%'>: {len(soup.find_all('table', width='100%'))}")
print(f"<div class='pl2'>: {len(soup.find_all('div', class_='pl2'))}")
print(f"<span class='rating_nums'>: {len(soup.find_all('span', class_='rating_nums'))}")
print(f"<a href 含 /subject/>: {len([a for a in soup.find_all('a') if '/subject/' in a.get('href','')][:5])}")

print("\n=== 前5个 /subject/ 链接 ===")
for a in soup.find_all("a"):
    href = a.get("href", "")
    if "/subject/" in href:
        print(f"  {href} -> {a.get_text(strip=True)[:30]}")
        break

print("\n=== HTML 开头 500 字符 ===")
print(html[:500])

print("\n=== body 内前 2000 字符 ===")
body = soup.find("body")
if body:
    print(str(body)[:2000])
