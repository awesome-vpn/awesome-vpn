from . import tool
import re
from urllib.parse import urlparse, parse_qs
def parse(data):
    info = data[:]
    server_info = urlparse(info)
    if server_info.path:
        server_info = server_info._replace(netloc=server_info.netloc + server_info.path)
    _netloc = server_info.netloc.rsplit("@", 1)
    #_netloc = (tool.b64Decode(server_info.netloc)).decode().split("@")
    netquery = dict(
        (k, v if len(v) > 1 else v[0])
        for k, v in parse_qs(server_info.query).items()
    )
    node = {
        'tag': server_info.fragment or tool.genName()+'_tuic',
        'type': 'tuic',
        'server': re.sub(r"\[|\]", "", _netloc[1].rsplit(":", 1)[0]),
        'server_port': int(re.search(r'\d+', _netloc[1].rsplit(":", 1)[1]).group()),
        'uuid': _netloc[0].split(":")[0],
        'password': _netloc[0].split(":")[1] if len(_netloc[0].split(":")) > 1 else netquery.get('password', ''),
        'congestion_control': netquery.get('congestion_control', 'bbr'),
        'udp_relay_mode': netquery.get('udp_relay_mode'),
        'zero_rtt_handshake': False,
        'heartbeat': '10s',
        'tls': {
            'enabled': True,
            'alpn': (netquery.get('alpn') or "h3").strip('{}').split(','),
            'insecure': False
        }
    }
    if netquery.get('allow_insecure') == '1' :
        node['tls']['insecure'] = True
    if netquery.get('disable_sni') and netquery['disable_sni'] != '1':
        node['tls']['server_name'] = netquery.get('sni', netquery.get('peer', ''))
    if netquery.get('sni') or netquery.get('peer'):
        node['tls']['server_name'] = netquery.get('sni', netquery.get('peer', ''))
    return node
