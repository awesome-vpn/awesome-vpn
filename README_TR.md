[![Türkçe](https://img.shields.io/badge/Dil-Türkçe-red)](README_TR.md)
[![English](https://img.shields.io/badge/Language-English-red)](README.md)

# Ücretsiz Ağ Hızlandırma Kaynakları

> Ücretsiz proxy'ler, hesaplar, ağ hızlandırma ve internet özgürlük araçlarını paylaşmak için optimize edilmiş README.

## 🚀 Hızlı Erişim

1. GitHub'da [açık kaynak istemcileri](https://github.com/awesome-vpn/awesome-vpn/wiki/Clients) arayın ve yükleyin
2. Aşağıdaki abonelik bağlantılarını istemciye kopyalayın
3. Uygun bir düğüm seçin ve kullanmaya başlayın

Proje bağlantısı:
- [https://github.com/awesome-vpn/awesome-vpn](https://github.com/awesome-vpn/awesome-vpn)

## 📥 Abonelik Bağlantıları

Ana abonelik bağlantısı:
- https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all

Ayna bağlantıları (GitHub kararsız ise kullanın):
- https://raw.kkgithub.com/awesome-vpn/awesome-vpn/master/all [Hong Kong, Japonya, Singapur, vb.]
- https://ghp.ci/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Japonya, Kore, Singapur, ABD, Almanya, vb.]
- https://ghproxy.net/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Osaka, Japonya]

## 📱 [Açık Kaynak İstemciler](https://github.com/awesome-vpn/awesome-vpn/wiki/Clients)

## 📊 VPN ve Proxy Protokol Analizi

| OSI Katmanı | Protokol | Açıklama |
|-------------|----------|----------|
| Katman 2 - Veri Bağlantısı | PPTP | Noktadan Noktaya Tünelleme Protokolü, eski, düşük güvenlik |
| Katman 2 - Veri Bağlantısı | L2TP | Katman 2 Tünelleme Protokolü, genellikle IPsec ile kullanılır |
| Katman 3 - Ağ | IPsec | İnternet Protokol Güvenliği, L2TP ile veya tek başına kullanılabilir |
| Katman 3 - Ağ | WireGuard | Yeni verimli VPN protokolü, üstün performans |
| Katman 3 - Ağ | GRE | Genel Yönlendirme Kapsülleme, çeşitli ağ protokollerini kapsülleyebilir |
| Katman 4 - Taşıma | TUIC | UDP üzerinde TCP, QUIC tabanlı taşıma protokolü |
| Katman 4 - Taşıma | Hysteria | QUIC tabanlı yüksek hızlı ağ taşıma protokolü |
| Katman 4 - Taşıma | Hysteria2 | Hysteria'nın geliştirilmiş versiyonu, daha verimli ve güvenli |
| Katman 4 - Taşıma | QUIC | Hızlı UDP internet bağlantıları, Google tarafından geliştirilmiştir |
| Katman 5 - Oturum | SOCKS4 | Basit güvenlik duvarı geçiş protokolü, kimlik doğrulama desteği yok |
| Katman 5 - Oturum | SOCKS5 | Kimlik doğrulama ve UDP destekleyen evrensel proxy protokolü |
| Katman 5 - Oturum | SSL/TLS | Güvenli Soketler/ Taşıma Katmanı Güvenliği, uygulama katmanı için şifreleme sağlar |
| Katman 7 - Uygulama | OpenVPN | Şifreleme için OpenSSL kütüphanesini kullanan VPN sistemi |
| Katman 7 - Uygulama | Shadowsocks | Hafif şifreli proxy protokolü |
| Katman 7 - Uygulama | ShadowsocksR | Shadowsocks'un genişletilmiş versiyonu, karartma gibi özellikler ekler |
| Katman 7 - Uygulama | VMess | TLS tabanlı şifreli iletim protokolü, V2Ray projesi tarafından önerilmiştir |
| Katman 7 - Uygulama | VLESS | VMess'in basitleştirilmiş versiyonu, şifreleme yükünü azaltır |
| Katman 7 - Uygulama | Trojan | HTTPS trafiği gibi görünen proxy protokolü |
| Katman 7 - Uygulama | Trojan-Go | Trojan protokolünün Go uygulaması, WebSocket gibi özellikler ekler |
| Katman 7 - Uygulama | HTTP Proxy | En temel proxy türü, genellikle şifrelenmemiş |
| Katman 7 - Uygulama | HTTPS Proxy | Şifreli HTTP proxy, daha iyi güvenlik sağlar |
| Katman 7 - Uygulama | SSH Tüneli | SSH protokolü kullanarak şifreli tüneller oluşturur |
| Katman 7 - Uygulama | Tor | Anonim iletişim ağı, çok katmanlı şifreleme ve yönlendirme ile yüksek gizlilik sağlar |
| Katman 7 - Uygulama | Naive | Chromium ağ yığınına dayalı HTTPS proxy protokolü |
| Katman 7 - Uygulama | Brook | Basit çapraz platform proxy protokolü |
| Katman 7 - Uygulama | Shadowtls | Shadowsocks trafiğini TLS trafiği gibi gösteren protokol |
| Katman 7 - Uygulama | Reality | TLS 1.3 tabanlı yeni proxy protokolü, daha iyi tespit önleme yeteneği sağlar |
| Katman 7 - Uygulama | WebSocket | Tek bir TCP bağlantısında tam çift yönlü iletişim sağlayan protokol |

## ⚠️ Mevcut Zorluklar

Birçok tek tıklamalı VPN istemcisi sorunlarla karşılaşıyor:
- Engellenen alan adları/IP'ler nedeniyle bağlantı sorunları
- Uygulama mağazalarında bulunmama
- Zorunlu ödemeler veya sınırlı denemeler

## 🔬 Misyonumuz

Ücretsiz, güvenilir, çapraz platform bir çözüm geliştirmek için uzun süredir var olan VPN istemcilerini araştırıyoruz. Amacımız şunları sağlayan bir uygulama oluşturmak:

- Kalıcı ücretsiz ve sınırsız kullanım
- Kararlı bağlantılar
- Tüm platformlar için destek
- Birden fazla proxy protokolü için destek
- Birden fazla şifreleme yöntemi için destek
- Mobil sürüm, resmi uygulama mağazaları dışında kurulum ve güncelleme yöntemleri sağlar

## 🤝 Katkıda Bulunun

Deneyimli geliştiricileri misyonumuza katılmaya davet ediyoruz. Görüşlerinizi paylaşın ve bu projeye katkıda bulunun:

- Öneriler için sorun açın
- Tartışmalara katılın
- Çekme istekleri gönderin

Daha iyi, ücretsiz bir internet hızlandırma çözümü oluşturmak için birlikte çalışalım!

## ⚖️ Sorumluluk Reddi

Bu proje yalnızca eğitim ve araştırma amaçlıdır. Kullanıcılar, bu kaynakları kullanırken yerel yasa ve düzenlemelere uymakla sorumludur.
