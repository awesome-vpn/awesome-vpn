[![Tiếng Việt](https://img.shields.io/badge/Ngôn%20ngữ-Tiếng%20Việt-red)](README_VI.md)
[![English](https://img.shields.io/badge/Language-English-red)](README.md)

## 🚀 Truy cập nhanh

1. Tìm kiếm và cài đặt [khách hàng mã nguồn mở](https://github.com/awesome-vpn/awesome-vpn/wiki/Clients) trên Github
2. Sao chép các liên kết đăng ký dưới đây vào khách hàng
3. Chọn một nút thích hợp và bắt đầu sử dụng

Liên kết dự án:
- [https://github.com/awesome-vpn/awesome-vpn](https://github.com/awesome-vpn/awesome-vpn)

## 📥 Liên kết Đăng ký

Liên kết đăng ký chính:
- https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all

Liên kết gương (Sử dụng nếu GitHub không ổn định):
- https://raw.kkgithub.com/awesome-vpn/awesome-vpn/master/all [Ưu tiên: Hồng Kông/Nhật Bản/Singapore]
- https://ghp.ci/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Ưu tiên: Nhật Bản/Hàn Quốc/Mỹ/Châu Âu]
- https://ghproxy.net/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Ưu tiên: Nhật Bản]

## 📊 Phân tích Giao thức VPN và Proxy

| Tầng OSI | Giao thức | Mô tả |
|----------|-----------|-------|
| Tầng 2 - Liên kết Dữ liệu | PPTP | Giao thức Tunneling Điểm-điểm, cũ hơn, bảo mật thấp |
| Tầng 2 - Liên kết Dữ liệu | L2TP | Giao thức Tunneling Tầng 2, thường được sử dụng với IPsec |
| Tầng 3 - Mạng | IPsec | Bảo mật Giao thức Internet, có thể được sử dụng với L2TP hoặc một mình |
| Tầng 3 - Mạng | WireGuard | Giao thức VPN mới hiệu quả, hiệu suất vượt trội |
| Tầng 3 - Mạng | GRE | Đóng gói Định tuyến Chung, có thể đóng gói nhiều giao thức tầng mạng khác nhau |
| Tầng 4 - Vận chuyển | TUIC | TCP qua UDP, giao thức tầng vận chuyển dựa trên QUIC |
| Tầng 4 - Vận chuyển | Hysteria | Giao thức vận chuyển mạng tốc độ cao dựa trên QUIC |
| Tầng 4 - Vận chuyển | Hysteria2 | Phiên bản cải tiến của Hysteria, hiệu quả và an toàn hơn |
| Tầng 4 - Vận chuyển | QUIC | Kết nối Internet UDP Nhanh, phát triển bởi Google |
| Tầng 5 - Phiên | SOCKS4 | Giao thức đơn giản để vượt qua tường lửa, không hỗ trợ xác thực |
| Tầng 5 - Phiên | SOCKS5 | Giao thức proxy phổ quát hỗ trợ xác thực và UDP |
| Tầng 5 - Phiên | SSL/TLS | Lớp Ổ cắm Bảo mật/Bảo mật Lớp Vận chuyển, cung cấp mã hóa cho tầng ứng dụng |
| Tầng 7 - Ứng dụng | OpenVPN | Hệ thống VPN sử dụng thư viện OpenSSL để mã hóa |
| Tầng 7 - Ứng dụng | Shadowsocks | Giao thức proxy mã hóa nhẹ |
| Tầng 7 - Ứng dụng | ShadowsocksR | Phiên bản mở rộng của Shadowsocks, thêm các tính năng như làm mờ |
| Tầng 7 - Ứng dụng | VMess | Giao thức truyền tải mã hóa dựa trên TLS, được đề xuất bởi dự án V2Ray |
| Tầng 7 - Ứng dụng | VLESS | Phiên bản đơn giản hóa của VMess, giảm chi phí mã hóa |
| Tầng 7 - Ứng dụng | Trojan | Giao thức proxy ngụy trang như lưu lượng HTTPS |
| Tầng 7 - Ứng dụng | Trojan-Go | Triển khai Go của giao thức Trojan, thêm các tính năng như WebSocket |
| Tầng 7 - Ứng dụng | Proxy HTTP | Loại proxy cơ bản nhất, thường không được mã hóa |
| Tầng 7 - Ứng dụng | Proxy HTTPS | Proxy HTTP mã hóa, cung cấp bảo mật tốt hơn |
| Tầng 7 - Ứng dụng | Tunneling SSH | Tạo các đường hầm mã hóa bằng cách sử dụng giao thức SSH |
| Tầng 7 - Ứng dụng | Tor | Mạng truyền thông ẩn danh, cung cấp quyền riêng tư cao thông qua mã hóa nhiều lớp và chuyển tiếp |
| Tầng 7 - Ứng dụng | Naive | Giao thức proxy HTTPS dựa trên ngăn xếp mạng Chromium |
| Tầng 7 - Ứng dụng | Brook | Giao thức proxy đơn giản đa nền tảng |
| Tầng 7 - Ứng dụng | Shadowtls | Giao thức ngụy trang lưu lượng Shadowsocks như lưu lượng TLS |
| Tầng 7 - Ứng dụng | Reality | Giao thức proxy mới dựa trên TLS 1.3, cung cấp khả năng chống phát hiện tốt hơn |
| Tầng 7 - Ứng dụng | WebSocket | Giao thức cung cấp giao tiếp full-duplex trên một kết nối TCP duy nhất |

## ⚠️ Thách thức Hiện tại

Nhiều khách hàng VPN một cú nhấp chuột gặp phải các vấn đề sau:
- Vấn đề kết nối do tên miền/IP bị chặn
- Không có sẵn trong các cửa hàng ứng dụng
- Thanh toán bắt buộc hoặc thử nghiệm giới hạn thời gian

## 🔬 Sứ mệnh của Chúng tôi

Chúng tôi đang nghiên cứu các khách hàng VPN lâu đời để phát triển một giải pháp miễn phí và đáng tin cậy đa nền tảng. Mục tiêu của chúng tôi là tạo ra một ứng dụng cung cấp:

- Sử dụng miễn phí và không giới hạn vĩnh viễn
- Kết nối ổn định
- Hỗ trợ cho tất cả các nền tảng
- Hỗ trợ cho nhiều giao thức proxy
- Hỗ trợ cho nhiều phương pháp mã hóa
- Phiên bản di động cung cấp các phương pháp cài đặt và cập nhật ngoài các cửa hàng ứng dụng chính thức

## ⚖️ Tuyên bố Miễn trừ

Dự án này chỉ dành cho mục đích giáo dục và nghiên cứu. Người dùng chịu trách nhiệm tuân thủ luật pháp và quy định địa phương khi sử dụng các tài nguyên này.
