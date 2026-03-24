import tool,re
from urllib.parse import urlparse, parse_qs, unquote
def parse(data):
    info = data[:]
    server_info = urlparse(info)
    netquery = dict(
        (k, v.replace(' ', '+') if len(v) > 1 else v[0].replace(' ', '+'))
        for k, v in parse_qs(server_info.query).items()
    )
    node = {
        'tag': unquote(server_info.fragment) or tool.genName()+'_wireguard',
        'type': 'wireguard',
        'private_key': netquery.get('privateKey') or unquote(server_info.netloc.rsplit("@", 1)[0]),
        'peers': []
    }
    peer_info = {
        'address': re.sub(r"\[|\]", "", server_info.netloc.rsplit("@", 1)[-1].rsplit(":", 1)[0]),
        'port': int(server_info.netloc.rsplit("@", 1)[-1].rsplit(":", 1)[1]),
        'public_key': netquery.get('publicKey') or netquery.get('publickey'),
        'allowed_ips': [
            "0.0.0.0/0"
        ],
        'persistent_keepalive_interval': 30
    }
    node['peers'].append(peer_info)
    if netquery.get('mtu'):
        node['mtu'] = int(netquery['mtu'])
    if netquery.get('reserved'):
        reserved_value = netquery.get('reserved')
        node['peers'][0]['reserved'] = [int(val) for val in reserved_value.split(",")] if ',' in reserved_value else reserved_value
    ip_value = netquery.get('ip') or netquery.get('address')
    if ',' in ip_value:
        ipv4_value, ipv6_value = ip_value.split(",", 1)
        ipv4_value = ipv4_value + "/32" if '/' not in ipv4_value else ipv4_value
        ipv6_value = ipv6_value + "/128" if '/' not in ipv6_value else ipv6_value
        node['address'] = [ipv4_value, ipv6_value]
    else:
        ipv4_value = ip_value + "/32" if '/' not in ip_value else ip_value
        node['address'] = [ipv4_value]
    if netquery.get('presharedKey'):
        node['peers'][0]['pre_shared_key'] = netquery['presharedKey']
    return (node)
