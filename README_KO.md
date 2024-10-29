[![한국어](https://img.shields.io/badge/언어-한국어-red)](README_KO.md)
[![English](https://img.shields.io/badge/Language-English-red)](README.md)

## 🚀 빠른 시작

1. Github에서 [오픈소스 클라이언트](https://github.com/awesome-vpn/awesome-vpn/wiki/Clients)를 검색하고 설치
2. 아래의 구독 링크를 클라이언트에 복사
3. 적절한 노드를 선택하여 사용 시작

프로젝트 링크:
- [https://github.com/awesome-vpn/awesome-vpn](https://github.com/awesome-vpn/awesome-vpn)

## 📥 구독 링크

메인 구독 링크:
- https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all

미러 링크 (GitHub 접속이 불안정할 경우):
- https://raw.kkgithub.com/awesome-vpn/awesome-vpn/master/all [최적: 홍콩/일본/싱가포르]
- https://ghp.ci/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [최적: 일본/한국/미국/유럽]
- https://ghproxy.net/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [최적: 일본]

## 📊 VPN 및 프록시 프로토콜 분석

| OSI 계층 | 프로토콜 | 설명 |
|----------|----------|------|
| 2계층 - 데이터 링크 | PPTP | 포인트 투 포인트 터널링 프로토콜, 오래됨, 보안 낮음 |
| 2계층 - 데이터 링크 | L2TP | 2계층 터널링 프로토콜, 종종 IPsec과 함께 사용 |
| 3계층 - 네트워크 | IPsec | 인터넷 프로토콜 보안, L2TP와 함께 또는 단독으로 사용 가능 |
| 3계층 - 네트워크 | WireGuard | 새로운 효율적인 VPN 프로토콜, 우수한 성능 |
| 3계층 - 네트워크 | GRE | 일반 라우팅 캡슐화, 다양한 네트워크 계층 프로토콜 캡슐화 가능 |
| 4계층 - 전송 | TUIC | TCP over UDP, QUIC 기반 전송 계층 프로토콜 |
| 4계층 - 전송 | Hysteria | QUIC 기반 고속 네트워크 전송 프로토콜 |
| 4계층 - 전송 | Hysteria2 | Hysteria의 개선된 버전, 더 효율적이고 안전함 |
| 4계층 - 전송 | QUIC | 빠른 UDP 인터넷 연결, Google 개발 |
| 5계층 - 세션 | SOCKS4 | 간단한 방화벽 통과 프로토콜, 인증 지원 없음 |
| 5계층 - 세션 | SOCKS5 | 인증 및 UDP를 지원하는 범용 프록시 프로토콜 |
| 5계층 - 세션 | SSL/TLS | 보안 소켓 계층/전송 계층 보안, 애플리케이션 계층에 암호화 제공 |
| 7계층 - 애플리케이션 | OpenVPN | OpenSSL 라이브러리를 사용하여 암호화하는 VPN 시스템 |
| 7계층 - 애플리케이션 | Shadowsocks | 경량 암호화 프록시 프로토콜 |
| 7계층 - 애플리케이션 | ShadowsocksR | Shadowsocks의 확장 버전, 난독화 등의 기능 추가 |
| 7계층 - 애플리케이션 | VMess | TLS 기반 암호화 전송 프로토콜, V2Ray 프로젝트에서 제안 |
| 7계층 - 애플리케이션 | VLESS | VMess의 간소화 버전, 암호화 오버헤드 감소 |
| 7계층 - 애플리케이션 | Trojan | HTTPS 트래픽으로 위장한 프록시 프로토콜 |
| 7계층 - 애플리케이션 | Trojan-Go | Trojan 프로토콜의 Go 구현, WebSocket 등의 기능 추가 |
| 7계층 - 애플리케이션 | HTTP 프록시 | 가장 기본적인 프록시 유형, 일반적으로 암호화되지 않음 |
| 7계층 - 애플리케이션 | HTTPS 프록시 | 암호화된 HTTP 프록시, 더 나은 보안 제공 |
| 7계층 - 애플리케이션 | SSH 터널 | SSH 프로토콜을 사용하여 암호화된 터널 생성 |
| 7계층 - 애플리케이션 | Tor | 익명 통신 네트워크, 다중 레이어 암호화 및 릴레이를 통해 높은 프라이버시 제공 |
| 7계층 - 애플리케이션 | Naive | Chromium 네트워크 스택 기반의 HTTPS 프록시 프로토콜 |
| 7계층 - 애플리케이션 | Brook | 간단한 크로스 플랫폼 프록시 프로토콜 |
| 7계층 - 애플리케이션 | Shadowtls | Shadowsocks 트래픽을 TLS 트래픽으로 위장하는 프로토콜 |
| 7계층 - 애플리케이션 | Reality | TLS 1.3 기반의 새로�� 프록시 프로토콜, 더 나은 탐지 방지 기능 제공 |
| 7계층 - 애플리케이션 | WebSocket | 단일 TCP 연결에서 풀 듀플렉스 통신을 제공하는 프로토콜 |

## ⚠️ 현재 과제

많은 원클릭 VPN 클라이언트가 다음과 같은 문제에 직면하고 있습니다:
- 도메인/IP 차단으로 인한 연결 문제
- 앱 스토어에서 사용 불가
- 강제 결제 또는 제한된 무료 체험

## 🔬 우리의 사명

우리는 오래된 VPN 클라이언트를 연구하여 무료, 신뢰할 수 있는 크로스 플랫폼 솔루션을 개발하고 있습니다. 우리의 목표는 다음을 제공하는 애플리케이션을 만드는 것입니다:

- 영구적으로 무료 및 무제한 사용
- 안정적인 연결
- 모든 플랫폼 지원
- 다양한 프록시 프로토콜 지원
- 다양한 암호화 방법 지원
- 모바일 버전은 공식 앱 스토어 외부에서 설치 및 업데이트 방법 제공

## ⚖️ 면책 조항

이 프로젝트는 교육 및 연구 목적으로만 사용됩니다. 사용자는 이러한 리소스를 사용할 때 지역 법률 및 규정을 준수할 책임이 있습니다.
