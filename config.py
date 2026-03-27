"""豆瓣 Top250 书籍爬虫配置"""

import os

# 数据库
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "douban_books.db")

# 豆瓣 Top250 URL
TOP250_BASE_URL = "https://book.douban.com/top250"
DOUBAN_BASE_URL = "https://book.douban.com"

# 请求配置
REQUEST_DELAY_MIN = 3  # 最小请求间隔（秒）
REQUEST_DELAY_MAX = 5  # 最大请求间隔（秒）
MAX_RETRIES = 3        # 最大重试次数
RETRY_BACKOFF = 2      # 重试退避倍数

# Nominatim 地理编码
NOMINATIM_USER_AGENT = "douban-books-scraper/1.0"
NOMINATIM_DELAY = 1.1  # Nominatim 请求间隔（秒），略大于1秒

# User-Agent 列表
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# 地名到大洲/国家映射（用于补充 Nominatim 无法直接提供的大洲信息）
CONTINENT_MAPPING = {
    "中国": ("亚洲", "中国"),
    "China": ("亚洲", "中国"),
    "日本": ("亚洲", "日本"),
    "Japan": ("亚洲", "日本"),
    "韩国": ("亚洲", "韩国"),
    "印度": ("亚洲", "印度"),
    "India": ("亚洲", "印度"),
    "美国": ("北美洲", "美国"),
    "United States": ("北美洲", "美国"),
    "USA": ("北美洲", "美国"),
    "英国": ("欧洲", "英国"),
    "United Kingdom": ("欧洲", "英国"),
    "法国": ("欧洲", "法国"),
    "France": ("欧洲", "法国"),
    "德国": ("欧洲", "德国"),
    "Germany": ("欧洲", "德国"),
    "俄罗斯": ("欧洲", "俄罗斯"),
    "Russia": ("欧洲", "俄罗斯"),
    "意大利": ("欧洲", "意大利"),
    "Italy": ("欧洲", "意大利"),
    "西班牙": ("欧洲", "西班牙"),
    "Spain": ("欧洲", "西班牙"),
    "巴西": ("南美洲", "巴西"),
    "Brazil": ("南美洲", "巴西"),
    "澳大利亚": ("大洋洲", "澳大利亚"),
    "Australia": ("大洋洲", "澳大利亚"),
    "加拿大": ("北美洲", "加拿大"),
    "Canada": ("北美洲", "加拿大"),
    "墨西哥": ("北美洲", "墨西哥"),
    "阿根廷": ("南美洲", "阿根廷"),
    "Argentina": ("南美洲", "阿根廷"),
    "哥伦比亚": ("南美洲", "哥伦比亚"),
    "Colombia": ("南美洲", "哥伦比亚"),
    "智利": ("南美洲", "智利"),
    "Chile": ("南美洲", "智利"),
    "奥地利": ("欧洲", "奥地利"),
    "Austria": ("欧洲", "奥地利"),
    "瑞士": ("欧洲", "瑞士"),
    "波兰": ("欧洲", "波兰"),
    "捷克": ("欧洲", "捷克"),
    "爱尔兰": ("欧洲", "爱尔兰"),
    "Ireland": ("欧洲", "爱尔兰"),
    "挪威": ("欧洲", "挪威"),
    "丹麦": ("欧洲", "丹麦"),
    "瑞典": ("欧洲", "瑞典"),
    "荷兰": ("欧洲", "荷兰"),
    "比利时": ("欧洲", "比利时"),
    "葡萄牙": ("欧洲", "葡萄牙"),
    "希腊": ("欧洲", "希腊"),
    "土耳其": ("亚洲", "土耳其"),
    "以色列": ("亚洲", "以色列"),
    "埃及": ("非洲", "埃及"),
    "南非": ("非洲", "南非"),
    "尼日利亚": ("非洲", "尼日利亚"),
}

# 国家到大洲映射（英文，用于 Nominatim 返回结果的解析）
COUNTRY_TO_CONTINENT = {
    "China": "亚洲",
    "Japan": "亚洲",
    "South Korea": "亚洲",
    "India": "亚洲",
    "Turkey": "亚洲",
    "Israel": "亚洲",
    "United States": "北美洲",
    "Canada": "北美洲",
    "Mexico": "北美洲",
    "United Kingdom": "欧洲",
    "France": "欧洲",
    "Germany": "欧洲",
    "Russia": "欧洲",
    "Italy": "欧洲",
    "Spain": "欧洲",
    "Austria": "欧洲",
    "Switzerland": "欧洲",
    "Poland": "欧洲",
    "Czech Republic": "欧洲",
    "Czechia": "欧洲",
    "Ireland": "欧洲",
    "Norway": "欧洲",
    "Denmark": "欧洲",
    "Sweden": "欧洲",
    "Netherlands": "欧洲",
    "Belgium": "欧洲",
    "Portugal": "欧洲",
    "Greece": "欧洲",
    "Brazil": "南美洲",
    "Argentina": "南美洲",
    "Colombia": "南美洲",
    "Chile": "南美洲",
    "Australia": "大洋洲",
    "New Zealand": "大洋洲",
    "Egypt": "非洲",
    "South Africa": "非洲",
    "Nigeria": "非洲",
}
