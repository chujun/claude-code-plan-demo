"""MVP验证：存储10本书和作者信息到数据库"""
import sys
sys.path.insert(0, '/data/ai/claudecode/claude-code-plan-demo')

from db import init_db, insert_book, insert_author

# 手动构建的10本书籍数据（rank 1-10）
books_data = [
    {
        "rank": 1,
        "douban_id": "1007305",
        "title": "红楼梦",
        "book_url": "https://book.douban.com/subject/1007305/",
        "cover_url": "https://img1.doubanio.com/view/subject/s/public/s1070959.jpg",
        "rating": 9.7,
        "rating_count": 461212,
        "summary": "都云作者痴，谁解其中味？",
        "publisher": "人民文学出版社",
        "publish_date": "1996-12",
        "pages": "1606",
        "price": "59.70元",
        "isbn": "9787020002207",
        "author_name": "曹雪芹 Xueqin Cao",
        "author_url": "https://www.douban.com/personage/27487378/",
        "author": {
            "name": "曹雪芹 Xueqin Cao",
            "douban_url": "https://www.douban.com/personage/27487378/",
            "gender": "男",
            "birth_date": "1715年5月28日",
            "birthplace": "中国,江苏,南京",
        }
    },
    {
        "rank": 2,
        "douban_id": "4913064",
        "title": "活着",
        "book_url": "https://book.douban.com/subject/4913064/",
        "cover_url": "https://img9.doubanio.com/view/subject/s/public/s29869926.jpg",
        "rating": 9.4,
        "rating_count": 910851,
        "summary": "生的苦难与伟大",
        "publisher": "作家出版社",
        "publish_date": "2012-8",
        "price": "28.00元",
        "author_name": "余华",
        "author_url": "https://book.douban.com/author/1045935",
        "author": {
            "name": "余华",
            "douban_url": "https://www.douban.com/personage/1000001/",
            "gender": "男",
            "birth_date": "1960年4月3日",
            "birthplace": "中国,浙江,杭州",
        }
    },
    {
        "rank": 3,
        "douban_id": "24531956",
        "title": "哈利·波特",
        "book_url": "https://book.douban.com/subject/24531956/",
        "cover_url": "https://img9.doubanio.com/view/subject/s/public/s29101586.jpg",
        "rating": 9.7,
        "rating_count": 134261,
        "summary": "从9¾站台开始的旅程",
        "publisher": "人民文学出版社",
        "publish_date": "2008-12-1",
        "price": "498.00元",
        "translator": "苏农",
        "author_name": "J.K.罗琳",
        "author_url": "https://book.douban.com/author/0001026",
        "author": {
            "name": "J.K.罗琳",
            "douban_url": "https://www.douban.com/personage/0001026/",
            "gender": "女",
            "birth_date": "1965年7月31日",
            "birthplace": "英国,格洛斯特郡,雅芳河畔斯特拉特福",
        }
    },
    {
        "rank": 4,
        "douban_id": "4820710",
        "title": "1984",
        "book_url": "https://book.douban.com/subject/4820710/",
        "cover_url": "https://img1.doubanio.com/view/subject/s/public/s4371408.jpg",
        "rating": 9.4,
        "rating_count": 310179,
        "summary": "栗树荫下，我出卖你，你出卖我",
        "publisher": "北京十月文艺出版社",
        "publish_date": "2010-4-1",
        "price": "28.00",
        "translator": "刘绍铭",
        "author_name": "乔治·奥威尔",
        "author_url": "https://book.douban.com/author/1056938",
        "author": {
            "name": "乔治·奥威尔",
            "douban_url": "https://www.douban.com/personage/1056938/",
            "gender": "男",
            "birth_date": "1903年6月25日",
            "birthplace": "英属印度,比哈尔邦,马达蒂里",
        }
    },
    {
        "rank": 5,
        "douban_id": "6518605",
        "title": "三体全集 : 地球往事三部曲",
        "book_url": "https://book.douban.com/subject/6518605/",
        "cover_url": "https://img9.doubanio.com/view/subject/s/public/s28357056.jpg",
        "rating": 9.5,
        "rating_count": 214582,
        "summary": "地球往事三部曲",
        "publisher": "重庆出版社",
        "publish_date": "2012-1",
        "price": "168.00元",
        "author_name": "刘慈欣",
        "author_url": "https://book.douban.com/author/1084916",
        "author": {
            "name": "刘慈欣",
            "douban_url": "https://www.douban.com/personage/1084916/",
            "gender": "男",
            "birth_date": "1963年6月23日",
            "birthplace": "中国,河南,信阳",
        }
    },
    {
        "rank": 6,
        "douban_id": "6082808",
        "title": "百年孤独",
        "book_url": "https://book.douban.com/subject/6082808/",
        "cover_url": "https://img1.doubanio.com/view/subject/s/public/s27237850.jpg",
        "rating": 9.3,
        "rating_count": 471485,
        "summary": "魔幻现实主义文学代表作",
        "publisher": "南海出版公司",
        "publish_date": "2011-6",
        "price": "39.50元",
        "translator": "范晔",
        "author_name": "加西亚·马尔克斯",
        "author_url": "https://book.douban.com/author/105浪029",
        "author": {
            "name": "加西亚·马尔克斯",
            "douban_url": "https://www.douban.com/personage/105029/",
            "gender": "男",
            "birth_date": "1927年3月6日",
            "birthplace": "哥伦比亚,阿拉卡塔卡",
        }
    },
    {
        "rank": 7,
        "douban_id": "1068920",
        "title": "飘",
        "book_url": "https://book.douban.com/subject/1068920/",
        "cover_url": "https://img1.doubanio.com/view/subject/s/public/s1078958.jpg",
        "rating": 9.3,
        "rating_count": 227825,
        "summary": "革命时期的爱情，随风而逝",
        "publisher": "译林出版社",
        "publish_date": "2000-9",
        "price": "40.00元",
        "translator": "李美华",
        "author_name": "玛格丽特·米切尔",
        "author_url": "https://book.douban.com/author/1022450",
        "author": {
            "name": "玛格丽特·米切尔",
            "douban_url": "https://www.douban.com/personage/1022450/",
            "gender": "女",
            "birth_date": "1900年11月8日",
            "birthplace": "美国,佐治亚州,亚特兰大",
        }
    },
    {
        "rank": 8,
        "douban_id": "2035179",
        "title": "动物农场",
        "book_url": "https://book.douban.com/subject/2035179/",
        "cover_url": "https://img1.doubanio.com/view/subject/s/public/s2347590.jpg",
        "rating": 9.3,
        "rating_count": 179858,
        "summary": "太阳底下并无新事",
        "publisher": "上海译文出版社",
        "publish_date": "2007-3",
        "price": "10.00元",
        "translator": "荣如德",
        "author_name": "乔治·奥威尔",
        "author_url": "https://book.douban.com/author/1056938",
        "author": {
            "name": "乔治·奥威尔",
            "douban_url": "https://www.douban.com/personage/1056938/",
            "gender": "男",
            "birth_date": "1903年6月25日",
            "birthplace": "英属印度,比哈尔邦,马达蒂里",
        }
    },
    {
        "rank": 9,
        "douban_id": "27614904",
        "title": "房思琪的初恋乐园",
        "book_url": "https://book.douban.com/subject/27614904/",
        "cover_url": "https://img2.doubanio.com/view/subject/s/public/s29651121.jpg",
        "rating": 9.2,
        "rating_count": 420449,
        "summary": "向死而生的文学绝唱",
        "publisher": "北京联合出版公司",
        "publish_date": "2018-2",
        "price": "45.00元",
        "author_name": "林奕含",
        "author_url": "https://book.douban.com/author/27608474",
        "author": {
            "name": "林奕含",
            "douban_url": "https://www.douban.com/personage/27608474/",
            "gender": "女",
            "birth_date": "1991年3月11日",
            "birthplace": "中国,台湾,台南",
        }
    },
    {
        "rank": 10,
        "douban_id": "1019568",
        "title": "三国演义（全二册）",
        "book_url": "https://book.douban.com/subject/1019568/",
        "cover_url": "https://img3.doubanio.com/view/subject/s/public/s1024407.jpg",
        "rating": 9.3,
        "rating_count": 182395,
        "summary": "是非成败转头空",
        "publisher": "人民文学出版社",
        "publish_date": "1998-05",
        "price": "39.50元",
        "author_name": "罗贯中",
        "author_url": "https://book.douban.com/author/20015484",
        "author": {
            "name": "罗贯中",
            "douban_url": "https://www.douban.com/personage/20015484/",
            "gender": "男",
            "birth_date": "约1330年",
            "birthplace": "中国,山西,太原",
        }
    },
]

