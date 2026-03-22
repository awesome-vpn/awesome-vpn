import os
import socket
import requests
import maxminddb

class GeoUtils:
    def __init__(self, mmdb_path):
        self.mmdb_path = mmdb_path
        self.reader = None
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
        """Resolve hostname to IP address"""
        try:
            socket.inet_aton(host)
            return host
        except socket.error:
            pass
        
        try:
            return socket.gethostbyname(host)
        except Exception as e:
            print(f"Error resolving {host}: {e}")
            return None
    
    def get_geo_info(self, host):
        """
        Get geo information for a host (IP or domain)
        Returns: (country_zh, country_en, city_zh, city_en)
        """
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
            except Exception as e:
                print(f"Error querying GeoLite2-City.mmdb: {e}")
        
        try:
            response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                country_code = data.get('country', '')
                city = data.get('city', '')
                country_names = {
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
                if country_code in country_names:
                    country_zh, country_en = country_names[country_code]
                    return country_zh, country_en, city, city
                return country_code, country_code, city, city
        except Exception as e:
            print(f"Error querying IP info API: {e}")
        
        return "未知", "Unknown", "", ""
    
    def format_node_name(self, host):
        """
        Format node name as "中文国家/英文国家/freeinternet" or "中文国家/中文城市/英文国家/英文城市/freeinternet"
        """
        country_zh, country_en, city_zh, city_en = self.get_geo_info(host)
        
        if city_zh and city_en:
            return f"{country_zh}/{city_zh}/{country_en}/{city_en}/freeinternet"
        else:
            return f"{country_zh}/{country_en}/freeinternet"
    
    def close(self):
        if self.reader:
            self.reader.close()
