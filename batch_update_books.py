"""批量更新书籍详情数据 - ISBN、页数、简介"""
import sys
sys.path.insert(0, '/data/ai/claudecode/claude-code-plan-demo')
from db import get_connection

# 从详情页采集的书籍数据
books_detail = [
    {"douban_id": "1007305", "isbn": "9787020002207", "pages": "1606", "author_id": 1,
     "summary": "《红楼梦》是一部百科全书式的长篇小说。以宝黛爱情悲剧为主线，以四大家族的荣辱兴衰为背景，描绘出18世纪中国封建社会的方方面面..."},
    {"douban_id": "4913064", "isbn": "9787506365437", "pages": "191", "author_id": 2,
     "summary": "《活着(新版)》讲述了农村人福贵悲惨的人生遭遇。福贵本是个阔少爷，可他嗜赌如命，终于赌光了家业..."},
    {"douban_id": "24531956", "isbn": "9787020096695", "pages": "3104", "author_id": 3,
     "summary": "《哈利·波特(共7册)(精)》编著者J.K.罗琳..."},
    {"douban_id": "4820710", "isbn": "9787530210291", "pages": "304", "author_id": 4,
     "summary": "《1984》是一部杰出的政治寓言小说，也是一部幻想小说..."},
    {"douban_id": "6518605", "isbn": "9787229042066", "pages": "1285", "author_id": 5,
     "summary": "《地球往事·三体》文化大革命如火如荼进行的同时..."},
    {"douban_id": "6082808", "isbn": "9787544253994", "pages": "360", "author_id": 6,
     "summary": "《百年孤独》是魔幻现实主义文学的代表作..."},
    {"douban_id": "1068920", "isbn": "9787806570920", "pages": "1235", "author_id": 7,
     "summary": "小说中的故事发生在1861年美国南北战争前夕..."},
]

def batch_update():
    conn = get_connection()
    cursor = conn.cursor()

    updated = 0
    for book in books_detail:
        cursor.execute('''
            UPDATE books
            SET isbn = ?, pages = ?, summary = ?, author_id = ?
            WHERE douban_id = ?
        ''', (book['isbn'], book['pages'], book['summary'], book['author_id'], book['douban_id']))
        updated += 1

    conn.commit()
    conn.close()
    return updated

if __name__ == '__main__':
    count = batch_update()
    print(f"更新了 {count} 本书")

    # 验证
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM books WHERE isbn != ''")
    with_isbn = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM books WHERE pages != ''")
    with_pages = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM books WHERE summary != '' AND summary IS NOT NULL")
    with_summary = cursor.fetchone()[0]
    print(f"\n数据库统计:")
    print(f"  有ISBN的书籍: {with_isbn}")
    print(f"  有页数的书籍: {with_pages}")
    print(f"  有简介的书籍: {with_summary}")
    conn.close()
