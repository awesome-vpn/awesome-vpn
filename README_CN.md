[![English](https://img.shields.io/badge/Language-English-red)](README.md)

## 🚀 快速开始

1. 复制下方的订阅链接
2. 导入客户端并连接使用

## 📥 订阅链接

主订阅链接:
- https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all

备用镜像 (GitHub访问不稳定时使用):
- https://raw.kkgithub.com/awesome-vpn/awesome-vpn/master/all [优选: 香港/日本/新加坡]
- https://ghp.ci/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [优选: 日韩/美国/欧洲]
- https://ghproxy.net/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [优选: 日本]

## 📊 VPN和代理协议分析

| OSI层级 | 协议 | 分类 | 说明 |
|--------|------|------|------|
| 第2层 - 数据链路层 | PPTP | VPN协议 | 点对点隧道协议，较旧，安全性较低 |
| 第2层 - 数据链路层 | L2TP | VPN协议 | 第二层隧道协议，通常与IPsec配合使用 |
| 第3层 - 网络层 | IPsec | VPN协议 | 互联网协议安全，可与L2TP配合或单独使用 |
| 第3层 - 网络层 | WireGuard | VPN协议 | 新型高效VPN协议，性能优越 |
| 第3层 - 网络层 | GRE | 隧道协议 | 通用路由封装，可封装多种网络层协议 |
| 第4层 - 传输层 | TUIC | 传输协议 | TCP over UDP，基于QUIC的传输层协议 |
| 第4层 - 传输层 | Hysteria | 传输协议 | 基于QUIC的高速网络传输协议 |
| 第4层 - 传输层 | Hysteria2 | 传输协议 | Hysteria的改进版本，更高效和安全 |
| 第4层 - 传输层 | Juicity | 传输协议 | 基于QUIC的代理协议，具有拥塞控制和零RTT特性 |
| 第4层 - 传输层 | QUIC | 传输协议 | 快速UDP网络连接，由Google开发 |
| 第5层 - 会话层 | SOCKS4 | 代理协议 | 简单的防火墙穿透协议，不支持认证 |
| 第5层 - 会话层 | SOCKS5 | 代理协议 | 支持认证和UDP的通用代理协议 |
| 第5层 - 会话层 | SSL/TLS | 加密协议 | 安全套接字层/传输层安全，为应用层提供加密 |
| 第7层 - 应用层 | OpenVPN | VPN协议 | 使用OpenSSL库加密的VPN系统 |
| 第7层 - 应用层 | Shadowsocks | 代理协议 | 轻量级加密代理协议 |
| 第7层 - 应用层 | ShadowsocksR | 代理协议 | Shadowsocks的扩展版本，增加了混淆等特性 |
| 第7层 - 应用层 | VMess | 代理协议 | 基于TLS的加密传输协议，由V2Ray项目提出 |
| 第7层 - 应用层 | VLESS | 代理协议 | VMess的简化版本，减少了加密开销 |
| 第7层 - 应用层 | Trojan | 代理协议 | 伪装成HTTPS流量的代理协议 |
| 第7层 - 应用层 | Trojan-Go | 代理协议 | Trojan协议的Go语言实现，增加了WebSocket等特性 |
| 第7层 - 应用层 | NaïveProxy | 代理协议 | 使用Chrome网络栈将流量伪装成标准HTTPS |
| 第7层 - 应用层 | HTTP代理 | 代理协议 | 最基本的代理类型，通常不加密 |
| 第7层 - 应用层 | HTTPS代理 | 代理协议 | 加密的HTTP代理，提供更好的安全性 |
| 第7层 - 应用层 | SSH隧道 | 隧道协议 | 利用SSH协议创建加密隧道 |
| 第7层 - 应用层 | Tor | 匿名网络 | 匿名通信网络，通过多层加密和中继提供高度隐私 |
| 第7层 - 应用层 | Brook | 代理协议 | 简单的跨平台代理协议 |
| 第7层 - 应用层 | Shadowtls | 传输协议 | 将Shadowsocks流量伪装成TLS流量的协议 |
| 第7层 - 应用层 | Reality | 传输协议 | 基于TLS 1.3的新型代理协议，提供更强的抗检测能力 |
| 第7层 - 应用层 | WebSocket | 传输协议 | 在单个TCP连接上提供全双工通信的协议 |
| 第7层 - 应用层 | gRPC | 传输协议 | 高性能RPC框架，常作为代理的传输层使用 |

## ⚠️ 当前挑战

许多一键式VPN客户端面临以下问题:
- 由于域名/IP被封锁导致的连接问题
- 在应用商店中无法获取
- 强制付费或限时试用

## 🎯 我们的目标

我们致力于提供稳定、免费的互联网访问资源和信息。本项目主要关注：

- **资源聚合**：收集并验证来自各种来源的公共代理节点（V2Ray, Shadowsocks, Hysteria等）。
- **稳定性**：通过每日自动更新和检测，确保节点的高可用性。
- **易用性**：提供兼容主流客户端（v2rayN, Clash, Sing-box等）的简单订阅链接。
- **知识普及**：提供关于协议和客户端的清晰文档，帮助用户突破封锁。

## ⚖️ 免责声明

本项目仅用于教育和研究目的。用户在使用这些资源时请负责遵守当地法律法规，保护自己。
