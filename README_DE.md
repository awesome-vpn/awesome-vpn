[![Deutsch](https://img.shields.io/badge/Sprache-Deutsch-red)](README_DE.md)
[![English](https://img.shields.io/badge/Language-English-red)](README.md)

## 🚀 Schnellstart

1. Suchen und installieren Sie einen [Open-Source-Client](https://github.com/awesome-vpn/awesome-vpn/wiki/Clients) auf Github
2. Kopieren Sie die unten stehenden Abonnement-Links in den Client
3. Wählen Sie einen geeigneten Knoten und beginnen Sie mit der Nutzung

Projekt-Link:
- [https://github.com/awesome-vpn/awesome-vpn](https://github.com/awesome-vpn/awesome-vpn)

## 📥 Abonnement-Links

Haupt-Abonnement-Link:
- https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all

Spiegel-Links (Falls GitHub instabil ist):
- https://raw.kkgithub.com/awesome-vpn/awesome-vpn/master/all [Optimiert für: Hongkong/Japan/Singapur]
- https://ghp.ci/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Optimiert für: Japan/Korea/USA/Europa]
- https://ghproxy.net/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Optimiert für: Japan]

## 📊 VPN- und Proxy-Protokollanalyse

| OSI-Schicht | Protokoll | Beschreibung |
|-------------|-----------|--------------|
| Schicht 2 - Datenverbindung | PPTP | Point-to-Point-Tunneling-Protokoll, älter, geringe Sicherheit |
| Schicht 2 - Datenverbindung | L2TP | Layer-2-Tunneling-Protokoll, häufig mit IPsec verwendet |
| Schicht 3 - Netzwerk | IPsec | Internet-Protokollsicherheit, kann mit L2TP oder allein verwendet werden |
| Schicht 3 - Netzwerk | WireGuard | Neues effizientes VPN-Protokoll, überlegene Leistung |
| Schicht 3 - Netzwerk | GRE | Generische Routing-Kapselung, kann verschiedene Netzwerkprotokolle kapseln |
| Schicht 4 - Transport | TUIC | TCP über UDP, transportbasiertes Protokoll auf QUIC |
| Schicht 4 - Transport | Hysteria | Hochgeschwindigkeits-Netzwerktransportprotokoll auf QUIC |
| Schicht 4 - Transport | Hysteria2 | Verbesserte Version von Hysteria, effizienter und sicherer |
| Schicht 4 - Transport | QUIC | Schnelle UDP-Internetverbindungen, entwickelt von Google |
| Schicht 5 - Sitzung | SOCKS4 | Einfaches Firewall-Durchquerungsprotokoll, keine Authentifizierungsunterstützung |
| Schicht 5 - Sitzung | SOCKS5 | Universelles Proxy-Protokoll, das Authentifizierung und UDP unterstützt |
| Schicht 5 - Sitzung | SSL/TLS | Sichere Sockets/Transportsicherheitsschicht, bietet Verschlüsselung für die Anwendungsschicht |
| Schicht 7 - Anwendung | OpenVPN | VPN-System, das die OpenSSL-Bibliothek zur Verschlüsselung verwendet |
| Schicht 7 - Anwendung | Shadowsocks | Leichtes verschlüsseltes Proxy-Protokoll |
| Schicht 7 - Anwendung | ShadowsocksR | Erweiterte Version von Shadowsocks, fügt Funktionen wie Verschleierung hinzu |
| Schicht 7 - Anwendung | VMess | TLS-basiertes verschlüsseltes Übertragungsprotokoll, vorgeschlagen vom V2Ray-Projekt |
| Schicht 7 - Anwendung | VLESS | Vereinfachte Version von VMess, reduziert Verschlüsselungsaufwand |
| Schicht 7 - Anwendung | Trojan | Proxy-Protokoll, das sich als HTTPS-Verkehr tarnt |
| Schicht 7 - Anwendung | Trojan-Go | Go-Implementierung des Trojan-Protokolls, fügt Funktionen wie WebSocket hinzu |
| Schicht 7 - Anwendung | HTTP-Proxy | Grundlegendster Proxy-Typ, normalerweise unverschlüsselt |
| Schicht 7 - Anwendung | HTTPS-Proxy | Verschlüsselter HTTP-Proxy, bietet bessere Sicherheit |
| Schicht 7 - Anwendung | SSH-Tunnel | Erstellt verschlüsselte Tunnel mit dem SSH-Protokoll |
| Schicht 7 - Anwendung | Tor | Anonymes Kommunikationsnetzwerk, bietet hohe Privatsphäre durch mehrschichtige Verschlüsselung und Weiterleitung |
| Schicht 7 - Anwendung | Naive | HTTPS-Proxy-Protokoll basierend auf dem Chromium-Netzwerk-Stack |
| Schicht 7 - Anwendung | Brook | Einfaches plattformübergreifendes Proxy-Protokoll |
| Schicht 7 - Anwendung | Shadowtls | Protokoll, das Shadowsocks-Verkehr als TLS-Verkehr tarnt |
| Schicht 7 - Anwendung | Reality | Neues Proxy-Protokoll basierend auf TLS 1.3, bietet bessere Erkennungsvermeidung |
| Schicht 7 - Anwendung | WebSocket | Protokoll, das Full-Duplex-Kommunikation über eine einzelne TCP-Verbindung bietet |

## ⚠️ Aktuelle Herausforderungen

Viele One-Click-VPN-Clients stehen vor den folgenden Problemen:
- Verbindungsprobleme aufgrund blockierter Domains/IPs
- Nichtverfügbarkeit in App-Stores
- Erzwungene Zahlungen oder zeitlich begrenzte Tests

## 🔬 Unsere Mission

Wir erforschen langjährige VPN-Clients, um eine kostenlose, zuverlässige plattformübergreifende Lösung zu entwickeln. Unser Ziel ist es, eine Anwendung zu erstellen, die bietet:

- Dauerhaft kostenlose und unbegrenzte Nutzung
- Stabile Verbindungen
- Unterstützung für alle Plattformen
- Unterstützung für mehrere Proxy-Protokolle
- Unterstützung für mehrere Verschlüsselungsmethoden
- Die mobile Version bietet Installations- und Aktualisierungsmethoden außerhalb offizieller App-Stores

## ⚖️ Haftungsausschluss

Dieses Projekt dient nur zu Bildungs- und Forschungszwecken. Benutzer sind dafür verantwortlich, die lokalen Gesetze und Vorschriften bei der Nutzung dieser Ressourcen einzuhalten.
