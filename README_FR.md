[![Français](https://img.shields.io/badge/Langue-Français-red)](README_FR.md)
[![English](https://img.shields.io/badge/Language-English-red)](README.md)

## 🚀 Démarrage Rapide

1. Recherchez et installez des [clients open source](https://github.com/awesome-vpn/awesome-vpn/wiki/Clients) sur Github
2. Copiez les liens d'abonnement ci-dessous dans le client
3. Sélectionnez le nœud approprié pour commencer à utiliser

Lien du projet:
- [https://github.com/awesome-vpn/awesome-vpn](https://github.com/awesome-vpn/awesome-vpn)

## 📥 Liens d'Abonnement

Lien d'abonnement principal:
- https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all

Liens miroirs (Utilisez si GitHub est instable):
- https://raw.kkgithub.com/awesome-vpn/awesome-vpn/master/all [Optimisé pour: Hong Kong/Japon/Singapour]
- https://ghp.ci/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Optimisé pour: Japon/Corée/USA/Europe]
- https://ghproxy.net/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Optimisé pour: Japon]

## 📊 Analyse des Protocoles VPN et Proxy

| Couche OSI | Protocole | Description |
|------------|-----------|-------------|
| Couche 2 - Liaison de Données | PPTP | Protocole de Tunneling Point-à-Point, ancien, faible sécurité |
| Couche 2 - Liaison de Données | L2TP | Protocole de Tunneling de Couche 2, souvent utilisé avec IPsec |
| Couche 3 - Réseau | IPsec | Sécurité du Protocole Internet, peut être utilisé avec L2TP ou seul |
| Couche 3 - Réseau | WireGuard | Nouveau protocole VPN efficace, performance supérieure |
| Couche 3 - Réseau | GRE | Encapsulation de Routage Générique, peut encapsuler divers protocoles de couche réseau |
| Couche 4 - Transport | TUIC | TCP sur UDP, protocole de transport basé sur QUIC |
| Couche 4 - Transport | Hysteria | Protocole de transport réseau à haute vitesse basé sur QUIC |
| Couche 4 - Transport | Hysteria2 | Version améliorée de Hysteria, plus efficace et sécurisée |
| Couche 4 - Transport | QUIC | Connexions Internet UDP rapides, développé par Google |
| Couche 5 - Session | SOCKS4 | Protocole simple de traversée de pare-feu, sans support d'authentification |
| Couche 5 - Session | SOCKS5 | Protocole proxy universel qui supporte l'authentification et UDP |
| Couche 5 - Session | SSL/TLS | Couche de Sockets Sécurisés/Sécurité de la Couche de Transport, fournit le chiffrement pour la couche application |
| Couche 7 - Application | OpenVPN | Système VPN qui utilise la bibliothèque OpenSSL pour le chiffrement |
| Couche 7 - Application | Shadowsocks | Protocole proxy chiffré léger |
| Couche 7 - Application | ShadowsocksR | Version étendue de Shadowsocks, ajoute des fonctionnalités comme l'obfuscation |
| Couche 7 - Application | VMess | Protocole de transmission chiffrée basé sur TLS, proposé par le projet V2Ray |
| Couche 7 - Application | VLESS | Version simplifiée de VMess, réduit la surcharge de chiffrement |
| Couche 7 - Application | Trojan | Protocole proxy qui se déguise en trafic HTTPS |
| Couche 7 - Application | Trojan-Go | Implémentation Go du protocole Trojan, ajoute des fonctionnalités comme WebSocket |
| Couche 7 - Application | Proxy HTTP | Type de proxy le plus basique, généralement non chiffré |
| Couche 7 - Application | Proxy HTTPS | Proxy HTTP chiffré, fournit une meilleure sécurité |
| Couche 7 - Application | Tunnel SSH | Crée des tunnels chiffrés en utilisant le protocole SSH |
| Couche 7 - Application | Tor | Réseau de communication anonyme, fournit une haute confidentialité grâce au chiffrement multi-couches et au relais |
| Couche 7 - Application | Naive | Protocole proxy HTTPS basé sur la pile réseau Chromium |
| Couche 7 - Application | Brook | Protocole proxy simple multiplateforme |
| Couche 7 - Application | Shadowtls | Protocole qui déguise le trafic Shadowsocks en trafic TLS |
| Couche 7 - Application | Reality | Nouveau protocole proxy basé sur TLS 1.3, fournit une meilleure capacité anti-détection |
| Couche 7 - Application | WebSocket | Protocole qui fournit une communication full-duplex sur une seule connexion TCP |

## ⚠️ Défis Actuels

De nombreux clients VPN en un clic rencontrent les problèmes suivants:
- Problèmes de connexion dus à des domaines/IP bloqués
- Indisponibilité dans les magasins d'applications
- Paiements forcés ou essais limités dans le temps

## 🔬 Notre Mission

Nous recherchons des clients VPN de longue date pour développer une solution gratuite et fiable multiplateforme. Notre objectif est de créer une application qui fournit:

- Utilisation gratuite et illimitée de manière permanente
- Connexions stables
- Support pour toutes les plateformes
- Support pour plusieurs protocoles proxy
- Support pour plusieurs méthodes de chiffrement
- La version mobile fournit des méthodes d'installation et de mise à jour en dehors des magasins d'applications officiels

## ⚖️ Avertissement

Ce projet est uniquement à des fins éducatives et de recherche. Les utilisateurs sont responsables de se conformer aux lois et règlements locaux lors de l'utilisation de ces ressources.
