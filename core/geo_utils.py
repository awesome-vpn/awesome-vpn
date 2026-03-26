import os
import socket
import threading
import requests
import maxminddb

COUNTRY_NAMES = {
    'US': ('美国', 'United States'), 'GB': ('英国', 'United Kingdom'),
    'JP': ('日本', 'Japan'), 'KR': ('韩国', 'South Korea'),
    'SG': ('新加坡', 'Singapore'), 'HK': ('香港', 'Hong Kong'),
    'TW': ('台湾', 'Taiwan'), 'DE': ('德国', 'Germany'),
    'FR': ('法国', 'France'), 'NL': ('荷兰', 'Netherlands'),
    'AU': ('澳大利亚', 'Australia'), 'CA': ('加拿大', 'Canada'),
    'RU': ('俄罗斯', 'Russia'), 'IN': ('印度', 'India'),
    'BR': ('巴西', 'Brazil'), 'IT': ('意大利', 'Italy'),
    'ES': ('西班牙', 'Spain'), 'CH': ('瑞士', 'Switzerland'),
    'SE': ('瑞典', 'Sweden'), 'NO': ('挪威', 'Norway'),
    'FI': ('芬兰', 'Finland'), 'DK': ('丹麦', 'Denmark'),
    'PL': ('波兰', 'Poland'), 'UA': ('乌克兰', 'Ukraine'),
    'IE': ('爱尔兰', 'Ireland'), 'AT': ('奥地利', 'Austria'),
    'BE': ('比利时', 'Belgium'), 'CZ': ('捷克', 'Czech Republic'),
    'RO': ('罗马尼亚', 'Romania'), 'PT': ('葡萄牙', 'Portugal'),
    'HU': ('匈牙利', 'Hungary'), 'GR': ('希腊', 'Greece'),
    'IL': ('以色列', 'Israel'), 'TR': ('土耳其', 'Turkey'),
    'MX': ('墨西哥', 'Mexico'), 'AR': ('阿根廷', 'Argentina'),
    'CL': ('智利', 'Chile'), 'CO': ('哥伦比亚', 'Colombia'),
    'MY': ('马来西亚', 'Malaysia'), 'TH': ('泰国', 'Thailand'),
    'VN': ('越南', 'Vietnam'), 'ID': ('印度尼西亚', 'Indonesia'),
    'PH': ('菲律宾', 'Philippines'), 'NZ': ('新西兰', 'New Zealand'),
    'ZA': ('南非', 'South Africa'), 'AE': ('阿联酋', 'United Arab Emirates'),
    'SA': ('沙特阿拉伯', 'Saudi Arabia'), 'EG': ('埃及', 'Egypt'),
    'NG': ('尼日利亚', 'Nigeria'), 'KE': ('肯尼亚', 'Kenya'),
}


class GeoUtils:
    def __init__(self, mmdb_path):
        self.mmdb_path = mmdb_path
        self.reader = None
        self._cache = {}       # host -> (country_zh, country_en, city_zh, city_en)
        self._lock = threading.Lock()
        self._init_reader()

    def _init_reader(self):
        if os.path.exists(self.mmdb_path):
            try:
                self.reader = maxminddb.open_database(self.mmdb_path)
                print(f"Using GeoLite2-City.mmdb at {self.mmdb_path}")
            except Exception as e:
                print(f"Error opening GeoLite2-City.mmdb: {e}")
                self.reader = None
        else:
            print(f"GeoLite2-City.mmdb not found at {self.mmdb_path}")

    def _resolve_to_ip(self, host):
        try:
            socket.inet_aton(host)
            return host
        except socket.error:
            pass
        try:
            return socket.gethostbyname(host)
        except Exception:
            return None

    def _fetch_geo_info(self, host):
        """Perform the actual geo lookup (no caching)."""
        ip = self._resolve_to_ip(host)
        if not ip:
            return "未知", "Unknown", "", ""

        if self.reader:
            try:
                result = self.reader.get(ip)
                if result:
                    country_zh = result.get('country', {}).get('names', {}).get('zh-CN', '')
                    country_en = result.get('country', {}).get('names', {}).get('en', '')
                    city_zh = result.get('city', {}).get('names', {}).get('zh-CN', '')
                    city_en = result.get('city', {}).get('names', {}).get('en', '')
                    if country_en:
                        return country_zh, country_en, city_zh, city_en
            except Exception:
                pass

        try:
            session = requests.Session()
            session.trust_env = False
            response = session.get(f"https://ipinfo.io/{ip}/json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                country_code = data.get('country', '')
                city = data.get('city', '')
                if country_code in COUNTRY_NAMES:
                    country_zh, country_en = COUNTRY_NAMES[country_code]
                    return country_zh, country_en, city, city
                return country_code, country_code, city, city
        except Exception:
            pass

        return "未知", "Unknown", "", ""

    def get_geo_info(self, host):
        """
        Get geo information for a host, with in-memory caching.
        Thread-safe: safe to call from multiple threads simultaneously.
        Returns: (country_zh, country_en, city_zh, city_en)
        """
        with self._lock:
            if host in self._cache:
                return self._cache[host]

        result = self._fetch_geo_info(host)

        with self._lock:
            self._cache[host] = result
        return result

    def format_node_name(self, host):
        country_zh, country_en, city_zh, city_en = self.get_geo_info(host)
        if city_zh and city_en:
            return f"{country_zh}/{city_zh}/{country_en}/{city_en}"
        return f"{country_zh}/{country_en}"

    def close(self):
        if self.reader:
            self.reader.close()
