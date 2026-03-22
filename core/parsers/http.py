import tool,re
from urllib.parse import urlparse, parse_qs, unquote
def parse(data):
    info = data[:]
    server_info = urlparse(info)
    '''
    try:
        remark = (tool.b64Decode(server_info.netloc)).decode().rsplit("/#", 1)
    except UnicodeDecodeError:
        remark = (tool.b64Decode(server_info.netloc+server_info.path)).decode().rsplit("/#", 1)
    remark = unquote(remark[1]) if len(remark) > 1 else tool.genName() + '_http'
    _netloc = remark[0].rsplit("@", 1)
    '''
    netloc1 = dict(
        (k, v if len(v) > 1 else v[0])
        for k, v in parse_qs(server_info.netloc).items()
    )
    remark = server_info.fragment
    netloc = (tool.b64Decode(server_info.netloc.split('&')[0])).decode()
    if '@' in netloc:
        _netloc = netloc.rsplit("@", 1)
        server_port = _netloc[1]
    else:
       server_port = netloc
    node = {
        'tag': remark or tool.genName()+'_http',
        'type': 'http',
        'server': re.sub(r"\[|\]", "", server_port.rsplit(":", 1)[0]),
        'server_port': int(server_port.rsplit(":", 1)[1]),
        'tls': {
            'enabled': True,
            'insecure': True
        }
    }
    if netloc1.get('sni'):
        node['tls']['server_name'] = netloc1['sni']
    if '@' in netloc:
        node['username'] = _netloc[0].split(":")[0]
        node['password'] = _netloc[0].split(":")[1]
    return (node)
