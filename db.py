"""数据库初始化与操作模块"""

import sqlite3
import os
from datetime import datetime

from config import DB_PATH


def get_connection():
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """创建数据库表结构"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            douban_url TEXT,
            birthplace TEXT,
            birth_date TEXT,
            description TEXT,
            continent TEXT,
            country TEXT,
            latitude REAL,
            longitude REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            douban_id TEXT UNIQUE,
            title TEXT NOT NULL,
            author_name TEXT,
            translator TEXT,
            publisher TEXT,
            publish_date TEXT,
            pages TEXT,
            price TEXT,
            isbn TEXT,
            rating REAL,
            rating_count INTEGER,
            summary TEXT,
            book_url TEXT,
            cover_url TEXT,
            rank INTEGER,
            author_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES authors(id)
        )
    """)

    # 索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_books_douban_id ON books(douban_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_authors_name ON authors(name)")

    conn.commit()
    conn.close()


def insert_author(author_data):
    """插入作者（按 name 去重），返回 author id"""
    conn = get_connection()
    cursor = conn.cursor()

    name = author_data.get("name", "").strip()
    if not name:
        conn.close()
        return None

    # 检查是否已存在
    cursor.execute("SELECT id FROM authors WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row:
        author_id = row["id"]
        # 更新已有记录（补充信息）
        updates = {}
        for field in ("douban_url", "birthplace", "birth_date", "description", "continent", "country"):
            if author_data.get(field):
                updates[field] = author_data[field]
        if updates:
            updates["updated_at"] = datetime.now().isoformat()
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            values = list(updates.values()) + [author_id]
            cursor.execute(f"UPDATE authors SET {set_clause} WHERE id = ?", values)
            conn.commit()
        conn.close()
        return author_id

    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO authors (name, douban_url, birthplace, birth_date, description, continent, country, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        author_data.get("douban_url"),
        author_data.get("birthplace"),
        author_data.get("birth_date"),
        author_data.get("description"),
        author_data.get("continent"),
        author_data.get("country"),
        now, now,
    ))
    author_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return author_id


def insert_book(book_data):
    """插入书籍（按 douban_id 去重），返回 book id"""
    conn = get_connection()
    cursor = conn.cursor()

    douban_id = book_data.get("douban_id")
    if not douban_id:
        conn.close()
        return None

    # 检查是否已存在
    cursor.execute("SELECT id FROM books WHERE douban_id = ?", (douban_id,))
    row = cursor.fetchone()
    if row:
        book_id = row["id"]
        # 更新已有记录
        now = datetime.now().isoformat()
        cursor.execute("""
            UPDATE books SET title=?, author_name=?, translator=?, publisher=?,
                publish_date=?, pages=?, price=?, isbn=?, rating=?, rating_count=?,
                summary=?, book_url=?, cover_url=?, rank=?, author_id=?, updated_at=?
            WHERE id=?
        """, (
            book_data.get("title"), book_data.get("author_name"),
            book_data.get("translator"), book_data.get("publisher"),
            book_data.get("publish_date"), book_data.get("pages"),
            book_data.get("price"), book_data.get("isbn"),
            book_data.get("rating"), book_data.get("rating_count"),
            book_data.get("summary"), book_data.get("book_url"),
            book_data.get("cover_url"), book_data.get("rank"),
            book_data.get("author_id"), now, book_id,
        ))
        conn.commit()
        conn.close()
        return book_id

    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO books (douban_id, title, author_name, translator, publisher,
            publish_date, pages, price, isbn, rating, rating_count,
            summary, book_url, cover_url, rank, author_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        douban_id, book_data.get("title"), book_data.get("author_name"),
        book_data.get("translator"), book_data.get("publisher"),
        book_data.get("publish_date"), book_data.get("pages"),
        book_data.get("price"), book_data.get("isbn"),
        book_data.get("rating"), book_data.get("rating_count"),
        book_data.get("summary"), book_data.get("book_url"),
        book_data.get("cover_url"), book_data.get("rank"),
        book_data.get("author_id"), now, now,
    ))
    book_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return book_id


def update_author_geo(author_id, latitude, longitude, continent=None, country=None):
    """更新作者的经纬度和大洲/国家信息"""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        UPDATE authors SET latitude=?, longitude=?, continent=?, country=?, updated_at=?
        WHERE id=?
    """, (latitude, longitude, continent, country, now, author_id))
    conn.commit()
    conn.close()


def get_authors_without_geo():
    """查询有出生地但缺少经纬度的作者"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, birthplace FROM authors
        WHERE birthplace IS NOT NULL AND birthplace != ''
          AND latitude IS NULL
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
