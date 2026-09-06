"""Security filter for honeypots, SSRF targets, and RFC private IP subnets."""

import ipaddress
import logging
from typing import Any

logger = logging.getLogger(__name__)

# RFC Private, Loopback, Link-Local, and Broadcast IP networks to block
BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),  # Current network
    ipaddress.ip_network("10.0.0.0/8"),  # RFC 1918
    ipaddress.ip_network("100.64.0.0/10"),  # Carrier-grade NAT
    ipaddress.ip_network("127.0.0.0/8"),  # Loopback
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local
    ipaddress.ip_network("172.16.0.0/12"),  # RFC 1918
    ipaddress.ip_network("192.0.0.0/24"),  # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),  # TEST-NET-1
    ipaddress.ip_network("192.168.0.0/16"),  # RFC 1918
    ipaddress.ip_network("198.18.0.0/15"),  # Benchmark testing
    ipaddress.ip_network("198.51.100.0/24"),  # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),  # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),  # Multicast
    ipaddress.ip_network("240.0.0.0/4"),  # Reserved
    ipaddress.ip_network("255.255.255.255/32"),  # Broadcast
    # IPv6
    ipaddress.ip_network("::1/128"),  # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),  # RFC 4193 Unique Local (ULA)
    ipaddress.ip_network("fe80::/10"),  # IPv6 Link-Local
]

FAKE_OR_DNS_IPS = {
    "8.8.8.8",
    "8.8.4.4",
    "1.1.1.1",
    "1.0.0.1",
    "4.2.2.2",
    "4.2.2.1",
    "114.114.114.114",
    "223.5.5.5",
    "9.9.9.9",
}

BLOCKED_DOMAINS = [
    ".google.com",
    ".github.com",
    ".bing.com",
    ".baidu.com",
    "localhost",
    ".local",
    ".internal",
    ".lan",
]


class HoneypotFilter:
    """Detects and drops malicious or fraudulent proxy node candidates."""

    @staticmethod
    def is_blocked_ip(ip_str: str) -> bool:
        """Check if an IP string falls into private, loopback, or reserved ranges."""
        try:
            ip = ipaddress.ip_address(ip_str)
            for net in BLOCKED_NETWORKS:
                if ip in net:
                    return True
            return False
        except ValueError:
            return False

    @classmethod
    def is_honeypot_or_invalid(cls, node: dict[str, Any]) -> bool:
        """
        Returns True if the node is malformed, uses private/internal addresses,
        or targets honeypot/well-known DNS IPs.
        """
        if not isinstance(node, dict):
            return True

        server = str(node.get("server", "")).strip().lower()
        if not server or "." not in server:
            return True

        # Check port
        raw_port = node.get("server_port") or node.get("port")
        if raw_port is None:
            return True
        try:
            port = int(raw_port)
            if port <= 0 or port > 65535:
                return True
            if port < 20 and port not in (80, 443):
                return True
        except (ValueError, TypeError):
            return True

        # Check well-known public DNS IPs (fakes)
        if server in FAKE_OR_DNS_IPS:
            return True

        # Check private / SSRF IP subnets
        if cls.is_blocked_ip(server):
            return True

        # Check blocked domain suffixes
        for domain in BLOCKED_DOMAINS:
            if server == domain.lstrip("."):
                return True
            if server.endswith(domain):
                return True

        return False
