[![Italiano](https://img.shields.io/badge/Lingua-Italiano-red)](README_IT.md)
[![English](https://img.shields.io/badge/Language-English-red)](README.md)

## 🚀 Avvio Rapido

1. Cerca e installa [client open source](https://github.com/awesome-vpn/awesome-vpn/wiki/Clients) su Github
2. Copia i link di sottoscrizione qui sotto nel client
3. Seleziona il nodo appropriato e inizia a usare

Link del progetto:
- [https://github.com/awesome-vpn/awesome-vpn](https://github.com/awesome-vpn/awesome-vpn)

## 📥 Link di Sottoscrizione

Link di sottoscrizione principale:
- https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all

Link specchio (Usa se GitHub è instabile):
- https://raw.kkgithub.com/awesome-vpn/awesome-vpn/master/all [Ottimizzato per: Hong Kong/Giappone/Singapore]
- https://ghp.ci/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Ottimizzato per: Giappone/Corea/USA/Europa]
- https://ghproxy.net/https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all [Ottimizzato per: Giappone]

## 📊 Analisi dei Protocolli VPN e Proxy

| Livello OSI | Protocollo | Descrizione |
|-------------|------------|-------------|
| Livello 2 - Collegamento Dati | PPTP | Protocollo di Tunneling Punto-a-Punto, vecchio, bassa sicurezza |
| Livello 2 - Collegamento Dati | L2TP | Protocollo di Tunneling di Livello 2, spesso usato con IPsec |
| Livello 3 - Rete | IPsec | Sicurezza del Protocollo Internet, può essere usato con L2TP o da solo |
| Livello 3 - Rete | WireGuard | Nuovo protocollo VPN efficiente, prestazioni superiori |
| Livello 3 - Rete | GRE | Incapsulamento di Routing Generico, può incapsulare vari protocolli di rete |
| Livello 4 - Trasporto | TUIC | TCP su UDP, protocollo di trasporto basato su QUIC |
| Livello 4 - Trasporto | Hysteria | Protocollo di trasporto di rete ad alta velocità basato su QUIC |
| Livello 4 - Trasporto | Hysteria2 | Versione migliorata di Hysteria, più efficiente e sicura |
| Livello 4 - Trasporto | QUIC | Connessioni Internet UDP veloci, sviluppato da Google |
| Livello 5 - Sessione | SOCKS4 | Protocollo semplice di attraversamento firewall, senza supporto di autenticazione |
| Livello 5 - Sessione | SOCKS5 | Protocollo proxy universale che supporta autenticazione e UDP |
| Livello 5 - Sessione | SSL/TLS | Livello di Sicurezza dei Socket/Trasporto, fornisce crittografia per il livello applicativo |
| Livello 7 - Applicazione | OpenVPN | Sistema VPN che utilizza la libreria OpenSSL per la crittografia |
| Livello 7 - Applicazione | Shadowsocks | Protocollo proxy crittografato leggero |
| Livello 7 - Applicazione | ShadowsocksR | Versione estesa di Shadowsocks, aggiunge funzionalità come l'offuscamento |
| Livello 7 - Applicazione | VMess | Protocollo di trasmissione crittografata basato su TLS, proposto dal progetto V2Ray |
| Livello 7 - Applicazione | VLESS | Versione semplificata di VMess, riduce il sovraccarico di crittografia |
| Livello 7 - Applicazione | Trojan | Protocollo proxy che si maschera come traffico HTTPS |
| Livello 7 - Applicazione | Trojan-Go | Implementazione Go del protocollo Trojan, aggiunge funzionalità come WebSocket |
| Livello 7 - Applicazione | Proxy HTTP | Tipo di proxy più basilare, generalmente non crittografato |
| Livello 7 - Applicazione | Proxy HTTPS | Proxy HTTP crittografato, fornisce maggiore sicurezza |
| Livello 7 - Applicazione | Tunnel SSH | Crea tunnel crittografati usando il protocollo SSH |
| Livello 7 - Applicazione | Tor | Rete di comunicazione anonima, fornisce alta privacy attraverso crittografia multilivello e inoltro |
| Livello 7 - Applicazione | Naive | Protocollo proxy HTTPS basato sullo stack di rete Chromium |
| Livello 7 - Applicazione | Brook | Protocollo proxy semplice multipiattaforma |
| Livello 7 - Applicazione | Shadowtls | Protocollo che maschera il traffico di Shadowsocks come traffico TLS |
| Livello 7 - Applicazione | Reality | Nuovo protocollo proxy basato su TLS 1.3, fornisce migliore capacità anti-rilevamento |
| Livello 7 - Applicazione | WebSocket | Protocollo che fornisce comunicazione full-duplex su una singola connessione TCP |

## ⚠️ Sfide Attuali

Molti client VPN one-click affrontano i seguenti problemi:
- Problemi di connessione a causa di domini/IP bloccati
- Indisponibilità nei negozi di app
- Pagamenti forzati o prove a tempo limitato

## 🔬 La Nostra Missione

Stiamo ricercando client VPN di lunga data per sviluppare una soluzione gratuita e affidabile multipiattaforma. Il nostro obiettivo è creare un'applicazione che fornisca:

- Uso gratuito e illimitato in modo permanente
- Connessioni stabili
- Supporto per tutte le piattaforme
- Supporto per più protocolli proxy
- Supporto per più metodi di crittografia
- La versione mobile fornisce metodi di installazione e aggiornamento al di fuori dei negozi di app ufficiali

## ⚖️ Disclaimer

Questo progetto è solo per scopi educativi e di ricerca. Gli utenti sono responsabili di rispettare le leggi e i regolamenti locali quando utilizzano queste risorse.
