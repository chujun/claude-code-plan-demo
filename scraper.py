"""豆瓣页面抓取与解析模块"""

import logging
import random
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import (
    DOUBAN_BASE_URL,
    MAX_RETRIES,
    REQUEST_DELAY_MAX,
    REQUEST_DELAY_MIN,
    RETRY_BACKOFF,
    TOP250_BASE_URL,
    USER_AGENTS,
)

logger = logging.getLogger(__name__)


def create_session():
    """创建配置好重试策略的 requests Session"""
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    # 默认 headers（不手动设置 Accept-Encoding，让 requests 自动处理解压）
    session.headers.update({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    })

    # 先访问豆瓣首页获取 Cookie
    _warm_up_session(session)
    return session


def _warm_up_session(session):
    """访问豆瓣首页以获取初始 Cookie"""
    try:
        session.headers["User-Agent"] = random.choice(USER_AGENTS)
        session.get("https://www.douban.com/", timeout=10)
        logger.info("Session 预热完成，已获取 Cookie")
    except Exception as e:
        logger.warning(f"Session 预热失败: {e}")


def fetch_page(session, url, referer=None):
    """发送 GET 请求，带随机延迟和 UA 轮换"""
    # 随机延迟
    delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
    time.sleep(delay)

    # 轮换 User-Agent
    session.headers["User-Agent"] = random.choice(USER_AGENTS)
    if referer:
        session.headers["Referer"] = referer

    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()
        response.encoding = "utf-8"
        logger.info(f"成功获取页面: {url}")
        return response.text
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 403:
            logger.warning(f"被反爬拦截 (403): {url}，等待更长时间后重试...")
            time.sleep(random.uniform(10, 20))
            session.headers["User-Agent"] = random.choice(USER_AGENTS)
            try:
                response = session.get(url, timeout=15)
                response.raise_for_status()
                response.encoding = "utf-8"
                return response.text
            except Exception as e2:
                logger.error(f"重试后仍失败: {url}, 错误: {e2}")
                return None
        logger.error(f"HTTP 错误: {url}, 错误: {e}")
        return None
    except Exception as e:
        logger.error(f"请求失败: {url}, 错误: {e}")
        return None


def parse_top250_list(html):
    """解析 Top250 列表页，返回书籍基本信息列表"""
    soup = BeautifulSoup(html, "lxml")
    books = []

    # 豆瓣 Top250 实际结构：每本书是一个 <tr class="item">
    items = soup.find_all("tr", class_="item")
    logger.debug(f"找到 <tr class='item'> 数量: {len(items)}")

    # 兼容备用结构：<table width="100%">
    if not items:
        items = soup.find_all("table", width="100%")
        logger.debug(f"回退到 <table width='100%'> 数量: {len(items)}")

    # 再次兼容：通过 div.pl2 直接定位
    if not items:
        pl2_divs = soup.find_all("div", class_="pl2")
        logger.debug(f"回退到 div.pl2 数量: {len(pl2_divs)}")
        if pl2_divs:
            # 用 pl2 的父级 td/tr 作为 item
            items = [div.find_parent("tr") or div.find_parent("td") or div for div in pl2_divs]

    if not items:
        # 输出 HTML 片段帮助调试
        snippet = html[:2000] if html else "(empty)"
        logger.warning(f"未找到任何书籍条目，HTML片段:\n{snippet}")
        return books

    for item in items:
        book = {}

        # 书名和链接
        title_link = item.find("div", class_="pl2")
        if title_link:
            a_tag = title_link.find("a")
            if a_tag:
                book["title"] = a_tag.get_text(strip=True).replace("\n", " ").strip()
                book["book_url"] = a_tag.get("href", "").strip()
                match = re.search(r"/subject/(\d+)/", book["book_url"])
                if match:
                    book["douban_id"] = match.group(1)

        # 封面图片
        img_tag = item.find("img")
        if img_tag:
            book["cover_url"] = img_tag.get("src", "")

        # 书籍元信息（作者 / 出版社 / 日期 / 价格）
        pl_tag = item.find("p", class_="pl")
        if pl_tag:
            meta_text = pl_tag.get_text(strip=True)
            book["meta_text"] = meta_text
            _parse_meta_text(meta_text, book)

        # 评分
        rating_tag = item.find("span", class_="rating_nums")
        if rating_tag:
            try:
                book["rating"] = float(rating_tag.get_text(strip=True))
            except ValueError:
                book["rating"] = None

        # 评价人数：格式为 "(N人评价)"
        for span in item.find_all("span", class_="pl"):
            count_text = span.get_text(strip=True)
            match = re.search(r"(\d+)", count_text)
            if match and "评价" in count_text:
                book["rating_count"] = int(match.group(1))
                break

        # 排名：<td class="number"> 或第一个 <td>
        rank_td = item.find("td", class_="number")
        if not rank_td:
            rank_td = item.find("td")
        if rank_td:
            try:
                book["rank"] = int(rank_td.get_text(strip=True).rstrip("."))
            except ValueError:
                pass

        if book.get("douban_id"):
            books.append(book)

    return books


