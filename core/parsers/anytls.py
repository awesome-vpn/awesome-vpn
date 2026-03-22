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
        'tag': unquote(server_info.fragment) or tool.genName()+'_anytls',
        'type': 'anytls',
        'server': re.sub(r"\[|\]", "", server_info.netloc.split("@")[-1].rsplit(":", 1)[0]),
        'server_port': int((server_info.netloc.rsplit(":", 1)[1]).split(",", 1)[0]), #fuck all
        'password': netquery['auth'] if netquery.get('auth') else server_info.netloc.split("@")[0].rsplit(":", 1)[-1],
        'tls': {
            'enabled': True,
            'server_name': netquery.get('sni', netquery.get('peer', '')),
            'insecure': False
        }
    }
    if netquery.get('idleSessionCheckInterval'):
        node['idle_session_check_interval'] = netquery['idleSessionCheckInterval']+'s'
    if netquery.get('idleSessionTimeout'):
        node['idle_session_timeout'] = netquery['idleSessionTimeout']+'s'
    if netquery.get('minIdleSession'):
        node['min_idle_session'] = int(netquery['minIdleSession'])
    if netquery.get('fp'):
        node['tls']['utls'] = {
            'enabled': True,
            'fingerprint': netquery.get('fp')
        }
    if netquery.get('alpn'):
        node['tls']['alpn'] = netquery['alpn'].strip('{}').split(',')
    if netquery.get('insecure') == '1' or netquery.get('allowInsecure') == '1':
        node['tls']['insecure'] = True
    return node
