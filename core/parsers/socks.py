import tool,re
from urllib.parse import urlparse,unquote
def parse(data):
    info = data[:]
    server_info = urlparse(info)
    if server_info.path:
        server_info = server_info._replace(netloc=server_info.netloc + server_info.path, path="")
    node = {
        'tag': unquote(server_info.fragment)  or tool.genName()+'_socks',
        'type': 'socks',
        "version": "5",
        'udp_over_tcp': {}
    }
    try:
        netloc = (tool.b64Decode(server_info.netloc)).decode()
    except:
        netloc = server_info.netloc
    if '@' in netloc:
        _netloc = netloc.split("@")
        node['server'] = re.sub(r"\[|\]", "", _netloc[1].rsplit(":", 1)[0])
        node['server_port'] = int(_netloc[1].rsplit(":", 1)[1])
        node['username'] = _netloc[0].split(":")[0]
        node['password'] = _netloc[0].split(":")[1]
    elif '@' in server_info.netloc:
        _netloc = server_info.netloc.split("@")
        node['server'] = re.sub(r"\[|\]", "", _netloc[1].rsplit(":", 1)[0])
        node['server_port'] = int(_netloc[1].rsplit(":", 1)[1])
        node['username'] = netloc.split(":")[0]
        node['password'] = netloc.split(":")[1]
    else:
        node['server'] = re.sub(r"\[|\]", "", netloc.rsplit(":", 1)[0])
        node['server_port'] = int(netloc.rsplit(":", 1)[1])
    return (node)