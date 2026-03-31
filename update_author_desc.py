"""更新作者描述信息"""
import sys
sys.path.insert(0, '/data/ai/claudecode/claude-code-plan-demo')
from db import get_connection

# 已知的作者描述信息
author_descriptions = {
    1: "曹雪芹（约1715—约1763），清代满族小说家，内务府正白旗旗鼓佐领人。名沾，字梦阮，雪芹是其号，又号芹圃、芹溪。长篇小说《红楼梦》的作者。",
    2: "余华（1960年4月3日—），中国当代作家，主要作品有《活着》《许三观卖血记》《兄弟》等。其作品被翻译成多种语言，在国际文坛有重要影响。",
    3: "J.K.罗琳（J.K. Rowling），1965年7月31日出生于英国格洛斯特郡，英国作家，代表作《哈利·波特》系列，该系列已被翻译成80种语言，销量超过5亿册。",
    4: "乔治·奥威尔（George Orwell，1903年6月25日—1950年1月21日），英国作家、记者和社会评论家，代表作《动物农场》和《1984》。",
    5: "刘慈欣（1963年6月23日—），中国科幻作家，代表作《三体》三部曲，被誉为中国科幻文学的里程碑。",
    6: "加西亚·马尔克斯（Gabriel García Márquez，1927年3月6日—2014年4月17日），哥伦比亚作家，魔幻现实主义文学的代表人物，1982年诺贝尔文学奖获得者。",
    7: "玛格丽特·米切尔（Margaret Mitchell，1900年11月8日—1949年8月16日），美国作家，唯一出版的长篇小说《飘》成为美国文学经典。",
    8: "林奕含（1991年3月11日—2017年4月27日），台湾作家，著有《房思琪的初恋乐园》，作品深刻探讨性侵与家庭暴力议题。",
    9: "罗贯中（约1330年—约1400年），元末明初小说家，名本，字贯中，号湖海散人，著有《三国演义》《水浒传》等，其中《三国演义》是中国古代四大名著之一。",
}

def main():
    conn = get_connection()
    cursor = conn.cursor()

    print("更新作者描述信息...")
    print("="*80)

    for auth_id, description in author_descriptions.items():
        cursor.execute(
            "UPDATE authors SET description = ? WHERE id = ?",
            (description, auth_id)
        )
        # 获取作者名用于显示
        cursor.execute("SELECT name FROM authors WHERE id = ?", (auth_id,))
        name = cursor.fetchone()[0]
        print(f"✅ ID:{auth_id:2d} {name[:15]:<15}")
        print(f"   描述: {description[:60]}...")
        print()

    conn.commit()
    conn.close()

    print("="*80)
    print("更新完成!")

if __name__ == '__main__':
    main()