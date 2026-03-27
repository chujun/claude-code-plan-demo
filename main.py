"""豆瓣 Top250 书籍爬虫 - 主入口"""

import logging
import sys

from db import init_db, insert_author, insert_book, update_author_geo, get_authors_without_geo
from scraper import create_session, scrape_top250_list, scrape_book_detail, scrape_author_page
from geocoder import geocode_location

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraper.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("豆瓣 Top250 书籍爬虫启动")
    logger.info("=" * 60)

    # 1. 初始化数据库
    logger.info("初始化数据库...")
    init_db()

    # 2. 创建 HTTP Session
    session = create_session()

    # 3. 抓取 Top250 列表
    logger.info("开始抓取 Top250 列表页...")
    books_list = scrape_top250_list(session)
    logger.info(f"共获取 {len(books_list)} 本书的基本信息")

    if not books_list:
        logger.error("未获取到任何书籍信息，请检查网络或反爬策略")
        return

    # 4. 逐本抓取详情并入库
    success_count = 0
    author_cache = {}  # name -> author_id 缓存

    for i, book in enumerate(books_list, 1):
        logger.info(f"[{i}/{len(books_list)}] 处理: {book.get('title', '未知')}")

        # 抓取书籍详情页
        book_url = book.get("book_url")
        if book_url:
            detail = scrape_book_detail(session, book_url)
            book.update(detail)

        # 处理作者信息
        author_name = book.get("author_name", "").strip()
        author_id = None

        if author_name:
            if author_name in author_cache:
                author_id = author_cache[author_name]
            else:
                author_data = {"name": author_name}

                # 如果有作者页面链接，抓取作者详情
                author_url = book.get("author_douban_url")
                if author_url:
                    logger.info(f"  抓取作者页面: {author_url}")
                    author_detail = scrape_author_page(session, author_url)
                    author_data.update(author_detail)
                    author_data["douban_url"] = author_url

                author_id = insert_author(author_data)
                if author_id:
                    author_cache[author_name] = author_id
                    logger.info(f"  作者入库: {author_name} (id={author_id})")

        # 书籍入库
        book["author_id"] = author_id
        book_id = insert_book(book)
        if book_id:
            success_count += 1
            logger.info(f"  书籍入库成功: {book.get('title')} (id={book_id})")
        else:
            logger.warning(f"  书籍入库失败: {book.get('title')}")

    logger.info(f"书籍抓取完成: 成功 {success_count}/{len(books_list)}")

    # 5. 地理编码：为有出生地的作者获取经纬度
    logger.info("开始地理编码...")
    authors_to_geocode = get_authors_without_geo()
    logger.info(f"需要地理编码的作者: {len(authors_to_geocode)} 位")

    geo_success = 0
    for author in authors_to_geocode:
        logger.info(f"  地理编码: {author['name']} - {author['birthplace']}")
        result = geocode_location(author["birthplace"])
        if result:
            update_author_geo(
                author["id"],
                result["latitude"],
                result["longitude"],
                result.get("continent"),
                result.get("country"),
            )
            geo_success += 1
            logger.info(f"    -> ({result['latitude']}, {result['longitude']}) "
                        f"{result.get('country', '')} {result.get('continent', '')}")
        else:
            logger.warning(f"    -> 地理编码失败")

    # 6. 输出统计摘要
    logger.info("=" * 60)
    logger.info("爬取完成！统计摘要:")
    logger.info(f"  书籍总数: {success_count}")
    logger.info(f"  作者总数: {len(author_cache)}")
    logger.info(f"  地理编码成功: {geo_success}/{len(authors_to_geocode)}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
