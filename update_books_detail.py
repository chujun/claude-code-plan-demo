"""更新书籍详情数据 - 修复P0和P2问题"""
import sys
sys.path.insert(0, '/data/ai/claudecode/claude-code-plan-demo')
from db import get_connection

# 所有10本书的详情数据
books_detail = [
    {
        "id": 1,
        "pages": "1606",
        "isbn": "9787020002207",
        "summary": "以贾、史、王、薛四大家族的兴衰为背景，以贾宝玉、林黛玉、薛宝钗的爱情婚姻故事为主线，刻画了以贾宝玉和金陵十二钗为中心的正邪两赋有情人的人性美和悲剧美。通过家族悲剧、女儿悲剧及主人公的人生悲剧，揭示出封建末世的危机。"
    },
    {
        "id": 2,
        "pages": "191",
        "isbn": "9787506365437",
        "summary": "《活着(新版)》讲述了农村人福贵悲惨的人生遭遇。福贵本是个阔少爷，可他嗜赌如命，终于赌光了家业，一贫如洗。他的父亲被他活活气死，母亲则在穷困中患了重病，福贵前去求药，却在途中被国民党抓去当壮丁。经过几番波折回到家里，才知道母亲早已去世，妻子家珍含辛茹苦地养大两个儿女。此后更加悲惨的命运一次又一次降临到福贵身上，他的妻子、儿女和孙子相继死去，最后只剩福贵和一头老牛相依为命，但老人依旧活着，仿佛比往日更加洒脱与坚强。"
    },
    {
        "id": 3,
        "translator": "苏农 / 马爱农 / 马爱新",
        "pages": "3104",
        "isbn": "9787020096695",
        "summary": "《哈利·波特(共7册)(精)》编著者J.K.罗琳。《哈利·波特(共7册)(精)》内容提要：2000年的一个深夜，在美国书店的烛光中，穿着黑斗篷，戴着小眼镜的店员开始销售哈利波特4英文版，从此哈利波特系列图书席卷全球，也是在这一年，简体中文版哈利波特系列图书通过人民文学出版社引进版权登陆中国，作者J.K.罗琳用一种简单的魔法游戏将魔幻的故事传递给了中国乃至全球的青少年读者，与此同时商业电影的改编更是将这部魔幻题材的小说推向了巅峰。"
    },
    {
        "id": 4,
        "translator": "刘绍铭",
        "pages": "304",
        "isbn": "9787530210291",
        "summary": "《1984》是一部杰出的政治寓言小说，也是一部幻想小说。作品刻画了人类在极权主义社会的生存状态，有若一个永不褪色的警示标签，警醒世人提防这种预想中的黑暗成为现实。历经几十年，其生命力益显强大，被誉为20世纪影响最为深远的文学经典之一。"
    },
    {
        "id": 5,
        "pages": "1285",
        "isbn": "9787229042066",
        "summary": "《地球往事·三体》文化大革命如火如荼进行的同时，军方探寻外星文明的绝秘计划红岸工程取得了突破性进展。但在按下发射键的那一刻，历经劫难的叶文洁没有意识到，她彻底改变了人类的命运。地球文明向宇宙发出的第一声啼鸣，以太阳为中心，以光速向宇宙深处飞驰……四光年外，三体文明正苦苦挣扎——三颗无规则运行的太阳主导下的百余次毁灭与重生逼迫他们逃离母星。而恰在此时，他们接收到了地球发来的信息。"
    },
    {
        "id": 6,
        "translator": "范晔",
        "pages": "360",
        "isbn": "9787544253994",
        "summary": "《百年孤独》是魔幻现实主义文学的代表作，描写了布恩迪亚家族七代人的传奇故事，以及加勒比海沿岸小镇马孔多的百年兴衰，反映了拉丁美洲一个世纪以来风云变幻的历史。作品融入神话传说、民间故事、宗教典故等神秘因素，巧妙地糅合了现实与虚幻，展现出一个瑰丽的想象世界，成为20世纪最重要的经典文学巨著之一。"
    },
    {
        "id": 7,
        "translator": "李美华",
        "pages": "1235",
        "isbn": "9787806570920",
        "summary": "小说中的故事发生在1861年美国南北战争前夕。生活在南方的少女郝思嘉从小深受南方文化传统的熏陶，可在她的血液里却流淌着野性的叛逆因素。随着战火的蔓廷和生活环境的恶化，郝思嘉的叛逆个性越来越丰满，越鲜明，在一系列的的挫折中她改造了自我，改变了个人甚至整个家族的命运，成为时代时势造就的新女性的形象。"
    },
    {
        "id": 8,
        "translator": "荣如德",
        "pages": "119",
        "isbn": "9787532741854",
        "summary": "《动物农场》是奥威尔最优秀的作品之一，是一则入木三分的反乌托的政治讽喻寓言。农场的一群动物成功地进行了一场革命，将压榨他们的人类东家赶出农场，建立起一个平等的动物社会。然而，动物领袖，那些聪明的猪们最终却篡夺了革命的果实，成为比人类东家更加独裁和极权的统治者。"
    },
    {
        "id": 9,
        "pages": "272",
        "isbn": "9787559614636",
        "summary": "令人心碎却无能为力的真实故事。向死而生的文学绝唱 打动万千读者的年度华语小说。李银河 戴锦华 骆以军 张悦然 詹宏志 蒋方舟 等多位学者作家社会名人郑重推荐。痛苦的际遇是如此难以分享，好险这个世界还有文学。小小的房思琪住在金碧辉煌的人生里，她的脸和她可以想象的将来一样漂亮。补习班语文名师李国华是同一栋高级住宅的邻居。崇拜文学的小房思琪同样崇拜饱读诗书的李老师。"
    },
    {
        "id": 10,
        "pages": "990",
        "isbn": "9787020008728",
        "summary": "《三国演义》又名《三国志演义》、《三国志通俗演义》，是我国小说史上最著名最杰出的长篇章回体历史小说。《三国演义》的作者是元末明初人罗贯中，由毛纶，毛宗岗父子批改。在其成书前，三国故事已经历了数百年的历史发展过程。在唐代，三国故事已广为流传，连儿童都很熟悉。随着市民文艺的发展，宋代的说话艺人，已有专门说三国故事的，当时称为说三分。"
    }
]

