import concurrent.futures
import json
import logging
import os
import platform
import random
import shutil
import socket
import struct
import subprocess
import tempfile
import threading
import time
from typing import Any

import requests

from core.dual_validator import detect_physical_interface

# Benchmark target: Google 204 response (requires functional proxy to reach)
TEST_URL = "https://www.google.com/generate_204"

# IP verification services (HTTPS, verifies outbound HTTPS relay)
IP_CHECK_URLS = [
    "https://ipinfo.io/ip",
    "https://api.ipify.org",
]

# DNS test: verify domestic domain resolution via proxy
DNS_TEST_DOMAINS = [
    ("www.baidu.com", "Baidu"),
    ("www.taobao.com", "Taobao"),
]

# Port allocation lock to prevent concurrency collisions
_port_lock = threading.Lock()
_allocated_ports: set[int] = set()


def _get_unique_port():
    """Allocate an available ephemeral port to prevent binding collisions."""
    with _port_lock:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        _allocated_ports.add(port)
        return port


class Validator:
    def __init__(self, sing_box_path=None, local_mode=False):
        if sing_box_path and os.path.exists(sing_box_path):
            self.sing_box_path = sing_box_path
        else:
            self.sing_box_path = self._find_sing_box()

        # local_mode=True: skip direct TCP checks (they fail behind GFW)
        self.local_mode = local_mode
        self.interface = detect_physical_interface() if self.local_mode else ""
        if self.interface:
            print(f"Validator: Binding to physical interface '{self.interface}' (bypassing TUN)")

        if self.sing_box_path and os.path.exists(self.sing_box_path):
            print(f"Validator: Using sing-box at {self.sing_box_path}")
        else:
            print("Validator: sing-box binary not found. Validation will be skipped.")

        mode_label = "local (skipping direct TCP checks)" if local_mode else "CI"
        print(f"Validator: Running in {mode_label} mode")

        self.logger = logging.getLogger("Validator")
        self.original_ip = self._get_original_ip()
        print(f"Validator: Original IP: {self.original_ip}")

    def _get_original_ip(self):
        """Retrieve real external IP of current host (bypassing proxies)."""
        for url in IP_CHECK_URLS:
            try:
                # Explicitly bypass proxies and disable environment proxy variables
                session = requests.Session()
                session.trust_env = False
                resp = session.get(url, timeout=5)
                if resp.status_code == 200:
                    ip = resp.text.strip()
                    if ip:
                        return ip
            except Exception:
                continue
        return None

    def _find_sing_box(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bin_dir = os.path.join(base_dir, "bin")

        system = platform.system().lower()
        machine = platform.machine().lower()
        if machine == "x86_64":
            machine = "amd64"
        elif machine == "aarch64":
            machine = "arm64"

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

        global_path = shutil.which("sing-box")
        if global_path:
            return global_path

        return None

    def tcp_ping(self, host, port, timeout=3):
        try:
            with socket.create_connection((host, int(port)), timeout=timeout):
                return True
        except Exception:
            return False

    def _wait_for_socks5_ready(self, port, timeout=3.0):
        """Poll until sing-box SOCKS5 port accepts connections (replaces sleep)."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                    return True
            except OSError:
                time.sleep(0.05)
        return False

    def check_udp_dns_via_socks5(self, listen_port, timeout=5):
        """Test UDP relay via SOCKS5 UDP ASSOCIATE.

        Constructs DNS query packet to 8.8.8.8:53.
        """
        try:
            # Establish SOCKS5 TCP connection for UDP ASSOCIATE
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect(("127.0.0.1", listen_port))

            # SOCKS5 handshake
            sock.sendall(b"\x05\x01\x00")  # ver 5, 1 auth method, no auth
            resp = sock.recv(2)
            if resp[0] != 0x05 or resp[1] != 0x00:
                sock.close()
                return False

            # UDP ASSOCIATE request
            sock.sendall(
                b"\x05\x03\x00\x01\x00\x00\x00\x00\x00\x00"
            )  # ver, UDP, rsv, ATYP, IP, port
            resp = sock.recv(10)
            if resp[0] != 0x05 or resp[1] != 0x00:
                sock.close()
                return False

            # Parse UDP relay address
            if resp[3] == 0x01:  # IPv4
                udp_addr = (socket.inet_ntoa(resp[4:8]), struct.unpack(">H", resp[8:10])[0])
            else:
                sock.close()
                return False

            sock.close()

            # Transmit DNS query through UDP relay
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.settimeout(timeout)

            # Construct SOCKS5 UDP header + DNS query
            dns_query = b"\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01"
            udp_packet = (
                b"\x00\x00\x00\x01\x01\x01\x01\x01\x00\x35" + dns_query
            )  # RSV, FRAG, ATYP, IP, port

            udp_sock.sendto(udp_packet, udp_addr)
            data, _ = udp_sock.recvfrom(1024)
            udp_sock.close()

            return len(data) > 0
        except Exception:
            return False

    def check_dns_via_proxy(self, listen_port, domain, timeout=5):
        """Verify domain resolution via SOCKS5 TCP DNS relay."""
        try:
            import socket

            # Connect to 8.8.8.8:53 via SOCKS5 proxy
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)

            # SOCKS5 handshake
            sock.connect(("127.0.0.1", listen_port))
            sock.sendall(b"\x05\x01\x00")
            resp = sock.recv(2)
            if resp[0] != 0x05 or resp[1] != 0x00:
                sock.close()
                return False

            # CONNECT to 8.8.8.8:53
            sock.sendall(b"\x05\x01\x00\x01\x08\x08\x08\x08\x00\x35")
            resp = sock.recv(10)
            if resp[0] != 0x05 or resp[1] != 0x00:
                sock.close()
                return False

            # Send DNS over TCP query
            query = self._build_dns_query(domain)
            sock.sendall(struct.pack(">H", len(query)) + query)

            resp_len = struct.unpack(">H", sock.recv(2))[0]
            resp = sock.recv(resp_len)
            sock.close()

            # Parse DNS response to extract IP
            ip = self._parse_dns_response(resp)
            return ip is not None
        except Exception:
            return False

    def _build_dns_query(self, domain):
        """Construct DNS A-record query payload."""
        parts = domain.split(".")
        qname = b"".join(bytes([len(p)]) + p.encode() for p in parts) + b"\x00"
        return (
            struct.pack(">HHHHHH", random.randint(1, 65535), 0x0100, 1, 0, 0, 0)
            + qname
            + b"\x00\x01\x00\x01"
        )

    def _parse_dns_response(self, data):
        """Parse DNS response payload and extract first A-record IP."""
        try:
            if len(data) < 12:
                return None
            ancount = struct.unpack(">H", data[6:8])[0]
            if ancount == 0:
                return None
            # Skip header and question section
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
                rtype = struct.unpack(">H", data[pos : pos + 2])[0]
                pos += 8  # type, class, ttl
                rdlen = struct.unpack(">H", data[pos : pos + 2])[0]
                pos += 2
                if rtype == 1 and rdlen == 4:  # A record
                    return socket.inet_ntoa(data[pos : pos + 4])
                pos += rdlen
            return None
        except Exception:
            return None

    def validate_nodes_parallel(self, nodes, timeout=5, max_workers=30):
        if not self.sing_box_path or not os.path.exists(self.sing_box_path):
            print(
                f"Warning: sing-box not available, skipping validation. All {len(nodes)} nodes will be kept."
            )
            return nodes

        valid_nodes = []
        print(f"Starting FINAL strict validation for {len(nodes)} nodes...")
        print("Criteria (concise, keep 2+4):")
        print("  2) google.com/generate_204 == 204 via proxy, latency < 1.0s")
        print("  4) hysteria2/tuic must have UDP support")
        print("  + China resistance score + 500ms hard filter + Top-N")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_node = {
                executor.submit(self.validate_node_final, node, timeout): node for node in nodes
            }
            for i, future in enumerate(concurrent.futures.as_completed(future_to_node)):
                node = future_to_node[future]
                try:
                    ok, latency_ms = future.result()
                    if ok:
                        # stash latency for ranking; not part of sing-box outbound spec, will be stripped on save
                        node["_latency_ms"] = latency_ms
                        valid_nodes.append(node)
                except Exception:
                    pass
                if (i + 1) % 50 == 0:
                    print(f"Validated {i + 1}/{len(nodes)}, {len(valid_nodes)} valid...")

        print(f"Complete: {len(valid_nodes)}/{len(nodes)} passed before ranking")
        return valid_nodes

    def validate_node_final(self, node, timeout=5):
        """
        Concise validation (keep 2+4):
        2) google.com/generate_204 == 204 via proxy, latency < 1.0s
        4) hysteria2/tuic UDP ASSOCIATE
        Returns (ok, latency_ms)
        """
        if not self.sing_box_path or not os.path.exists(self.sing_box_path):
            return True, 0.0

        server = node.get("server")
        port = node.get("server_port") or node.get("port")
        node_type = node.get("type", "").lower()

        # UDP protocols (QUIC-based) skip TCP ping since TCP connection to UDP port fails normally
        # In local mode, skip direct TCP ping as outbound connections may be intercepted by local firewalls
        UDP_PROTOCOLS = {"hysteria2", "hy2", "tuic"}
        if server and port and node_type not in UDP_PROTOCOLS and not self.local_mode:
            if not self.tcp_ping(server, port, timeout=2):
                return False, 0.0

        node_config = node.copy()
        keys_to_remove = [k for k in list(node_config.keys()) if k.startswith("_")]
        for k in keys_to_remove:
            del node_config[k]

        if "tag" not in node_config:
            node_config["tag"] = "proxy"

        listen_port = _get_unique_port()

        dns_config: dict[str, Any] = {
            "servers": [{"type": "udp", "tag": "dns-remote", "server": "8.8.8.8"}],
            "final": "dns-remote",
        }
        outbound_direct: dict[str, Any] = {"type": "direct", "tag": "direct"}

        if self.local_mode and self.interface:
            dns_config = {
                "servers": [
                    {
                        "type": "udp",
                        "tag": "dns-direct",
                        "server": "223.5.5.5",
                        "server_port": 53,
                        "detour": "direct",
                    },
                ],
                "final": "dns-direct",
                "strategy": "prefer_ipv4",
            }
            node_config["bind_interface"] = self.interface
            outbound_direct["bind_interface"] = self.interface

        test_config = {
            "log": {"level": "fatal", "timestamp": True},
            "dns": dns_config,
            "inbounds": [
                {
                    "type": "socks",
                    "tag": "socks-in",
                    "listen": "127.0.0.1",
                    "listen_port": listen_port,
                }
            ],
            "outbounds": [node_config, outbound_direct],
            "route": {
                "rules": [{"inbound": "socks-in", "outbound": node_config.get("tag", "proxy")}]
            },
        }

        proc = None
        tmp_config_path = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
                json.dump(test_config, tmp_file)
                tmp_config_path = tmp_file.name

            env = dict(os.environ)
            env["ENABLE_DEPRECATED_LEGACY_DNS_SERVERS"] = "true"
            cmd = [self.sing_box_path, "run", "-c", tmp_config_path]
            proc = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, env=env
            )

            # Poll until SOCKS5 port is accepting connections (much faster than fixed sleep)
            if not self._wait_for_socks5_ready(listen_port, timeout=3.0) or proc.poll() is not None:
                if proc.poll() is not None:
                    stderr_output = proc.stderr.read() if proc.stderr else ""
                    if stderr_output:
                        print(f"    sing-box failed: {stderr_output[:200]}")
                return False, 0.0

            proxies = {
                "http": f"socks5h://127.0.0.1:{listen_port}",
                "https": f"socks5h://127.0.0.1:{listen_port}",
            }

            # Verification: google.com/generate_204 returns 204 via proxy
            start = time.time()
            try:
                session = requests.Session()
                session.trust_env = False
                session.proxies.update(proxies)
                resp = session.get(TEST_URL, timeout=timeout)
                latency = time.time() - start
                max_lat = 4.0 if self.local_mode else 1.0
                if resp.status_code != 204 or latency >= max_lat:
                    return False, latency * 1000
            except Exception:
                return False, 0.0

            # Verification: UDP support (required for hysteria2 / tuic)
            if node_type in ["hysteria2", "hy2", "tuic"]:
                udp_ok = self.check_udp_dns_via_socks5(listen_port, timeout=3)
                if not udp_ok:
                    return False, latency * 1000

            return True, latency * 1000

        except Exception:
            return False, 0.0
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
            # Release allocated port only after process is terminated to avoid collision
            with _port_lock:
                _allocated_ports.discard(listen_port)

            if tmp_config_path and os.path.exists(tmp_config_path):
                try:
                    os.remove(tmp_config_path)
                except Exception:
                    pass


def quick_tcp_prescreen(nodes, max_workers=60, timeout=2):
    """P1: Fast TCP connectivity pre-screening (TCP nodes only).

    Quickly eliminates unreachable endpoints before launching sing-box processes.
    UDP nodes (hysteria2/tuic) skip this check and proceed to full validation.
    """
    import concurrent.futures

    # UDP protocol list: skip TCP pre-screening
    UDP_PROTOCOLS = {"hysteria2", "hy2", "tuic"}

    tcp_nodes = []  # Nodes requiring TCP pre-screen
    udp_nodes = []  # UDP protocol nodes passed through directly

    for node in nodes:
        node_type = node.get("type", "").lower()
        if node_type in UDP_PROTOCOLS:
            udp_nodes.append(node)  # UDP nodes enter full validation directly
        else:
            tcp_nodes.append(node)  # TCP nodes undergo pre-screening

    def tcp_check(node):
        server = node.get("server")
        port = node.get("server_port") or node.get("port")

        if not server or not port:
            return None

        try:
            with socket.create_connection((server, int(port)), timeout=timeout):
                return node
        except Exception:
            return None

    # Pre-screen TCP nodes only
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
                    print(
                        f"  TCP pre-screen: {i + 1}/{total_tcp} checked, {len(passed_tcp)} passed..."
                    )

    # Merge passed TCP nodes + skipped UDP nodes
    result = passed_tcp + udp_nodes
    print(
        f"  TCP pre-screen: {len(passed_tcp)}/{len(tcp_nodes)} TCP passed, {len(udp_nodes)} UDP skipped"
    )

    return result
