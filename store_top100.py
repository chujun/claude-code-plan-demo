"""存储TOP100书籍数据"""
import sys
sys.path.insert(0, '/data/ai/claudecode/claude-code-plan-demo')

from db import init_db, insert_book, insert_author, get_connection
import re
import json

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
    # 去掉 著作/著/写 等后缀
    name = re.sub(r'\s*[著写过]+$', '', name)
    return name.strip()

def store_books(books_data):
    """存储书籍数据到数据库"""
    conn = get_connection()
    cursor = conn.cursor()

    stored_count = 0
    skipped_count = 0

    for book in books_data:
        douban_id = book.get('douban_id')
        if not douban_id:
            skipped_count += 1
            continue

        # 检查是否已存在
        cursor.execute("SELECT id FROM books WHERE douban_id = ?", (douban_id,))
        existing = cursor.fetchone()

        if existing:
            skipped_count += 1
            continue

        # 解析meta_text
        parsed = parse_meta_text(book.get('meta_text', ''))
        book.update(parsed)

        # 清理作者名
        author_name_raw = book.get('author_name', '').strip()
        author_name = clean_author_name(author_name_raw)
        book['author_name'] = author_name

        # 插入书籍
        now = 'CURRENT_TIMESTAMP'
        cursor.execute(f"""
            INSERT INTO books (douban_id, title, author_name, translator, publisher,
                publish_date, pages, price, isbn, rating, rating_count, summary,
                book_url, cover_url, rank, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, {now}, {now})
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
            book.get('rank')
        ))
        stored_count += 1

    conn.commit()
    conn.close()
    return stored_count, skipped_count

if __name__ == '__main__':
    # 读取books_data.json
    try:
        with open('books_data.json', 'r', encoding='utf-8') as f:
            books_data = json.load(f)
        print(f"从 books_data.json 加载了 {len(books_data)} 本书")
    except FileNotFoundError:
        print("错误: books_data.json 文件不存在")
        sys.exit(1)

    # 初始化数据库
    init_db()
    print("数据库已初始化")

    # 存储书籍
    stored, skipped = store_books(books_data)
    print(f"\n存储完成: 新增 {stored} 本, 跳过 {skipped} 本 (已存在)")

    # 验证
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM books")
    count = cursor.fetchone()[0]
    print(f"数据库中共有 {count} 本书")
    conn.close()