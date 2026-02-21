[![简体中文](https://img.shields.io/badge/语言-简体中文-red)](README_CN.md)
[![English](https://img.shields.io/badge/Language-English-red)](README.md)
[![العربية](https://img.shields.io/badge/اللغة-العربية-red)](README_AR.md)
[![বাংলা](https://img.shields.io/badge/ভাষা-বাংলা-red)](README_BN.md)
[![Deutsch](https://img.shields.io/badge/Sprache-Deutsch-red)](README_DE.md)
[![Español](https://img.shields.io/badge/Idioma-Español-red)](README_ES.md)
[![فارسی](https://img.shields.io/badge/زبان-فارسی-red)](README_FA.md)
[![Français](https://img.shields.io/badge/Langue-Français-red)](README_FR.md)
[![हिन्दी](https://img.shields.io/badge/भाषा-हिन्दी-red)](README_HI.md)
[![Bahasa Indonesia](https://img.shields.io/badge/Bahasa-Indonesia-red)](README_ID.md)
[![Italiano](https://img.shields.io/badge/Lingua-Italiano-red)](README_IT.md)
[![日本語](https://img.shields.io/badge/言語-日本語-red)](README_JA.md)
[![한국어](https://img.shields.io/badge/언어-한국어-red)](README_KO.md)
[![Polski](https://img.shields.io/badge/Język-Polski-red)](README_PL.md)
[![Português](https://img.shields.io/badge/Língua-Português-red)](README_PT.md)
[![Русский](https://img.shields.io/badge/Язык-Русский-red)](README_RU.md)
[![ไทย](https://img.shields.io/badge/ภาษา-ไทย-red)](README_TH.md)
[![Türkçe](https://img.shields.io/badge/Dil-Türkçe-red)](README_TR.md)
[![اردو](https://img.shields.io/badge/زبان-اردو-red)](README_UR.md)
[![Tiếng Việt](https://img.shields.io/badge/Ngôn%20ngữ-Tiếng%20Việt-red)](README_VI.md)

## 🚀 Quick Start

1. Download and install a [Recommended Client](#recommended-clients)
2. Copy the subscription link below
3. Import into your client and connect

## 📥 Subscription Links

Main subscription link:
- https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all

Mirror links (use if GitHub is unstable):
- https://raw.kkgithub.com/awesome-vpn/awesome-vpn/master/all [Preferred: Hong Kong/Japan/Singapore]
- https://ghp.ci/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Preferred: Japan/Korea/USA/Europe]
- https://ghproxy.net/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Preferred: Japan]

## 📱 Recommended Clients

| Platform | Client | Protocol Support | Link |
|----------|--------|------------------|------|
| **Windows** | **v2rayN** | VMess, VLESS, Trojan, SS, etc. | [GitHub](https://github.com/2dust/v2rayN) |
| | **Clash Verge** | Clash Meta (All Protocols) | [GitHub](https://github.com/clash-verge-rev/clash-verge-rev) |
| **Android** | **v2rayNG** | VMess, VLESS, Trojan, SS, etc. | [GitHub](https://github.com/2dust/v2rayNG) |
| | **Sing-box** | All (Official Client) | [Google Play](https://play.google.com/store/apps/details?id=io.nekohasekai.sfa) |
| **macOS** | **Clash Verge** | Clash Meta (All Protocols) | [GitHub](https://github.com/clash-verge-rev/clash-verge-rev) |
| | **Sing-box** | All (Official Client) | [App Store](https://apps.apple.com/us/app/sing-box/id6451272673) |
| **iOS** | **Sing-box** | All (Official Client) | [App Store](https://apps.apple.com/us/app/sing-box/id6451272673) |
| | **V2Box** | VMess, VLESS, Trojan, SS | [App Store](https://apps.apple.com/us/app/v2box-v2ray-client/id6446814690) |

## 📊 VPN and Proxy Protocol Analysis

| OSI Layer | Protocol | Category | Description |
|-----------|----------|----------|-------------|
| Layer 2 - Data Link | PPTP | VPN Protocol | Point-to-Point Tunneling Protocol, older, low security |
| Layer 2 - Data Link | L2TP | VPN Protocol | Layer 2 Tunneling Protocol, often used with IPsec |
| Layer 3 - Network | IPsec | VPN Protocol | Internet Protocol Security, can be used with L2TP or alone |
| Layer 3 - Network | WireGuard | VPN Protocol | New efficient VPN protocol, superior performance |
| Layer 3 - Network | GRE | Tunneling Protocol | Generic Routing Encapsulation, can encapsulate various network layer protocols |
| Layer 4 - Transport | TUIC | Transport Protocol | TCP over UDP, transport layer protocol based on QUIC |
| Layer 4 - Transport | Hysteria | Transport Protocol | High-speed network transport protocol based on QUIC |
| Layer 4 - Transport | Hysteria2 | Transport Protocol | Improved version of Hysteria, more efficient and secure |
| Layer 4 - Transport | Juicity | Transport Protocol | QUIC-based proxy protocol with congestion control and zero-RTT |
| Layer 4 - Transport | QUIC | Transport Protocol | Quick UDP Internet Connections, developed by Google |
| Layer 5 - Session | SOCKS4 | Proxy Protocol | Simple firewall traversal protocol, no authentication support |
| Layer 5 - Session | SOCKS5 | Proxy Protocol | Universal proxy protocol supporting authentication and UDP |
| Layer 5 - Session | SSL/TLS | Encryption | Secure Sockets Layer/Transport Layer Security, provides encryption for application layer |
| Layer 7 - Application | OpenVPN | VPN Protocol | VPN system using OpenSSL library for encryption |
| Layer 7 - Application | Shadowsocks | Proxy Protocol | Lightweight encrypted proxy protocol |
| Layer 7 - Application | ShadowsocksR | Proxy Protocol | Extended version of Shadowsocks, adds features like obfuscation |
| Layer 7 - Application | VMess | Proxy Protocol | TLS-based encrypted transmission protocol, proposed by V2Ray project |
| Layer 7 - Application | VLESS | Proxy Protocol | Simplified version of VMess, reduces encryption overhead |
| Layer 7 - Application | Trojan | Proxy Protocol | Proxy protocol disguising as HTTPS traffic |
| Layer 7 - Application | Trojan-Go | Proxy Protocol | Go implementation of Trojan protocol, adds features like WebSocket |
| Layer 7 - Application | NaïveProxy | Proxy Protocol | Uses Chrome's network stack to camouflage traffic as standard HTTPS |
| Layer 7 - Application | HTTP Proxy | Proxy Protocol | Most basic proxy type, usually unencrypted |
| Layer 7 - Application | HTTPS Proxy | Proxy Protocol | Encrypted HTTP proxy, provides better security |
| Layer 7 - Application | SSH Tunnel | Tunneling Protocol | Creates encrypted tunnels using SSH protocol |
| Layer 7 - Application | Tor | Anonymity Network | Anonymous communication network, provides high privacy through multi-layer encryption and relaying |
| Layer 7 - Application | Brook | Proxy Protocol | Simple cross-platform proxy protocol |
| Layer 7 - Application | Shadowtls | Transport Protocol | Protocol disguising Shadowsocks traffic as TLS traffic |
| Layer 7 - Application | Reality | Transport Protocol | New proxy protocol based on TLS 1.3, provides better anti-detection capability |
| Layer 7 - Application | WebSocket | Transport Protocol | Protocol providing full-duplex communication on a single TCP connection |
| Layer 7 - Application | gRPC | Transport Protocol | High performance RPC framework, used as transport layer for proxies |

## ⚠️ Current Challenges

Many one-click VPN clients face the following issues:
- Connection problems due to blocked domains/IPs
- Unavailability in app stores
- Forced payments or time-limited trials

## 🎯 Our Goal

We aim to provide a reliable source of information and resources for free and open internet access. This project focuses on:

- **Resource Aggregation**: Collecting and verifying public proxy nodes (V2Ray, Shadowsocks, Hysteria, etc.) from various sources.
- **Stability**: Ensuring high availability through daily automated updates and checks.
- **Accessibility**: Providing simple subscription links compatible with popular clients (v2rayN, Clash, Sing-box, etc.).
- **Education**: Offering clear documentation on protocols and clients to help users bypass censorship.

## ⚖️ Disclaimer

This project is for educational and research purposes only. Users are responsible for complying with local laws and regulations when using these resources.
