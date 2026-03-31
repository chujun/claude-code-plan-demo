"""爬取豆瓣Top100书籍数据"""
import sys
sys.path.insert(0, '/data/ai/claudecode/claude-code-plan-demo')

from db import init_db, insert_book, insert_author, get_connection
import re
import json
import time

# 存储所有书籍数据
all_books = []

def parse_meta_text(meta_text):
    """解析meta_text提取作者、译者、出版社、出版日期、价格"""
    if not meta_text:
        return {}
    parts = [p.strip() for p in meta_text.split('/')]
    result = {}
    if len(parts) >= 1:
        result['author_name'] = parts[0]
    if len(parts) >= 2:
        result['translator'] = parts[1]
    if len(parts) >= 3:
        result['publisher'] = parts[2]
    if len(parts) >= 4:
        result['publish_date'] = parts[3]
    if len(parts) >= 5:
        result['price'] = parts[4]
    return result

def clean_author_name(name):
    """清理作者名中的国籍前缀"""
    if not name:
        return name
    # 去掉 [清] [英] [美] 等前缀
    name = re.sub(r'^\[[^\]]+\]\s*', '', name)
    # 去掉 著作/著 等后缀
    name = re.sub(r'\s*[著写过]+$', '', name)
    return name.strip()

def store_books(books_data):
    """存储书籍数据到数据库"""
    conn = get_connection()
    cursor = conn.cursor()

    stored_count = 0
    author_cache = {}

    for book in books_data:
        # 解析meta_text
        parsed = parse_meta_text(book.get('meta_text', ''))
        book.update(parsed)

        # 清理作者名
        author_name_raw = book.get('author_name', '').strip()
        author_name = clean_author_name(author_name_raw)
        book['author_name'] = author_name

        # 检查作者是否已存在
        if author_name and author_name not in author_cache:
            cursor.execute("SELECT id FROM authors WHERE name = ?", (author_name,))
            row = cursor.fetchone()
            if row:
                author_cache[author_name] = row[0]

        # 插入书籍（使用已有的完整数据）
        douban_id = book.get('douban_id')
        if douban_id:
            # 检查是否已存在
            cursor.execute("SELECT id FROM books WHERE douban_id = ?", (douban_id,))
            existing = cursor.fetchone()

            if not existing:
                # 插入新书籍
                now = 'CURRENT_TIMESTAMP'
                cursor.execute(f"""
                    INSERT INTO books (douban_id, title, author_name, translator, publisher,
                        publish_date, pages, price, isbn, rating, rating_count, summary,
                        book_url, cover_url, rank, author_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, {now}, {now})
                """, (
                    book.get('douban_id'),
                    book.get('title'),
                    book.get('author_name'),
                    book.get('translator'),
                    book.get('publisher'),
                    book.get('publish_date'),
                    book.get('pages', ''),
                    book.get('price'),
                    book.get('isbn', ''),
                    book.get('rating'),
                    book.get('rating_count'),
                    book.get('summary'),
                    book.get('book_url'),
                    book.get('cover_url'),
                    book.get('rank'),
                    author_cache.get(author_name)
                ))
                stored_count += 1

        all_books.append(book)

    conn.commit()
    conn.close()
    return stored_count

if __name__ == '__main__':
    print("等待从浏览器获取数据...")
    print("请在浏览器中运行以下代码获取数据，然后保存为 books_data.json:")
    print("""
    const books = [];
    document.querySelectorAll('tr.item').forEach(row => {
        const book = {};
        const rankTd = row.querySelector('td.number');
        if (rankTd) book.rank = parseInt(rankTd.textContent.trim());
        const titleLink = row.querySelector('div.pl2 a');
        if (titleLink) {
            book.title = titleLink.textContent.trim().replace(/\\s+/g, ' ');
            book.book_url = titleLink.href;
            const m = titleLink.href.match(/\\/subject\\/(\\d+)\\//);
            if (m) book.douban_id = m[1];
        }
        const img = row.querySelector('td:first-child img');
        if (img) book.cover_url = img.src;
        const pl = row.querySelector('p.pl');
        if (pl) book.meta_text = pl.textContent.trim();
        const rating = row.querySelector('span.rating_nums');
        if (rating) book.rating = parseFloat(rating.textContent.trim());
        row.querySelectorAll('span.pl').forEach(s => {
            if (s.textContent.includes('评价')) {
                const m = s.textContent.match(/(\\d+)/);
                if (m) book.rating_count = parseInt(m[1]);
            }
        });
        const quote = row.querySelector('p.quote');
        if (quote) book.summary = quote.textContent.trim();
        if (book.douban_id) books.push(book);
    });
    console.log(JSON.stringify(books));
    """)