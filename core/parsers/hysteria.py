import tool,re
from urllib.parse import urlparse, parse_qs, unquote

def parse(data):
    info = data[:]
    server_info = urlparse(info)
    netquery = dict(
        (k, v if len(v) > 1 else v[0])
        for k, v in parse_qs(server_info.query).items()
    )
    node = {
        'tag': unquote(server_info.fragment) or tool.genName()+'_hysteria',
        'type': 'hysteria',
        'server': re.sub(r"\[|\]", "", server_info.netloc.rsplit(":", 1)[0]),
        'server_port': int((server_info.netloc.rsplit(":", 1)[1]).split(",", 1)[0]), #fuck all
        'up_mbps': int(re.search(r'\d+', netquery.get('upmbps', '10')).group()),
        'down_mbps': int(re.search(r'\d+', netquery.get('downmbps', '100')).group()),
        'auth_str': netquery.get('auth', ''),
        'tls': {
            'enabled': True,
            'server_name': netquery.get('sni', netquery.get('peer', '')),
            'insecure': False
        }
    }
    if netquery.get('alpn'):
        node['tls']['alpn'] = netquery['alpn'].strip('{}').split(',')
    if netquery.get('insecure') == '1' or netquery.get('allowInsecure') == '1':
        node['tls']['insecure'] = True
    if netquery.get('obfs') and netquery['obfs'] != 'none':
        node['obfs'] = netquery.get('obfs')
    return node