def _parse_meta_text(meta_text, book):
    """解析列表页中的书籍元信息文本"""
    # 格式通常为: 作者 / 译者 / 出版社 / 出版年 / 价格
    # 或: 作者 / 出版社 / 出版年 / 价格
    parts = [p.strip() for p in meta_text.split("/")]
    if len(parts) >= 4:
        book["author_name"] = parts[0]
        # 判断是否有译者（倒数第三个是出版社，倒数第二个是日期，最后一个是价格）
        book["price"] = parts[-1]
        book["publish_date"] = parts[-2]
        book["publisher"] = parts[-3]
        if len(parts) >= 5:
            book["translator"] = parts[1]
    elif len(parts) == 3:
        book["author_name"] = parts[0]
        book["publisher"] = parts[1]
        book["publish_date"] = parts[2]


def parse_book_detail(html):
    """解析书籍详情页，返回补充信息字典"""
    soup = BeautifulSoup(html, "lxml")
    detail = {}

    # 书籍信息块 <div id="info">
    info_div = soup.find("div", id="info")
    if info_div:
        info_text = info_div.get_text()

        # 逐行提取键值对
        for line in info_text.split("\n"):
            line = line.strip()
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip()
                if key == "作者":
                    detail["author_name"] = _clean_author_name(value)
                elif key == "译者":
                    detail["translator"] = value
                elif key == "出版社":
                    detail["publisher"] = value
                elif key == "出版年":
                    detail["publish_date"] = value
                elif key == "页数":
                    detail["pages"] = value
                elif key == "定价":
                    detail["price"] = value
                elif key == "ISBN":
                    detail["isbn"] = value

        # 作者链接
        author_links = info_div.find_all("a")
        for a in author_links:
            href = a.get("href", "")
            if "/author/" in href:
                detail["author_douban_url"] = urljoin(DOUBAN_BASE_URL, href)
                break

    # 评分
    rating_tag = soup.find("strong", class_="rating_num")
    if rating_tag:
        try:
            detail["rating"] = float(rating_tag.get_text(strip=True))
        except ValueError:
            pass

    # 评分人数
    rating_people = soup.find("a", class_="rating_people")
    if rating_people:
        span = rating_people.find("span")
        if span:
            try:
                detail["rating_count"] = int(span.get_text(strip=True))
            except ValueError:
                pass

    # 内容简介
    intro_div = soup.find("div", id="link-report")
    if intro_div:
        # 优先取展开后的内容
        hidden = intro_div.find("span", class_="all hidden")
        if hidden:
            intro = hidden.find("div", class_="intro")
        else:
            intro = intro_div.find("div", class_="intro")
        if intro:
            detail["summary"] = intro.get_text(strip=True)

    return detail


def _clean_author_name(name):
    """清理作者名中的多余字符"""
    # 去除 [国籍] 前缀，如 [法] 加缪
    name = re.sub(r"\[.*?\]\s*", "", name)
    # 去除多余空格
    name = " ".join(name.split())
    return name.strip()


def parse_author_page(html):
    """解析作者页面，提取出生地等信息"""
    soup = BeautifulSoup(html, "lxml")
    author_info = {}

    # 作者简介区域
    info_div = soup.find("div", id="content")
    if not info_div:
        return author_info

    # 基本信息列表
    info_list = info_div.find("ul")
    if info_list:
        for li in info_list.find_all("li"):
            text = li.get_text(strip=True)
            if "出生地" in text or "birth" in text.lower():
                _, _, value = text.partition(":")
                if not value:
                    _, _, value = text.partition("：")
                author_info["birthplace"] = value.strip()
            elif "出生日期" in text or "born" in text.lower():
                _, _, value = text.partition(":")
                if not value:
                    _, _, value = text.partition("：")
                author_info["birth_date"] = value.strip()

    # 作者简介
    intro_div = info_div.find("div", class_="indent")
    if intro_div:
        intro_span = intro_div.find("span", class_="all hidden")
        if intro_span:
            author_info["description"] = intro_span.get_text(strip=True)
        else:
            # 尝试从简介文本中提取出生地
            intro_text = intro_div.get_text()
            if not author_info.get("birthplace"):
                birthplace = _extract_birthplace_from_text(intro_text)
                if birthplace:
                    author_info["birthplace"] = birthplace
            if not author_info.get("description"):
                author_info["description"] = intro_text.strip()[:500]

    return author_info


def _extract_birthplace_from_text(text):
    """从简介文本中尝试提取出生地"""
    # 匹配常见模式：出生于XXX、生于XXX、XXX人
    patterns = [
        r"出生于(.{2,20}?)[，。,.]",
        r"生于(.{2,20}?)[，。,.]",
        r"born in ([A-Za-z\s,]+?)[\.,]",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None


def scrape_top250_list(session):
    """抓取全部 Top250 列表页，返回所有书籍基本信息"""
    all_books = []
    for start in range(0, 250, 25):
        url = f"{TOP250_BASE_URL}?start={start}"
        logger.info(f"正在抓取列表页: {url}")
        html = fetch_page(session, url, referer=TOP250_BASE_URL)
        if html is None:
            logger.warning(f"跳过列表页: {url}")
            continue
        books = parse_top250_list(html)
        logger.info(f"列表页解析到 {len(books)} 本书")
        all_books.extend(books)
    return all_books


def scrape_book_detail(session, book_url):
    """抓取单本书的详情页"""
    html = fetch_page(session, book_url, referer=TOP250_BASE_URL)
    if html is None:
        return {}
    return parse_book_detail(html)


def scrape_author_page(session, author_url):
    """抓取作者页面"""
    html = fetch_page(session, author_url, referer=DOUBAN_BASE_URL)
    if html is None:
        return {}
    return parse_author_page(html)
