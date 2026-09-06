"""Dual-Engine Node Validator supporting both Sing-box and Mihomo (Clash.Meta).

Engineered to bypass virtual network card (TUN) interference from Clash Verge
by binding directly to the underlying physical network interface on macOS/Linux.
"""

import concurrent.futures
import json
import logging
import os
import shutil
import socket
import subprocess
import tempfile
import threading
import time
from typing import Any

import requests
import yaml

from core.converters.clash import to_clash_proxies

logger = logging.getLogger(__name__)

TEST_URL = "https://www.google.com/generate_204"

_port_lock = threading.Lock()
_allocated_ports: set[int] = set()


def get_free_port() -> int:
    """Allocate a unique local TCP port."""
    with _port_lock:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = int(s.getsockname()[1])
        _allocated_ports.add(port)
        return port


def release_port(port: int) -> None:
    with _port_lock:
        _allocated_ports.discard(port)


def wait_for_port(port: int, timeout: float = 3.0) -> bool:
    """Poll until a local port is open and accepting TCP connections."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                if s.connect_ex(("127.0.0.1", port)) == 0:
                    return True
        except Exception:
            pass
        time.sleep(0.04)
    return False


def detect_physical_interface() -> str:
    """
    Detect the default physical network interface (e.g. en0, en1, eth0)
    to bypass TUN virtual adapters (such as utun0..utun6 from Clash Verge).
    """
    # 1. macOS route get default
    try:
        route_bin = shutil.which("route") or "/sbin/route"
        res = subprocess.run(
            [route_bin, "-n", "get", "default"], capture_output=True, text=True, check=True
        )  # nosec B607
        for line in res.stdout.splitlines():
            if "interface:" in line:
                iface = line.split("interface:")[1].strip()
                if not iface.startswith("utun"):
                    return iface
    except Exception:
        pass

    # 2. Linux ip route get 1.1.1.1
    try:
        ip_bin = shutil.which("ip") or "/sbin/ip"
        res = subprocess.run(
            [ip_bin, "route", "get", "1.1.1.1"], capture_output=True, text=True, check=True
        )  # nosec B607
        parts = res.stdout.split()
        if "dev" in parts:
            dev_idx = parts.index("dev") + 1
            if dev_idx < len(parts) and not parts[dev_idx].startswith("utun"):
                return parts[dev_idx]
    except Exception:
        pass

    return "en0"


class DualValidator:
    """Validates nodes symmetrically against Sing-box and Mihomo."""

    def __init__(
        self,
        sing_box_bin: str | None = None,
        mihomo_bin: str | None = None,
        interface: str | None = None,
        timeout: float = 5.0,
    ):
        self.interface = interface or detect_physical_interface()
        self.timeout = timeout
        self.sing_box_bin = sing_box_bin or self._find_singbox()
        self.mihomo_bin = mihomo_bin or self._find_mihomo()

        logger.info(
            f"DualValidator initialized on physical interface '{self.interface}' (bypassing TUN)."
        )
        if self.sing_box_bin:
            logger.info(f"  Sing-box Binary: {self.sing_box_bin}")
        if self.mihomo_bin:
            logger.info(f"  Mihomo Binary:   {self.mihomo_bin}")

    def _find_singbox(self) -> str | None:
        if shutil.which("sing-box"):
            return shutil.which("sing-box")
        candidates = [
            "/opt/homebrew/bin/sing-box",
            "/usr/local/bin/sing-box",
            os.path.abspath("bin/sing-box-darwin-arm64"),
            os.path.abspath("bin/sing-box-linux-amd64"),
        ]
        for p in candidates:
            if os.path.isfile(p) and os.access(p, os.X_OK):
                return p
        return None

    def _find_mihomo(self) -> str | None:
        for name in ("mihomo", "clash-meta", "clash"):
            found = shutil.which(name)
            if found:
                return found
        candidates = [
            "/Applications/Clash Verge.app/Contents/MacOS/verge-mihomo",
            "/Applications/Clash Verge.app/Contents/MacOS/verge-mihomo-alpha",
            "/Applications/Clash Verge Rev.app/Contents/MacOS/verge-mihomo",
            "/opt/homebrew/bin/mihomo",
            "/usr/local/bin/mihomo",
        ]
        for p in candidates:
            if os.path.isfile(p) and os.access(p, os.X_OK):
                return p
        return None

    def test_with_singbox(self, node: dict[str, Any]) -> tuple[bool, float, str]:
        """Test a node using Sing-box, bound to physical interface with clean direct DNS."""
        if not self.sing_box_bin:
            return False, 0.0, "sing-box binary not found"

        listen_port = get_free_port()
        node_copy = dict(node)
        node_copy["bind_interface"] = self.interface

        cfg = {
            "log": {"level": "warn"},
            "dns": {
                "servers": [
                    {
                        "type": "udp",
                        "tag": "dns-direct",
                        "server": "223.5.5.5",
                        "server_port": 53,
                        "detour": "direct",
                    }
                ],
                "final": "dns-direct",
                "strategy": "prefer_ipv4",
            },
            "inbounds": [
                {
                    "type": "socks",
                    "tag": "socks-in",
                    "listen": "127.0.0.1",
                    "listen_port": listen_port,
                }
            ],
            "outbounds": [
                node_copy,
                {"type": "direct", "tag": "direct", "bind_interface": self.interface},
            ],
            "route": {
                "rules": [
                    {"protocol": "dns", "outbound": "dns-direct"},
                    {"inbound": "socks-in", "outbound": node_copy.get("tag", "proxy")},
                ]
            },
        }

        tmp_path = None
        proc = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
                json.dump(cfg, f)
                tmp_path = f.name

            env = dict(os.environ)
            env["ENABLE_DEPRECATED_LEGACY_DNS_SERVERS"] = "true"
            proc = subprocess.Popen(
                [self.sing_box_bin, "run", "-c", tmp_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )

            if not wait_for_port(listen_port, timeout=3.0) or proc.poll() is not None:
                err = proc.stderr.read() if proc.stderr else "SOCKS5 startup timeout"
                return False, 0.0, f"sing-box startup failed: {err[:60].strip()}"

            session = requests.Session()
            session.trust_env = False
            session.proxies.update(
                {
                    "http": f"socks5h://127.0.0.1:{listen_port}",
                    "https": f"socks5h://127.0.0.1:{listen_port}",
                }
            )

            start = time.time()
            resp = session.get(TEST_URL, timeout=self.timeout)
            elapsed = (time.time() - start) * 1000

            if resp.status_code == 204:
                return True, round(elapsed, 1), "OK"
            return False, round(elapsed, 1), f"HTTP {resp.status_code}"

        except requests.exceptions.Timeout:
            return False, 0.0, "Timeout"
        except Exception as e:
            return False, 0.0, f"{type(e).__name__}"
        finally:
            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=1)
                except Exception:
                    proc.kill()
            release_port(listen_port)
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def test_with_mihomo(self, node: dict[str, Any]) -> tuple[bool, float, str]:
        """Test a node using Mihomo (Clash.Meta), bound to physical interface."""
        if not self.mihomo_bin:
            return False, 0.0, "mihomo binary not found"

        clash_proxies = to_clash_proxies([node])
        if not clash_proxies:
            return False, 0.0, "protocol unsupported by clash converter"

        listen_port = get_free_port()
        proxy_name = clash_proxies[0]["name"]

        cfg = {
            "mixed-port": listen_port,
            "interface-name": self.interface,
            "mode": "rule",
            "log-level": "silent",
            "dns": {
                "enable": True,
                "ipv6": False,
                "enhanced-mode": "redir-host",
                "nameserver": ["223.5.5.5", "119.29.29.29"],
            },
            "proxies": clash_proxies,
            "rules": [f"MATCH,{proxy_name}"],
        }

        tmp_path = None
        proc = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
                yaml.dump(cfg, f)
                tmp_path = f.name

            proc = subprocess.Popen(
                [self.mihomo_bin, "-f", tmp_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )

            if not wait_for_port(listen_port, timeout=3.0) or proc.poll() is not None:
                err = proc.stderr.read() if proc.stderr else "mixed-port startup timeout"
                return False, 0.0, f"mihomo startup failed: {err[:60].strip()}"

            session = requests.Session()
            session.trust_env = False
            session.proxies.update(
                {
                    "http": f"http://127.0.0.1:{listen_port}",
                    "https": f"http://127.0.0.1:{listen_port}",
                }
            )

            start = time.time()
            resp = session.get(TEST_URL, timeout=self.timeout)
            elapsed = (time.time() - start) * 1000

            if resp.status_code == 204:
                return True, round(elapsed, 1), "OK"
            return False, round(elapsed, 1), f"HTTP {resp.status_code}"

        except requests.exceptions.Timeout:
            return False, 0.0, "Timeout"
        except Exception as e:
            return False, 0.0, f"{type(e).__name__}"
        finally:
            if proc:
                try:
                    proc.terminate()
                    proc.wait(timeout=1)
                except Exception:
                    proc.kill()
            release_port(listen_port)
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass

    def test_node_dual(self, node: dict[str, Any]) -> dict[str, Any]:
        """Test a single node sequentially through both Sing-box and Mihomo."""
        tag = node.get("tag", "unknown")
        ntype = node.get("type", "unknown")

        sb_ok, sb_lat, sb_err = self.test_with_singbox(node)
        mh_ok, mh_lat, mh_err = self.test_with_mihomo(node)

        return {
            "tag": tag,
            "type": ntype,
            "singbox": {"ok": sb_ok, "latency_ms": sb_lat, "error": sb_err},
            "mihomo": {"ok": mh_ok, "latency_ms": mh_lat, "error": mh_err},
            "both_ok": sb_ok and mh_ok,
            "any_ok": sb_ok or mh_ok,
        }

    def test_batch(self, nodes: list[dict[str, Any]], max_workers: int = 8) -> list[dict[str, Any]]:
        """Test a list of nodes concurrently with both engines."""
        results: list[dict[str, Any]] = []
        workers = min(max_workers, max(1, len(nodes)))

        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_node = {executor.submit(self.test_node_dual, n): n for n in nodes}
            for future in concurrent.futures.as_completed(future_to_node):
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.debug(f"Dual test error: {e}")

        return results
