[![简体中文](https://img.shields.io/badge/语言-简体中文-red)](README_CN.md)
[![English](https://img.shields.io/badge/Language-English-red)](README.md)

## 🚀 快速开始

1. 在Github上搜索并安装[开源客户端](https://github.com/awesome-vpn/awesome-vpn/wiki/Clients)
2. 将下方的订阅链接复制到客户端
3. 选择合适的节点开始使用

项目地址:
- [https://github.com/awesome-vpn/awesome-vpn](https://github.com/awesome-vpn/awesome-vpn)

## 📥 订阅链接

主订阅链接:
- https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all

备用镜像 (GitHub访问不稳定时使用):
- https://raw.kkgithub.com/awesome-vpn/awesome-vpn/master/all [优选: 香港/日本/新加坡]
- https://ghp.ci/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [优选: 日韩/美国/欧洲]
- https://ghproxy.net/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [优选: 日本]

## 📊 VPN和代理协议分析

| OSI层级 | 协议 | 说明 |
|--------|------|------|
| 第2层 - 数据链路层 | PPTP | 点对点隧道协议，较旧，安全性较低 |
| 第2层 - 数据链路层 | L2TP | 第二层隧道协议，通常与IPsec配合使用 |
| 第3层 - 网络层 | IPsec | 互联网协议安全，可与L2TP配合或单独使用 |
| 第3层 - 网络层 | WireGuard | 新型高效VPN协议，性能优越 |
| 第3层 - 网络层 | GRE | 通用路由封装，可封装多种网络层协议 |
| 第4层 - 传输层 | TUIC | TCP over UDP，基于QUIC的传输层协议 |
| 第4层 - 传输层 | Hysteria | 基于QUIC的高速网络传输协议 |
| 第4层 - 传输层 | Hysteria2 | Hysteria的改进版本，更高效和安全 |
| 第4层 - 传输层 | QUIC | 快速UDP网络连接，由Google开发 |
| 第5层 - 会话层 | SOCKS4 | 简单的防火墙穿透协议，不支持认证 |
| 第5层 - 会话层 | SOCKS5 | 支持认证和UDP的通用代理协议 |
| 第5层 - 会话层 | SSL/TLS | 安全套接字层/传输层安全，为应用层提供加密 |
| 第7层 - 应用层 | OpenVPN | 使用OpenSSL库加密的VPN系统 |
| 第7层 - 应用层 | Shadowsocks | 轻量级加密代理协议 |
| 第7层 - 应用层 | ShadowsocksR | Shadowsocks的扩展版本，增加了混淆等特性 |
| 第7层 - 应用层 | VMess | 基于TLS的加密传输协议，由V2Ray项目提出 |
| 第7层 - 应用层 | VLESS | VMess的简化版本，减少了加密开销 |
| 第7层 - 应用层 | Trojan | 伪装成HTTPS流量的代理协议 |
| 第7层 - 应用层 | Trojan-Go | Trojan协议的Go语言实现，增加了WebSocket等特性 |
| 第7层 - 应用层 | HTTP代理 | 最基本的代理类型，通常不加密 |
| 第7层 - 应用层 | HTTPS代理 | 加密的HTTP代理，提供更好的安全性 |
| 第7层 - 应用层 | SSH隧道 | 利用SSH协议创建加密隧道 |
| 第7层 - 应用层 | Tor | 匿名通信网络，通过多层加密和中继提供高度隐私 |
| 第7层 - 应用层 | Naive | 基于Chromium网络栈的HTTPS代理协议 |
| 第7层 - 应用层 | Brook | 简单的跨平台代理协议 |
| 第7层 - 应用层 | Shadowtls | 将Shadowsocks流量伪装成TLS流量的协议 |
| 第7层 - 应用层 | Reality | 基于TLS 1.3的新型代理协议，提供更强的抗检测能力 |
| 第7层 - 应用层 | WebSocket | 在单个TCP连接上提供全双工通信的协议 |

## ⚠️ 当前挑战

许多一键式VPN客户端面临以下问题:
- 由于域名/IP被封锁导致的连接问题
- 在应用商店中无法获取
- 强制付费或限时试用

## 🔬 如何让互联网更自由

一般国家层面要大范围封杀代理或者VPN，会从OSI协议中较容易检测出特征的流量进行大面积封锁。并勒令应用商店下架代理类应用。
如果针对性封杀的话，会从IP或者域名层面实现精确打击。因此理论上，如果没有海量服务器支撑，无论代理协议多么先进，都无法长期稳定使用。

所以需要一款好的代理客户端，满足以下条件：

- 永久免费且无限制使用
- 海量代理服务器节点
- 跨所有平台支持
- 支持多种代理协议
- 支持多种加密方式
- 手机版本提供官方应用商店之外的安装更新方式

## ⚖️ 免责声明

本项目仅用于教育和研究目的。用户在使用这些资源时请负责遵守当地法律法规，保护自己。
