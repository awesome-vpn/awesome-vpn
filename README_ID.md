[![Bahasa Indonesia](https://img.shields.io/badge/Bahasa-Indonesia-red)](README_ID.md)
[![English](https://img.shields.io/badge/Language-English-red)](README.md)

## 🚀 Mulai Cepat

1. Cari dan instal [klien sumber terbuka](https://github.com/awesome-vpn/awesome-vpn/wiki/Clients) di Github
2. Salin tautan langganan di bawah ini ke klien
3. Pilih node yang sesuai untuk mulai menggunakan

Tautan proyek:
- [https://github.com/awesome-vpn/awesome-vpn](https://github.com/awesome-vpn/awesome-vpn)

## 📥 Tautan Langganan

Tautan langganan utama:
- https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all

Tautan cermin (gunakan jika GitHub tidak stabil):
- https://raw.kkgithub.com/awesome-vpn/awesome-vpn/master/all [Diutamakan: Hong Kong/Jepang/Singapura]
- https://ghp.ci/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Diutamakan: Jepang/Korea/USA/Eropa]
- https://ghproxy.net/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Diutamakan: Jepang]

## 📊 Analisis Protokol VPN dan Proxy

| Lapisan OSI | Protokol | Deskripsi |
|-------------|----------|-----------|
| Lapisan 2 - Data Link | PPTP | Protokol Tunneling Point-to-Point, lebih tua, keamanan rendah |
| Lapisan 2 - Data Link | L2TP | Protokol Tunneling Lapisan 2, sering digunakan dengan IPsec |
| Lapisan 3 - Jaringan | IPsec | Keamanan Protokol Internet, dapat digunakan dengan L2TP atau sendiri |
| Lapisan 3 - Jaringan | WireGuard | Protokol VPN baru yang efisien, kinerja superior |
| Lapisan 3 - Jaringan | GRE | Enkapsulasi Routing Generik, dapat mengenkapsulasi berbagai protokol lapisan jaringan |
| Lapisan 4 - Transportasi | TUIC | TCP over UDP, protokol lapisan transportasi berbasis QUIC |
| Lapisan 4 - Transportasi | Hysteria | Protokol transportasi jaringan berkecepatan tinggi berbasis QUIC |
| Lapisan 4 - Transportasi | Hysteria2 | Versi perbaikan dari Hysteria, lebih efisien dan aman |
| Lapisan 4 - Transportasi | QUIC | Koneksi Internet UDP Cepat, dikembangkan oleh Google |
| Lapisan 5 - Sesi | SOCKS4 | Protokol traversal firewall sederhana, tidak mendukung otentikasi |
| Lapisan 5 - Sesi | SOCKS5 | Protokol proxy universal yang mendukung otentikasi dan UDP |
| Lapisan 5 - Sesi | SSL/TLS | Lapisan Soket Aman/Keamanan Lapisan Transportasi, menyediakan enkripsi untuk lapisan aplikasi |
| Lapisan 7 - Aplikasi | OpenVPN | Sistem VPN menggunakan perpustakaan OpenSSL untuk enkripsi |
| Lapisan 7 - Aplikasi | Shadowsocks | Protokol proxy terenkripsi ringan |
| Lapisan 7 - Aplikasi | ShadowsocksR | Versi diperluas dari Shadowsocks, menambahkan fitur seperti obfuscation |
| Lapisan 7 - Aplikasi | VMess | Protokol transmisi terenkripsi berbasis TLS, diusulkan oleh proyek V2Ray |
| Lapisan 7 - Aplikasi | VLESS | Versi sederhana dari VMess, mengurangi overhead enkripsi |
| Lapisan 7 - Aplikasi | Trojan | Protokol proxy yang menyamar sebagai lalu lintas HTTPS |
| Lapisan 7 - Aplikasi | Trojan-Go | Implementasi Go dari protokol Trojan, menambahkan fitur seperti WebSocket |
| Lapisan 7 - Aplikasi | HTTP Proxy | Jenis proxy paling dasar, biasanya tidak terenkripsi |
| Lapisan 7 - Aplikasi | HTTPS Proxy | Proxy HTTP terenkripsi, menyediakan keamanan yang lebih baik |
| Lapisan 7 - Aplikasi | SSH Tunnel | Membuat terowongan terenkripsi menggunakan protokol SSH |
| Lapisan 7 - Aplikasi | Tor | Jaringan komunikasi anonim, menyediakan privasi tinggi melalui enkripsi multi-lapisan dan relai |
| Lapisan 7 - Aplikasi | Naive | Protokol proxy HTTPS berbasis tumpukan jaringan Chromium |
| Lapisan 7 - Aplikasi | Brook | Protokol proxy lintas platform sederhana |
| Lapisan 7 - Aplikasi | Shadowtls | Protokol yang menyamarkan lalu lintas Shadowsocks sebagai lalu lintas TLS |
| Lapisan 7 - Aplikasi | Reality | Protokol proxy baru berbasis TLS 1.3, menyediakan kemampuan anti-deteksi yang lebih baik |
| Lapisan 7 - Aplikasi | WebSocket | Protokol yang menyediakan komunikasi full-duplex pada satu koneksi TCP |

## ⚠️ Tantangan Saat Ini

Banyak klien VPN satu klik menghadapi masalah berikut:
- Masalah koneksi karena domain/IP yang diblokir
- Tidak tersedia di toko aplikasi
- Pembayaran paksa atau uji coba terbatas

## 🔬 Misi Kami

Kami sedang meneliti klien VPN yang sudah lama ada untuk mengembangkan solusi lintas platform yang gratis dan andal. Tujuan kami adalah membuat aplikasi yang menyediakan:

- Penggunaan gratis dan tak terbatas secara permanen
- Koneksi yang stabil
- Dukungan untuk semua platform
- Dukungan untuk berbagai protokol proxy
- Dukungan untuk berbagai metode enkripsi
- Versi seluler menyediakan metode instalasi dan pembaruan di luar toko aplikasi resmi

## ⚖️ Penafian

Proyek ini hanya untuk tujuan pendidikan dan penelitian. Pengguna bertanggung jawab untuk mematuhi hukum dan peraturan setempat saat menggunakan sumber daya ini.