def main():
    conn = get_connection()
    cursor = conn.cursor()

    print("开始更新书籍详情数据...")
    print("="*80)

    for book in books_detail:
        book_id = book["id"]

        # 构建更新SQL
        update_fields = []
        values = []

        if "translator" in book and book["translator"]:
            update_fields.append("translator = ?")
            values.append(book["translator"])
        if "pages" in book and book["pages"]:
            update_fields.append("pages = ?")
            values.append(book["pages"])
        if "isbn" in book and book["isbn"]:
            update_fields.append("isbn = ?")
            values.append(book["isbn"])
        if "summary" in book and book["summary"]:
            update_fields.append("summary = ?")
            values.append(book["summary"])

        if update_fields:
            values.append(book_id)
            sql = f"UPDATE books SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(sql, values)

            # 获取书名用于显示
            cursor.execute("SELECT title FROM books WHERE id = ?", (book_id,))
            title = cursor.fetchone()[0]

            print(f"✓ ID:{book_id:2d} {title[:20]}")
            print(f"    translator: {book.get('translator', 'N/A')}")
            print(f"    pages: {book.get('pages', 'N/A')}")
            print(f"    isbn: {book.get('isbn', 'N/A')}")
            print(f"    summary: {book.get('summary', 'N/A')[:60]}...")
            print()

    conn.commit()
    conn.close()

    print("="*80)
    print("更新完成!")

if __name__ == '__main__':
    main()