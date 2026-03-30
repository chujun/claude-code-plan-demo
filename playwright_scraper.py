"""豆瓣 Top250 书籍爬虫 - Playwright 浏览器版本

使用真实浏览器访问，绕过反爬机制。
依赖: pip install playwright && playwright install chromium
"""

import asyncio
import logging
import random
import re
from typing import Optional

from playwright.async_api import async_playwright, Page, Browser

from config import TOP250_BASE_URL, DOUBAN_BASE_URL

logger = logging.getLogger(__name__)

# 请求间隔（秒）
DELAY_MIN = 2.0
DELAY_MAX = 4.0


async def _random_delay() -> None:
    delay = random.uniform(DELAY_MIN, DELAY_MAX)
    await asyncio.sleep(delay)


async def _safe_navigate(page: Page, url: str) -> bool:
    """导航到指定 URL，返回是否成功"""
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await _random_delay()
        return True
    except Exception as e:
        logger.error(f"导航失败: {url}, 错误: {e}")
        return False


async def scrape_top250_page(page: Page, start: int) -> list[dict]:
    """抓取单页 Top250 列表，返回书籍基本信息列表"""
    url = f"{TOP250_BASE_URL}?start={start}"
    logger.info(f"抓取列表页: {url}")

    if not await _safe_navigate(page, url):
        return []

    books: list[dict] = await page.evaluate("""() => {
        const books = [];
        const rows = document.querySelectorAll('tr.item');
        rows.forEach(row => {
            const book = {};
            // 排名
            const rankTd = row.querySelector('td.number');
            if (rankTd) {
                const rank = parseInt(rankTd.textContent.trim());
                if (!isNaN(rank)) book.rank = rank;
            }
            // 书名和链接
            const titleLink = row.querySelector('div.pl2 a');
            if (titleLink) {
                book.title = titleLink.textContent.trim().replace(/\\s+/g, ' ');
                book.book_url = titleLink.href;
                const m = titleLink.href.match(/\\/subject\\/(\\d+)\\//);
                if (m) book.douban_id = m[1];
            }
            // 封面
            const img = row.querySelector('td:first-child img');
            if (img) book.cover_url = img.src;
            // 元信息
            const pl = row.querySelector('p.pl');
            if (pl) book.meta_text = pl.textContent.trim();
            // 评分
            const rating = row.querySelector('span.rating_nums');
            if (rating) {
                const r = parseFloat(rating.textContent.trim());
                if (!isNaN(r)) book.rating = r;
            }
            // 评价人数
            row.querySelectorAll('span.pl').forEach(s => {
                const t = s.textContent.trim();
                if (t.includes('评价')) {
                    const m = t.match(/(\\d+)/);
                    if (m) book.rating_count = parseInt(m[1]);
                }
            });
            if (book.douban_id) books.push(book);
        });
        return books;
    }""")

    logger.info(f"  解析到 {len(books)} 本书")
    return books


async def scrape_all_top250(page: Page) -> list[dict]:
    """抓取全部 10 页 Top250 列表"""
    all_books: list[dict] = []
    for start in range(0, 250, 25):
        books = await scrape_top250_page(page, start)
        all_books.extend(books)
    logger.info(f"Top250 列表抓取完成，共 {len(all_books)} 本")
    return all_books


async def scrape_book_detail(page: Page, book_url: str) -> dict:
    """抓取书籍详情页，返回补充信息"""
    logger.info(f"  抓取详情: {book_url}")

    if not await _safe_navigate(page, book_url):
        return {}

    detail: dict = await page.evaluate("""() => {
        const d = {};
        const info = document.querySelector('#info');
        if (info) {
            const text = info.innerText;
            const lines = text.split('\\n');
            lines.forEach(line => {
                line = line.trim();
                const sep = line.indexOf(':');
                if (sep === -1) return;
                const key = line.substring(0, sep).trim();
                const val = line.substring(sep + 1).trim();
                if (!val) return;
                if (key === '作者') d.author_name = val;
                else if (key === '译者') d.translator = val;
                else if (key === '出版社') d.publisher = val;
                else if (key === '出版年') d.publish_date = val;
                else if (key === '页数') d.pages = val;
                else if (key === '定价') d.price = val;
                else if (key === 'ISBN') d.isbn = val;
            });
            // 作者链接（格式: /author/ID）
            const links = info.querySelectorAll('a');
            for (const a of links) {
                if (a.href.includes('/author/')) {
                    d.author_book_url = a.href;
                    break;
                }
            }
        }
        // 评分
        const rating = document.querySelector('strong.rating_num');
        if (rating) {
            const r = parseFloat(rating.textContent.trim());
            if (!isNaN(r)) d.rating = r;
        }
        // 评价人数
        const rp = document.querySelector('a.rating_people span');
        if (rp) {
            const n = parseInt(rp.textContent.trim());
            if (!isNaN(n)) d.rating_count = n;
        }
        // 简介
        const intro = document.querySelector('#link-report .all.hidden .intro') ||
                      document.querySelector('#link-report .intro');
        if (intro) d.summary = intro.textContent.trim();
        return d;
    }""")

    return detail