def main():
    init_db()
    print("数据库初始化完成")

    author_cache = {}  # 用于去重作者

    for book in books_data:
        # 处理作者信息
        author_data = book.pop('author')
        author_key = author_data['name']

        if author_key not in author_cache:
            author_id = insert_author(author_data)
            author_cache[author_key] = author_id
            print(f"作者: {author_data['name']} (ID: {author_id}, 出生地: {author_data.get('birthplace', 'N/A')})")
        else:
            author_id = author_cache[author_key]

        book['author_id'] = author_id

        # 插入书籍
        book_id = insert_book(book)
        print(f"书籍: {book['title']} (Rank: {book['rank']}, Author ID: {author_id}, Book ID: {book_id})")

    print(f"\n共存储 {len(books_data)} 本书, {len(author_cache)} 位作者")

    # 验证数据
    print("\n" + "="*80)
    print("数据验证:")
    print("="*80)

    conn = None
    try:
        from db import get_connection
        conn = get_connection()
        cursor = conn.cursor()

        print("\n【Books 表】")
        cursor.execute("SELECT id, rank, title, author_name, rating, publisher FROM books ORDER BY rank")
        for row in cursor.fetchall():
            print(f"  ID:{row[0]:2d} Rank:{str(row[1]):>3s} {str(row[2])[:20]:20s} Author:{str(row[3])[:15]:15s} Rating:{row[4]} Pub:{row[5][:15] if row[5] else 'N/A'}")

        print("\n【Authors 表】")
        cursor.execute("SELECT id, name, gender, birth_date, birthplace FROM authors")
        for row in cursor.fetchall():
            print(f"  ID:{row[0]:2d} {str(row[1])[:20]:20s} {str(row[2]):3s} {str(row[3])[:15]:15s} {str(row[4])[:20]:20s}")

        print("\n【统计】")
        cursor.execute("SELECT COUNT(*) FROM books")
        print(f"  书籍总数: {cursor.fetchone()[0]}")
        cursor.execute("SELECT COUNT(*) FROM authors")
        print(f"  作者总数: {cursor.fetchone()[0]}")

        conn.close()
    except Exception as e:
        print(f"验证查询出错: {e}")

if __name__ == '__main__':
    main()