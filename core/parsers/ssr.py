import tool
def parse(data):
    info = data[6:]
    if not info or info.isspace():
        return None
    try:
        proxy_str = tool.b64Decode(info).decode('utf-8')
    except:
        proxy_str = info
    i = 0
    parts = proxy_str.split(':')
    if len(parts) == 5: #fuck
        i = 1
        next_part, _, proxy_str = proxy_str.partition('=')
        parts.append(proxy_str)
        for ssr_obfs in ['plain', 'http_simple', 'http_post', 'random_head', 'tls1.2_ticket_auth']:
            if ssr_obfs in parts[4]:
                parts[5] = parts[4].split(ssr_obfs)[-1]
                parts[4] = ssr_obfs
    node = {
        'tag':None,
        'type':'shadowsocksr',
        'server': parts[0],
        'server_port': int(parts[1]),
        'protocol': parts[2],
        'method': parts[3],
        'obfs': parts[4]
    }
    password_params = parts[5].split('/?')
    if i == 0:
        node['password'] = tool.b64Decode(password_params[0]).decode('utf-8')
        params = password_params[1].split('&')
    else: #fuck
        node['password'] = tool.b64Decode(password_params[0].split('remarks')[0]).decode('utf-8')
        params = password_params[-1].split(password_params[0].split('remarks')[0])[-1].split('&')
    pdict = {'obfsparam':'obfs_param','protoparam':'protocol_param','remarks':'tag'}
    for p in params:
        key_value = p.split('=')
        keyname = key_value[0]
        if keyname in pdict.keys():
            keyname = pdict[keyname]
            node[keyname] = tool.b64Decode(key_value[1]).decode('utf-8')
    node['tag'] = node['tag'] if node.get('tag') else tool.genName()+'_shadowsocksr'
    return node