async def _resolve_author_url(page: Page, author_book_url: str) -> Optional[str]:
    """
    将 book.douban.com/author/ID 解析为真实作者页 URL
    豆瓣会 301 跳转到 www.douban.com/personage/ID/
    """
    try:
        response = await page.goto(
            author_book_url,
            wait_until="domcontentloaded",
            timeout=20000,
        )
        await _random_delay()
        final_url = page.url
        if "/personage/" in final_url:
            return final_url
        logger.warning(f"作者页跳转后 URL 异常: {final_url}")
        return final_url
    except Exception as e:
        logger.error(f"解析作者 URL 失败: {author_book_url}, 错误: {e}")
        return None


async def scrape_author_page(page: Page, author_book_url: str) -> dict:
    """
    抓取作者页面（personage），提取出生地、出生日期等。
    author_book_url: book.douban.com/author/ID 格式
    """
    logger.info(f"  抓取作者: {author_book_url}")

    final_url = await _resolve_author_url(page, author_book_url)
    if not final_url:
        return {}

    author_info: dict = await page.evaluate("""() => {
        const info = {};
        // 姓名
        const h1 = document.querySelector('h1');
        if (h1) info.name = h1.textContent.trim();
        // 基本信息 li 列表
        document.querySelectorAll('ul li').forEach(li => {
            const text = li.textContent.trim();
            if (text.startsWith('性别:') || text.startsWith('性别：')) {
                info.gender = text.replace(/^性别[:：]\\s*/, '');
            } else if (text.startsWith('出生日期:') || text.startsWith('出生日期：')) {
                info.birth_date = text.replace(/^出生日期[:：]\\s*/, '');
            } else if (text.startsWith('出生地:') || text.startsWith('出生地：')) {
                info.birthplace = text.replace(/^出生地[:：]\\s*/, '');
            } else if (text.startsWith('职业:') || text.startsWith('职业：')) {
                info.occupation = text.replace(/^职业[:：]\\s*/, '');
            }
        });
        // 简介（展开前）
        const descEl = document.querySelector('.abstract, .description');
        if (descEl) info.description = descEl.textContent.trim().substring(0, 500);
        info.douban_url = window.location.href;
        return info;
    }""")

    return author_info


async def run_playwright_scraper() -> list[dict]:
    """
    主流程：使用 Playwright 浏览器抓取 Top250 书籍及作者信息。
    返回包含书籍+作者数据的列表。
    """
    results: list[dict] = []
    author_cache: dict[str, dict] = {}  # author_book_url -> author_info

    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="zh-CN",
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()

        # 先访问豆瓣首页预热 Cookie
        try:
            await page.goto("https://www.douban.com/", wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2)
            logger.info("浏览器预热完成")
        except Exception as e:
            logger.warning(f"预热失败（继续）: {e}")

        # 1. 抓取 Top250 列表
        books = await scrape_all_top250(page)

        # 2. 逐本抓取详情 + 作者
        for i, book in enumerate(books, 1):
            logger.info(f"[{i}/{len(books)}] 处理: {book.get('title', '未知')}")
            book_url = book.get("book_url")
            if not book_url:
                results.append(book)
                continue

            # 书籍详情
            detail = await scrape_book_detail(page, book_url)
            book.update(detail)

            # 作者信息
            author_book_url = book.get("author_book_url")
            if author_book_url:
                if author_book_url in author_cache:
                    book["author_info"] = author_cache[author_book_url]
                else:
                    author_info = await scrape_author_page(page, author_book_url)
                    author_cache[author_book_url] = author_info
                    book["author_info"] = author_info

            results.append(book)

        await browser.close()

    logger.info(f"Playwright 抓取完成，共 {len(results)} 本书")
    return results


def scrape_with_playwright() -> list[dict]:
    """同步入口，供 main.py 调用"""
    return asyncio.run(run_playwright_scraper())
