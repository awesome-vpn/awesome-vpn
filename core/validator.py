import os
import json
import subprocess
import time
import tempfile
import concurrent.futures
import random
import sys
import logging
import requests
import platform
import shutil
import socket
import struct
import threading

# 测试目标：Google 生成 204 响应（必须通过代理才能访问）
TEST_URL = 'https://www.google.com/generate_204'

# IP检测服务
IP_CHECK_URLS = [
    'http://ipinfo.io/ip',
    'http://api.ipify.org',
]

# DNS 测试：验证通过代理解析国内域名
DNS_TEST_DOMAINS = [
    ('www.baidu.com', 'Baidu'),
    ('www.taobao.com', 'Taobao'),
]

# 端口分配锁，避免并发冲突
_port_lock = threading.Lock()
_allocated_ports = set()

def _get_unique_port():
    """让 OS 分配一个空闲端口，避免与 ephemeral 端口范围冲突"""
    with _port_lock:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            port = s.getsockname()[1]
        _allocated_ports.add(port)
        return port


class Validator:
    def __init__(self, sing_box_path=None):
        if sing_box_path and os.path.exists(sing_box_path):
            self.sing_box_path = sing_box_path
        else:
            self.sing_box_path = self._find_sing_box()
        
        if self.sing_box_path and os.path.exists(self.sing_box_path):
            print(f"Validator: Using sing-box at {self.sing_box_path}")
        else:
            print(f"Validator: sing-box binary not found. Validation will be skipped.")
        
        self.logger = logging.getLogger('Validator')
        self.original_ip = self._get_original_ip()
        print(f"Validator: Original IP (GitHub Actions): {self.original_ip}")

    def _get_original_ip(self):
        """获取当前机器的真实IP（不经过代理）"""
        for url in IP_CHECK_URLS:
            try:
                # 明确不使用代理，禁用环境变量代理设置
                session = requests.Session()
                session.trust_env = False
                resp = session.get(url, timeout=5)
                if resp.status_code == 200:
                    ip = resp.text.strip()
                    if ip:
                        return ip
            except:
                continue
        return None

    def _find_sing_box(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bin_dir = os.path.join(base_dir, 'bin')
        
        system = platform.system().lower()
        machine = platform.machine().lower()
        if machine == 'x86_64':
            machine = 'amd64'
        elif machine == 'aarch64':
            machine = 'arm64'
        
        possible_names = [
            f"sing-box-{system}-{machine}",
            "sing-box",
            f"sing-box-{system}-amd64",
            f"sing-box-{system}-arm64",
        ]
        
        for name in possible_names:
            path = os.path.join(bin_dir, name)
            if os.path.exists(path):
                return path
        
        global_path = shutil.which('sing-box')
        if global_path:
            return global_path
        
        return None

    def tcp_ping(self, host, port, timeout=3):
        try:
            with socket.create_connection((host, int(port)), timeout=timeout):
                return True
        except:
            return False

    def _wait_for_socks5_ready(self, port, timeout=3.0):
        """Poll until sing-box SOCKS5 port accepts connections (replaces sleep)."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with socket.create_connection(('127.0.0.1', port), timeout=0.1):
                    return True
            except OSError:
                time.sleep(0.05)
        return False

    def check_udp_dns_via_socks5(self, listen_port, timeout=5):
        """
        通过 SOCKS5 UDP ASSOCIATE 测试 UDP 转发
        构造 DNS 查询包测试 8.8.8.8:53
        """
        try:
            # 先建立 SOCKS5 TCP 连接做 UDP ASSOCIATE
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect(('127.0.0.1', listen_port))
            
            # SOCKS5 握手
            sock.sendall(b'\x05\x01\x00')  # ver 5, 1 auth method, no auth
            resp = sock.recv(2)
            if resp[0] != 0x05 or resp[1] != 0x00:
                sock.close()
                return False
            
            # UDP ASSOCIATE 请求
            sock.sendall(b'\x05\x03\x00\x01\x00\x00\x00\x00\x00\x00')  # ver, UDP, rsv, ATYP, IP, port
            resp = sock.recv(10)
            if resp[0] != 0x05 or resp[1] != 0x00:
                sock.close()
                return False
            
            # 解析 UDP relay 地址
            if resp[3] == 0x01:  # IPv4
                udp_addr = (socket.inet_ntoa(resp[4:8]), struct.unpack('>H', resp[8:10])[0])
            else:
                sock.close()
                return False
            
            sock.close()
            
            # 现在通过 UDP relay 发送 DNS 查询
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.settimeout(timeout)
            
            # 构造 SOCKS5 UDP 头部 + DNS 查询
            dns_query = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01'
            udp_packet = b'\x00\x00\x00\x01\x01\x01\x01\x01\x00\x35' + dns_query  # RSV, FRAG, ATYP, IP, port
            
            udp_sock.sendto(udp_packet, udp_addr)
            data, _ = udp_sock.recvfrom(1024)
            udp_sock.close()
            
            return len(data) > 0
        except:
            return False

    def check_dns_via_proxy(self, listen_port, domain, timeout=5):
        """
        通过 SOCKS5 代理的 TCP DNS 检查域名解析
        """
        try:
            import socket
            # 使用 SOCKS5 代理建立 TCP 连接到 8.8.8.8:53
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # SOCKS5 握手
            sock.connect(('127.0.0.1', listen_port))
            sock.sendall(b'\x05\x01\x00')
            resp = sock.recv(2)
            if resp[0] != 0x05 or resp[1] != 0x00:
                sock.close()
                return False
            
            # CONNECT 到 8.8.8.8:53
            sock.sendall(b'\x05\x01\x00\x01\x08\x08\x08\x08\x00\x35')
            resp = sock.recv(10)
            if resp[0] != 0x05 or resp[1] != 0x00:
                sock.close()
                return False
            
            # 发送 DNS over TCP 查询
            query = self._build_dns_query(domain)
            sock.sendall(struct.pack('>H', len(query)) + query)
            
            resp_len = struct.unpack('>H', sock.recv(2))[0]
            resp = sock.recv(resp_len)
            sock.close()
            
            # 解析 DNS 响应获取 IP
            ip = self._parse_dns_response(resp)
            return ip is not None
        except:
            return False

    def _build_dns_query(self, domain):
        """构造 DNS A 记录查询包"""
        parts = domain.split('.')
        qname = b''.join(bytes([len(p)]) + p.encode() for p in parts) + b'\x00'
        return struct.pack('>HHHHHH', random.randint(1, 65535), 0x0100, 1, 0, 0, 0) + qname + b'\x00\x01\x00\x01'

    def _parse_dns_response(self, data):
        """解析 DNS 响应获取第一个 A 记录 IP"""
        try:
            if len(data) < 12:
                return None
            ancount = struct.unpack('>H', data[6:8])[0]
            if ancount == 0:
                return None
            # 跳过 header 和 question
            pos = 12
            while pos < len(data) and data[pos] != 0:
                if data[pos] & 0xC0 == 0xC0:
                    pos += 2
                else:
                    pos += 1 + data[pos]
            pos += 5  # skip null, type, class
            # parse answer
            for _ in range(ancount):
                if pos >= len(data):
                    break
                if data[pos] & 0xC0 == 0xC0:
                    pos += 2
                else:
                    while pos < len(data) and data[pos] != 0:
                        pos += 1 + data[pos]
                    pos += 1
                rtype = struct.unpack('>H', data[pos:pos+2])[0]
                pos += 8  # type, class, ttl
                rdlen = struct.unpack('>H', data[pos:pos+2])[0]
                pos += 2
                if rtype == 1 and rdlen == 4:  # A record
                    return socket.inet_ntoa(data[pos:pos+4])
                pos += rdlen
            return None
        except:
            return None

    def validate_nodes_parallel(self, nodes, timeout=5, max_workers=50):
        if not self.sing_box_path or not os.path.exists(self.sing_box_path):
            print(f"Warning: sing-box not available, skipping validation. All {len(nodes)} nodes will be kept.")
            return nodes
        
        valid_nodes = []
        print(f"Starting FINAL strict validation for {len(nodes)} nodes...")
        print(f"Criteria:")
        print(f"  1) IP must change (≠ {self.original_ip})")
        print(f"  2) Can access google.com via proxy")
        print(f"  3) DNS works (TCP DNS via SOCKS5)")
        print(f"  4) hysteria2/tuic must have UDP support")
        print(f"  5) Latency < 3s")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_node = {executor.submit(self.validate_node_final, node, timeout): node for node in nodes}
            for i, future in enumerate(concurrent.futures.as_completed(future_to_node)):
                node = future_to_node[future]
                try:
                    if future.result():
                        valid_nodes.append(node)
                except Exception as exc:
                    pass
                if (i + 1) % 50 == 0:
                    print(f"Validated {i + 1}/{len(nodes)}, {len(valid_nodes)} valid...")
        
        print(f"Complete: {len(valid_nodes)}/{len(nodes)} passed")
        return valid_nodes

    def validate_node_final(self, node, timeout=5):
        """
        最终严格验证：
        1. TCP 连通性
        2. 出口 IP ≠ 原始 IP
        3. 能访问 google.com（最小最快的测试）
        4. DNS 解析正常（TCP DNS via SOCKS5）
        5. hysteria2/tuic 必须 UDP 通（SOCKS5 UDP ASSOCIATE）
        6. 延迟 < 3s
        """
        if not self.sing_box_path or not os.path.exists(self.sing_box_path):
            return True

        server = node.get('server')
        port = node.get('server_port') or node.get('port')
        node_type = node.get('type', '').lower()
        
        if server and port:
            if not self.tcp_ping(server, port, timeout=2):
                return False

        node_config = node.copy()
        keys_to_remove = [k for k in list(node_config.keys()) if k.startswith('_')]
        for k in keys_to_remove:
            del node_config[k]
        
        if "tag" not in node_config:
            node_config["tag"] = "proxy"

        listen_port = _get_unique_port()
        
        test_config = {
            "log": {
                "level": "fatal",
                "timestamp": True
            },
            "dns": {
                "servers": [
                    {"type": "udp", "tag": "dns-remote", "server": "8.8.8.8"}
                ],
                "final": "dns-remote"
            },
            "inbounds": [
                {
                    "type": "socks",
                    "tag": "socks-in",
                    "listen": "127.0.0.1",
                    "listen_port": listen_port
                }
            ],
            "outbounds": [
                node_config,
                {
                    "type": "direct",
                    "tag": "direct"
                }
            ],
            "route": {
                "rules": [
                    {
                        "inbound": "socks-in",
                        "outbound": node_config.get("tag", "proxy")
                    }
                ]
            }
        }
        
        proc = None
        tmp_config_path = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                json.dump(test_config, tmp_file)
                tmp_config_path = tmp_file.name
            
            cmd = [self.sing_box_path, 'run', '-c', tmp_config_path]
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

            # Poll until SOCKS5 port is accepting connections (much faster than fixed sleep)
            if not self._wait_for_socks5_ready(listen_port, timeout=3.0) or proc.poll() is not None:
                if proc.poll() is not None:
                    stderr_output = proc.stderr.read() if proc.stderr else ""
                    if stderr_output:
                        print(f"    sing-box failed: {stderr_output[:200]}")
                return False
            
            proxies = {
                'http': f'socks5://127.0.0.1:{listen_port}',
                'https': f'socks5://127.0.0.1:{listen_port}'
            }
            
            # === 验证 1: 出口IP必须变化 ===
            ip_changed = False
            proxy_ip = None
            for ip_url in IP_CHECK_URLS:
                try:
                    # 强制使用 SOCKS5 代理，禁用环境变量
                    session = requests.Session()
                    session.trust_env = False
                    session.proxies.update(proxies)
                    resp = session.get(ip_url, timeout=timeout)
                    if resp.status_code == 200:
                        proxy_ip = resp.text.strip()
                        if proxy_ip and proxy_ip != self.original_ip:
                            ip_changed = True
                            break
                except:
                    continue

            if not ip_changed:
                return False

            # === 验证 2: 访问 google.com/generate_204 返回 204 ===
            start = time.time()
            try:
                session = requests.Session()
                session.trust_env = False
                session.proxies.update(proxies)
                resp = session.get(TEST_URL, timeout=timeout)
                latency = time.time() - start
                if resp.status_code != 204 or latency >= 3:
                    return False
            except:
                return False
            
            # === 验证 3: DNS 解析正常（通过 SOCKS5 TCP DNS）===
            dns_works = False
            for domain, name in DNS_TEST_DOMAINS:
                if self.check_dns_via_proxy(listen_port, domain, timeout=3):
                    dns_works = True
                    break
            
            if not dns_works:
                return False
            
            # === 验证 4: UDP 支持（hysteria2/tuic 必须）===
            if node_type in ['hysteria2', 'hy2', 'tuic']:
                udp_ok = self.check_udp_dns_via_socks5(listen_port, timeout=3)
                if not udp_ok:
                    return False
            
            return True
                
        except Exception as e:
            return False
        finally:
            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    try:
                        proc.wait(timeout=1)
                    except Exception:
                        pass
            # 进程已终止后再释放端口，避免其他线程拿到仍被占用的端口
            with _port_lock:
                _allocated_ports.discard(listen_port)

            if tmp_config_path and os.path.exists(tmp_config_path):
                try:
                    os.remove(tmp_config_path)
                except:
                    pass


def quick_tcp_prescreen(nodes, max_workers=100, timeout=2):
    """
    P1: 快速 TCP 连通性预筛选（仅对 TCP 协议节点）
    在 sing-box 验证前快速排除不通的节点，大幅缩短总验证时间

    注意：UDP 协议节点（hysteria2/tuic）跳过 TCP 预筛选，直接进入完整验证
    """
    import concurrent.futures

    # UDP 协议列表 - 这些节点跳过 TCP 预筛选
    UDP_PROTOCOLS = {'hysteria2', 'hy2', 'tuic'}

    tcp_nodes = []  # 需要 TCP 预筛选的节点
    udp_nodes = []  # UDP 协议节点，直接保留

    for node in nodes:
        node_type = node.get('type', '').lower()
        if node_type in UDP_PROTOCOLS:
            udp_nodes.append(node)  # UDP 节点直接进入完整验证
        else:
            tcp_nodes.append(node)   # TCP 节点做预筛选

    def tcp_check(node):
        server = node.get('server')
        port = node.get('server_port') or node.get('port')

        if not server or not port:
            return None

        try:
            with socket.create_connection((server, int(port)), timeout=timeout):
                return node
        except:
            return None

    # 只对 TCP 节点进行预筛选
    passed_tcp = []
    total_tcp = len(tcp_nodes)

    if total_tcp > 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_node = {executor.submit(tcp_check, node): node for node in tcp_nodes}

            for i, future in enumerate(concurrent.futures.as_completed(future_to_node)):
                result = future.result()
                if result:
                    passed_tcp.append(result)

                if (i + 1) % 100 == 0 or (i + 1) == total_tcp:
                    print(f"  TCP pre-screen: {i + 1}/{total_tcp} checked, {len(passed_tcp)} passed...")

    # 合并：通过 TCP 预筛选的节点 + 跳过的 UDP 节点
    result = passed_tcp + udp_nodes
    print(f"  TCP pre-screen: {len(passed_tcp)}/{len(tcp_nodes)} TCP passed, {len(udp_nodes)} UDP skipped")

    return result
