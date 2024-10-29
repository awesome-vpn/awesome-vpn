[![Español](https://img.shields.io/badge/Idioma-Español-red)](README_ES.md)
[![English](https://img.shields.io/badge/Language-English-red)](README.md)

## 🚀 Inicio Rápido

1. Busque e instale un [cliente de código abierto](https://github.com/awesome-vpn/awesome-vpn/wiki/Clients) en Github
2. Copie los enlaces de suscripción siguientes en el cliente
3. Seleccione un nodo apropiado y comience a usarlo

Enlace del proyecto:
- [https://github.com/awesome-vpn/awesome-vpn](https://github.com/awesome-vpn/awesome-vpn)

## 📥 Enlaces de Suscripción

Enlace de suscripción principal:
- https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all

Enlaces espejo (Si GitHub es inestable):
- https://raw.kkgithub.com/awesome-vpn/awesome-vpn/master/all [Optimizado para: Hong Kong/Japón/Singapur]
- https://ghp.ci/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Optimizado para: Japón/Corea/EE.UU./Europa]
- https://ghproxy.net/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Optimizado para: Japón]

## 📊 Análisis de Protocolos VPN y Proxy

| Capa OSI | Protocolo | Descripción |
|----------|-----------|-------------|
| Capa 2 - Enlace de Datos | PPTP | Protocolo de Túnel Punto a Punto, más antiguo, baja seguridad |
| Capa 2 - Enlace de Datos | L2TP | Protocolo de Túnel de Capa 2, a menudo usado con IPsec |
| Capa 3 - Red | IPsec | Seguridad de Protocolo de Internet, puede usarse con L2TP o solo |
| Capa 3 - Red | WireGuard | Nuevo protocolo VPN eficiente, rendimiento superior |
| Capa 3 - Red | GRE | Encapsulación de Enrutamiento Genérico, puede encapsular varios protocolos de capa de red |
| Capa 4 - Transporte | TUIC | TCP sobre UDP, protocolo de capa de transporte basado en QUIC |
| Capa 4 - Transporte | Hysteria | Protocolo de transporte de red de alta velocidad basado en QUIC |
| Capa 4 - Transporte | Hysteria2 | Versión mejorada de Hysteria, más eficiente y segura |
| Capa 4 - Transporte | QUIC | Conexiones Rápidas de Internet UDP, desarrollado por Google |
| Capa 5 - Sesión | SOCKS4 | Protocolo simple de paso de firewall, sin soporte de autenticación |
| Capa 5 - Sesión | SOCKS5 | Protocolo de proxy universal que soporta autenticación y UDP |
| Capa 5 - Sesión | SSL/TLS | Capa de Sockets Seguros/Seguridad de Capa de Transporte, proporciona cifrado para la capa de aplicación |
| Capa 7 - Aplicación | OpenVPN | Sistema VPN que utiliza la biblioteca OpenSSL para cifrado |
| Capa 7 - Aplicación | Shadowsocks | Protocolo de proxy cifrado ligero |
| Capa 7 - Aplicación | ShadowsocksR | Versión extendida de Shadowsocks, añade características como ofuscación |
| Capa 7 - Aplicación | VMess | Protocolo de transmisión cifrada basado en TLS, propuesto por el proyecto V2Ray |
| Capa 7 - Aplicación | VLESS | Versión simplificada de VMess, reduce la sobrecarga de cifrado |
| Capa 7 - Aplicación | Trojan | Protocolo de proxy que se disfraza como tráfico HTTPS |
| Capa 7 - Aplicación | Trojan-Go | Implementación en Go del protocolo Trojan, añade características como WebSocket |
| Capa 7 - Aplicación | Proxy HTTP | Tipo de proxy más básico, generalmente no cifrado |
| Capa 7 - Aplicación | Proxy HTTPS | Proxy HTTP cifrado, proporciona mejor seguridad |
| Capa 7 - Aplicación | Túnel SSH | Crea túneles cifrados usando el protocolo SSH |
| Capa 7 - Aplicación | Tor | Red de comunicación anónima, proporciona alta privacidad a través de cifrado de múltiples capas y retransmisión |
| Capa 7 - Aplicación | Naive | Protocolo de proxy HTTPS basado en la pila de red de Chromium |
| Capa 7 - Aplicación | Brook | Protocolo de proxy simple multiplataforma |
| Capa 7 - Aplicación | Shadowtls | Protocolo que disfraza el tráfico de Shadowsocks como tráfico TLS |
| Capa 7 - Aplicación | Reality | Nuevo protocolo de proxy basado en TLS 1.3, proporciona mejor capacidad anti-detección |
| Capa 7 - Aplicación | WebSocket | Protocolo que proporciona comunicación full-duplex en una sola conexión TCP |

## ⚠️ Desafíos Actuales

Muchos clientes VPN de un clic enfrentan los siguientes problemas:
- Problemas de conexión debido a dominios/IPs bloqueados
- No disponibilidad en las tiendas de aplicaciones
- Pagos forzados o pruebas limitadas en tiempo

## 🔬 Nuestra Misión

Estamos investigando clientes VPN de larga data para desarrollar una solución gratuita y confiable multiplataforma. Nuestro objetivo es crear una aplicación que proporcione:

- Uso gratuito y sin límites de forma permanente
- Conexiones estables
- Soporte para todas las plataformas
- Soporte para múltiples protocolos de proxy
- Soporte para múltiples métodos de cifrado
- La versión móvil proporciona métodos de instalación y actualización fuera de las tiendas de aplicaciones oficiales

## ⚖️ Descargo de Responsabilidad

Este proyecto es solo para fines educativos e investigativos. Los usuarios son responsables de cumplir con las leyes y regulaciones locales al usar estos recursos.
