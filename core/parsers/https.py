import tool,re
from urllib.parse import urlparse,unquote
def parse(data):
    info = data[:]
    server_info = urlparse(info)
    try:
        remark = tool.b64Decode(server_info.netloc+server_info.path).decode().rsplit("/#", 1)
    except UnicodeDecodeError:
        remark = (server_info.netloc).rsplit("/#", 1)
    _netloc = remark[0].rsplit("@", 1)
    node = {
        'tag': unquote(remark[1]) if len(remark) > 1 else tool.genName() + '_http',
        'type': 'http',
        'server': re.sub(r"\[|\]", "", _netloc[-1].rsplit(":", 1)[0]),
        'server_port': int(_netloc[-1].rsplit(":", 1)[1]),
        'tls': {
            'enabled': True,
            'insecure': True
        }
    }
    if remark[0].count("@") == 2:
        node ['username'] = _netloc[0].split(":")[0]
        node ['password'] = _netloc[0].split(":")[1]
    return (node)
