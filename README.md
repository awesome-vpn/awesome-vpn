# Awesome VPN 🌍

**Free proxy nodes, updated daily. Zero config, copy and use.**

🌐 **Quick Copy:** https://awesome-vpn.github.io/

<div align="center">

[![English](https://img.shields.io/badge/Language-English-green?style=for-the-badge&logo=markdown)](README.md)
[![简体中文](https://img.shields.io/badge/语言-简体中文-blue?style=for-the-badge&logo=markdown)](README_CN.md)

</div>

---

## 🚀 30-Second Quick Start

### Step 1: Copy a subscription link

Right-click the link → "Copy link address":

| Format | Subscription Link | Best For |
|--------|-------------------|----------|
| **Clash YAML** | [`https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/clash.yaml`](https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/clash.yaml) | Clash Verge Rev |
| **Sing-box JSON** | [`https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/sing-box.json`](https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/sing-box.json) | Sing-box, NekoBox |
| **Base64 List** | [`https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all`](https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/master/all) | v2rayN, v2rayNG |

> 💡 **Tip:** We recommend **Clash YAML** (with Clash Verge Rev) or **Sing-box JSON**. After importing, simply select the **"Auto"** group to let your client automatically route through the lowest-latency responsive node in your local network.


### Step 2: Download a client app

> 🛡️ **Inclusion Policy:** This project exclusively recommends clients that are **100% open-source and 100% free (zero ads / zero paywalls)**. Paid commercial or closed-source software is strictly excluded.

| Platform | Recommended Client | Official Download & Repo |
|----------|-------------------|--------------------------|
| **Windows** | Clash Verge Rev / v2rayN | [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev/releases) / [v2rayN](https://github.com/2dust/v2rayN/releases) |
| **macOS** | Clash Verge Rev | [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev/releases) |
| **Linux** | Clash Verge Rev | [Clash Verge Rev](https://github.com/clash-verge-rev/clash-verge-rev/releases) |
| **Android** | v2rayNG / NekoBox | [v2rayNG](https://github.com/2dust/v2rayNG/releases) / [NekoBox](https://github.com/MatsuriDayo/NekoBoxForAndroid/releases) |
| **iOS** | | |

### Step 3: Paste and connect

1. Open your client app
2. Find "Subscription" or "Import" button
3. Paste the link from Step 1
4. Click "Update" or "Download"
5. Select a server and click "Connect"

---

## 📥 Subscription Links (Mirror)

If GitHub is slow or inaccessible in your region, use the official jsDelivr CDN mirror:

| Format | Subscription Link (jsDelivr CDN) | Best For |
|--------|----------------------------------|----------|
| **Clash YAML** | [`https://cdn.jsdelivr.net/gh/awesome-vpn/awesome-vpn@master/clash.yaml`](https://cdn.jsdelivr.net/gh/awesome-vpn/awesome-vpn@master/clash.yaml) | Clash Verge Rev |
| **Sing-box JSON** | [`https://cdn.jsdelivr.net/gh/awesome-vpn/awesome-vpn@master/sing-box.json`](https://cdn.jsdelivr.net/gh/awesome-vpn/awesome-vpn@master/sing-box.json) | Sing-box, NekoBox |
| **Base64 List** | [`https://cdn.jsdelivr.net/gh/awesome-vpn/awesome-vpn@master/all`](https://cdn.jsdelivr.net/gh/awesome-vpn/awesome-vpn@master/all) | v2rayN, v2rayNG |

---

## ❓ Frequently Asked Questions

### Q: Is this free?
**Yes.** All nodes are collected from public sources. No payment required.

### Q: Why doesn't it work?
Possible reasons:
- **Node expired**: Wait for the next daily update (UTC 00:00)
- **Network blocked**: Try a different mirror link
- **Client issue**: Make sure you're using the correct format (Base64 List/Sing-box JSON/Clash YAML)

### Q: Is it safe?
- These are **public nodes** from the internet
- **Do not use for sensitive activities** (banking, private accounts)
- We don't log your traffic, but public nodes might

### Q: How often is it updated?
**Daily at 00:00 UTC** (~8:00 AM Beijing time)

### Q: Which format should I use?
| If your app is... | Use this format |
|-------------------|-----------------|
| Clash Verge Rev | **Clash YAML** |
| Sing-box, NekoBox | **Sing-box JSON** |
| v2rayN, v2rayNG | **Base64 List** |

---

## 🛠️ Troubleshooting

**"Failed to fetch subscription"**
→ Try the mirror links above, or enable "System Proxy" in your client first.

**"Connected but no internet"**
→ The node might be dead. Click "Update" to get fresh nodes, or try another server.

**"Slow speed"**
→ Public nodes are shared by many users. Try different servers until you find a fast one.

---

## 📱 Client Setup Guides

<details>
<summary><b>Clash Verge Rev (Windows / macOS / Linux)</b></summary>

1. Download and install from [GitHub Releases](https://github.com/clash-verge-rev/clash-verge-rev/releases)
2. Paste the **Clash YAML** link in "Profiles / Subscriptions", or use one-click import on our [Website](https://awesome-vpn.github.io/)
3. Click "Save & Import" to download the node list
4. In the "Proxies" panel, select a low-latency server
5. Toggle "System Proxy" or "TUN Mode" on to connect
</details>

<details>
<summary><b>NekoBox (Android)</b></summary>

1. Download from [GitHub Releases](https://github.com/MatsuriDayo/NekoBoxForAndroid/releases)
2. Open NekoBox, tap the top menu (⋮) → select **New Profile** / **Import from URL**
3. Paste the **Sing-box JSON** or **Base64 List** subscription link
4. Tap to update the subscription group, choose a proxy, and tap the **Connect** floating button
</details>

<details>
<summary><b>v2rayN (Windows)</b></summary>

1. Download from [GitHub releases](https://github.com/2dust/v2rayN/releases)
2. Extract and run `v2rayN.exe`
3. Click **Subscription** → **Subscription Settings**
4. Paste the Base64 List link, click **Add** → **OK**
5. Click **Subscription** → **Update Subscription**
6. Right-click a server → **Set as active server**
7. Click **System Proxy** → **Auto configure system proxy**
</details>

<details>
<summary><b>v2rayNG (Android)</b></summary>

1. Download from [GitHub releases](https://github.com/2dust/v2rayNG/releases)
2. Tap **+** button → **Import from URL**
3. Paste the Base64 List link, tap **Import**
4. Tap the menu (⋮) → **Update subscription**
5. Tap a server to select it
6. Tap the **V** button to connect
</details>

---

## 🔄 Update Schedule

| Action | Time (UTC) | Time (Beijing) |
|--------|-----------|----------------|
| Auto-update | 00:00 daily | 08:00 daily |
| Manual trigger | Anytime | Anytime (via GitHub Actions) |

---

## ⚖️ Disclaimer

- This project aggregates **publicly available** proxy nodes
- **For educational and research purposes only**
- Users are responsible for complying with local laws
- **No warranty provided** - nodes may stop working anytime
- We do not own or control these nodes

---

## 🌟 Star History

If this project helps you, please ⭐ star it!

[![Star History Chart](https://api.star-history.com/svg?repos=awesome-vpn/awesome-vpn&type=Date)](https://star-history.com/#awesome-vpn/awesome-vpn&Date)

---

<p align="center">
  <b>Free Internet for Everyone 🌐</b>
</p>
