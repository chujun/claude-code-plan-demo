"""地理编码模块：将作者出生地转换为经纬度"""

import logging
import time

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from config import NOMINATIM_USER_AGENT, NOMINATIM_DELAY, COUNTRY_TO_CONTINENT, CONTINENT_MAPPING

logger = logging.getLogger(__name__)

_geolocator = None


def _get_geolocator():
    """获取 Nominatim 地理编码器单例"""
    global _geolocator
    if _geolocator is None:
        _geolocator = Nominatim(user_agent=NOMINATIM_USER_AGENT, timeout=10)
    return _geolocator


def geocode_location(location_text):
    """
    将地名转换为经纬度和大洲/国家信息。

    返回:
        dict: {"latitude": float, "longitude": float, "continent": str, "country": str}
        如果失败返回 None
    """
    if not location_text or not location_text.strip():
        return None

    location_text = location_text.strip()
    geolocator = _get_geolocator()

    # 遵守 Nominatim 请求频率限制
    time.sleep(NOMINATIM_DELAY)

    try:
        location = geolocator.geocode(location_text, language="zh", addressdetails=True)
        if location is None:
            # 尝试简化地名后重试（去掉省/市等后缀）
            simplified = _simplify_location(location_text)
            if simplified != location_text:
                time.sleep(NOMINATIM_DELAY)
                location = geolocator.geocode(simplified, language="zh", addressdetails=True)

        if location is None:
            logger.warning(f"无法地理编码: {location_text}")
            return None

        result = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "continent": None,
            "country": None,
        }

        # 从地址详情中提取国家
        address = location.raw.get("address", {})
        country = address.get("country", "")
        country_code = address.get("country_code", "")

        if country:
            result["country"] = country
            # 从映射中获取大洲
            continent = _get_continent(country, country_code)
            if continent:
                result["continent"] = continent

        # 如果 Nominatim 未返回国家，尝试从配置映射中获取
        if not result["country"]:
            for key, (continent, country_name) in CONTINENT_MAPPING.items():
                if key in location_text:
                    result["continent"] = continent
                    result["country"] = country_name
                    break

        logger.info(f"地理编码成功: {location_text} -> ({result['latitude']}, {result['longitude']}), "
                     f"国家: {result['country']}, 大洲: {result['continent']}")
        return result

    except GeocoderTimedOut:
        logger.warning(f"地理编码超时: {location_text}")
        return None
    except GeocoderServiceError as e:
        logger.error(f"地理编码服务错误: {location_text}, 错误: {e}")
        return None
    except Exception as e:
        logger.error(f"地理编码异常: {location_text}, 错误: {e}")
        return None


def _simplify_location(location_text):
    """简化地名，去除省/市/县等后缀"""
    # 去掉"省"、"市"、"县"、"区"等后缀，保留核心地名
    import re
    simplified = re.sub(r"[省市县区]$", "", location_text)
    return simplified if simplified else location_text


def _get_continent(country, country_code=""):
    """根据国家名获取大洲"""
    # 先查英文映射
    if country in COUNTRY_TO_CONTINENT:
        return COUNTRY_TO_CONTINENT[country]

    # 再查中文映射
    for key, (continent, _) in CONTINENT_MAPPING.items():
        if key == country:
            return continent

    # 通过国家代码粗略判断
    continent_by_code = {
        "cn": "亚洲", "jp": "亚洲", "kr": "亚洲", "in": "亚洲", "tr": "亚洲", "il": "亚洲",
        "us": "北美洲", "ca": "北美洲", "mx": "北美洲",
        "gb": "欧洲", "fr": "欧洲", "de": "欧洲", "ru": "欧洲", "it": "欧洲", "es": "欧洲",
        "at": "欧洲", "ch": "欧洲", "pl": "欧洲", "cz": "欧洲", "ie": "欧洲",
        "no": "欧洲", "dk": "欧洲", "se": "欧洲", "nl": "欧洲", "be": "欧洲", "pt": "欧洲",
        "gr": "欧洲",
        "br": "南美洲", "ar": "南美洲", "co": "南美洲", "cl": "南美洲",
        "au": "大洋洲", "nz": "大洋洲",
        "eg": "非洲", "za": "非洲", "ng": "非洲",
    }
    if country_code.lower() in continent_by_code:
        return continent_by_code[country_code.lower()]

    return None
