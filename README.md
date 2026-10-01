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


## 🌐 Web Resources & Aesthetic Symbols Index
- [SYM 1D409](https://baroque-aesthetic-symbols-59.pages.dev/symbol/sym-1d409/)
- [RIGHT MATHEMATICAL WHITE SQUARE BRACKET](https://sleek-dot-symbols-31.pages.dev/symbol/right-mathematical-white-square-bracket/)
- [SYM 1F611](https://scholarly-runes-text-68.pages.dev/symbol/sym-1f611/)
- [WHITE HEART](https://lace-bow-symbols-18.pages.dev/symbol/white-heart/)
- [SYM 1F632](https://gothic-bio-fonts-26.pages.dev/symbol/sym-1f632/)
- [SYM 263A](https://anime-sparkle-text-14.pages.dev/symbol/sym-263a/)
- [SYM 1D403](https://dolly-angel-fonts-14.pages.dev/symbol/sym-1d403/)
- [SYM 1F60E](https://zen-unicode-symbols-89.pages.dev/symbol/sym-1f60e/)
- [SYM 2742](https://vintage-script-symbols-65.pages.dev/symbol/sym-2742/)
- [SYM 2637](https://zen-unicode-symbols-89.pages.dev/symbol/sym-2637/)
- [SYM 2634](https://theeduplaycampen.pages.dev/symbol/sym-2634/)
- [SYM 1D448](https://kawaii-kaomoji-hub-80.pages.dev/symbol/sym-1d448/)
- [STARS](https://aesthetic-spacing-fonts-10.pages.dev/es/stars/)
- [BORDERS DIVIDERS](https://anime-sparkle-text-14.pages.dev/pt/borders-dividers/)
- [MUSIC SHARP SIGN](https://zen-unicode-symbols-89.pages.dev/symbol/music-sharp-sign/)
- [SYM 26BE](https://neon-futuristic-symbols-58.pages.dev/symbol/sym-26be/)
- [SYM 1F629](https://anime-sparkle-text-73.pages.dev/symbol/sym-1f629/)
- [SYM 1F609](https://zen-unicode-symbols-89.pages.dev/symbol/sym-1f609/)
- [SYM 1D403](https://aesthetic-spacing-fonts-10.pages.dev/symbol/sym-1d403/)
- [RIGHT MATHEMATICAL WHITE SQUARE BRACKET](https://daintystar-font-studio-48.pages.dev/symbol/right-mathematical-white-square-bracket/)
- [SYM 1F479](https://minimal-star-symbols-91.pages.dev/symbol/sym-1f479/)
- [SYM 26D6](https://modern-bullet-symbols-45.pages.dev/symbol/sym-26d6/)
- [SYM 1D419](https://vintage-script-symbols-65.pages.dev/symbol/sym-1d419/)
- [SYM 265D](https://theeduplaycampen.pages.dev/symbol/sym-265d/)
- [SYM 1D4A2](https://anime-sparkle-text-73.pages.dev/symbol/sym-1d4a2/)
- [SYM 2642](https://coquette-aesthetic-symbols-62.pages.dev/symbol/sym-2642/)
- [ZODIAC CELESTIAL](https://sleek-arrow-symbols-42.pages.dev/es/zodiac-celestial/)
- [SYM 26BD](https://techno-hacker-text-43.pages.dev/symbol/sym-26bd/)
- [COQUETTE BOW RIBBON](https://minimal-star-symbols-26.pages.dev/symbol/coquette-bow-ribbon/)
- [NATURE FLOWERS](https://glitch-font-studio-46.pages.dev/ru/nature-flowers/)
- [SYM 26B2](https://techno-hacker-text-43.pages.dev/symbol/sym-26b2/)
- [NATURE FLOWERS](https://fairy-lace-symbols-92.pages.dev/ja/nature-flowers/)
- [FLORAL BRANCH BOUQUET](https://cyber-clan-tags-69.pages.dev/symbol/floral-branch-bouquet/)
- [FIRST QUARTER WAXING MOON](https://gothic-bio-fonts-69.pages.dev/symbol/first-quarter-waxing-moon/)
- [SYM 273D](https://techno-hacker-text-43.pages.dev/symbol/sym-273d/)
- [KAOMOJI](https://techno-hacker-text-43.pages.dev/es/kaomoji/)
- [SYM 1D472](https://kawaii-kaomoji-hub-80.pages.dev/symbol/sym-1d472/)
- [TAURUS ZODIAC BULL](https://techno-hacker-text-43.pages.dev/symbol/taurus-zodiac-bull/)
- [VIRGO ZODIAC MAIDEN](https://techno-hacker-text-43.pages.dev/symbol/virgo-zodiac-maiden/)
- [SYM 1F642 200D 2195 FE0F](https://minimal-star-symbols-26.pages.dev/symbol/sym-1f642-200d-2195-fe0f/)
- [SYM 1F61F](https://zen-unicode-hub-94.pages.dev/symbol/sym-1f61f/)
- [SYM 1D431](https://minimal-star-symbols-87.pages.dev/symbol/sym-1d431/)
- [INSTAGRAM BIO](https://zen-unicode-hub-94.pages.dev/es/instagram-bio/)
- [SYM 1F644](https://vintage-angel-text-38.pages.dev/symbol/sym-1f644/)
- [TRENDING](https://coquette-heart-text-40.pages.dev/trending/)
- [SYM 1F610](https://modern-bullet-symbols-45.pages.dev/symbol/sym-1f610/)
- [SYM 2656](https://cyber-clan-tags-36.pages.dev/symbol/sym-2656/)
- [SYM 1D44F](https://coquette-aesthetic-symbols-63.pages.dev/symbol/sym-1d44f/)
- [SYM 1D439](https://neon-matrix-symbols-94.pages.dev/symbol/sym-1d439/)
- [STARS](https://neon-futuristic-symbols-58.pages.dev/pt/stars/)
- [BRACKETS](https://cyber-clan-tags-69.pages.dev/vi/brackets/)
- [SYM 1D476](https://dolly-angel-fonts-14.pages.dev/symbol/sym-1d476/)
- [SYM 1D419](https://cyber-clan-tags-36.pages.dev/symbol/sym-1d419/)
- [BLACK CENTRE STAR](https://ribbon-bow-unicode-18.pages.dev/symbol/black-centre-star/)
- [BORDERS DIVIDERS](https://minimal-star-symbols-26.pages.dev/vi/borders-dividers/)
- [SYM 1F480](https://zen-unicode-symbols-89.pages.dev/symbol/sym-1f480/)
- [SYM 265B](https://glitch-font-studio-46.pages.dev/symbol/sym-265b/)
- [SYM 1D467](https://neon-hacker-text-25.pages.dev/symbol/sym-1d467/)
- [SYM 260C](https://fairy-lace-symbols-92.pages.dev/symbol/sym-260c/)
- [SYM 26C4](https://chibi-kaomoji-vault-58.pages.dev/symbol/sym-26c4/)
- [SYM 1F634](https://kawaii-kaomoji-hub-80.pages.dev/symbol/sym-1f634/)
- [SYM 1D444](https://coquette-aesthetic-symbols-62.pages.dev/symbol/sym-1d444/)
- [SYM 1F92A](https://kawaii-kaomoji-hub-51.pages.dev/symbol/sym-1f92a/)
- [SYM 1D44A](https://vintage-script-symbols-65.pages.dev/symbol/sym-1d44a/)
- [SYM 2630](https://zen-unicode-symbols-89.pages.dev/symbol/sym-2630/)
- [HEAVY HEART EXCLAMATION](https://modern-bullet-symbols-45.pages.dev/symbol/heavy-heart-exclamation/)
- [SYM 1D442](https://dolly-angel-fonts-14.pages.dev/symbol/sym-1d442/)
- [SYM 1D41C](https://vintage-script-symbols-65.pages.dev/symbol/sym-1d41c/)
- [LEFT POINTING DOUBLE ANGLE QUOTATION](https://sleek-bio-symbols-40.pages.dev/symbol/left-pointing-double-angle-quotation/)
- [RIGHT WHITE CORNER BRACKET](https://sleek-bio-symbols-40.pages.dev/symbol/right-white-corner-bracket/)
- [SYM 26D6](https://sleek-arrow-symbols-42.pages.dev/symbol/sym-26d6/)
- [SYM 1D468](https://coquette-aesthetic-symbols-63.pages.dev/symbol/sym-1d468/)
- [SYM 2677](https://sleek-bio-symbols-40.pages.dev/symbol/sym-2677/)
- [KAOMOJI](https://minimal-star-symbols-26.pages.dev/ru/kaomoji/)
- [SYM 2743](https://sleek-bio-symbols-40.pages.dev/symbol/sym-2743/)
- [CAPRICORN ZODIAC GOAT](https://modern-bullet-symbols-45.pages.dev/symbol/capricorn-zodiac-goat/)
- [SYM 2741](https://kawaii-kaomoji-hub-80.pages.dev/symbol/sym-2741/)
- [SYM 2684](https://cyber-clan-tags-36.pages.dev/symbol/sym-2684/)
- [SYM 2615](https://fairy-lace-symbols-92.pages.dev/symbol/sym-2615/)
- [LEFT HEAVY BRACKET BOX](https://techno-hacker-text-43.pages.dev/symbol/left-heavy-bracket-box/)
- [SYM 1D4A5](https://vintage-angel-text-38.pages.dev/symbol/sym-1d4a5/)
- [SYM 26A6](https://chibi-kaomoji-vault-58.pages.dev/symbol/sym-26a6/)
- [FLUTTERING BUTTERFLY](https://zen-unicode-symbols-89.pages.dev/symbol/fluttering-butterfly/)
- [MUSIC WEATHER](https://modern-bullet-symbols-45.pages.dev/ja/music-weather/)
- [SYM 1D446](https://vintage-script-symbols-65.pages.dev/symbol/sym-1d446/)
- [COQUETTE BOW RIBBON](https://kawaii-kaomoji-hub-51.pages.dev/symbol/coquette-bow-ribbon/)
- [DAGGER CROSS SYMBOL](https://chibi-emoticon-lab-65.pages.dev/symbol/dagger-cross-symbol/)
- [SYM 262F](https://zen-unicode-symbols-89.pages.dev/symbol/sym-262f/)
- [SWIMMING FISH RIGHT](https://techno-hacker-text-43.pages.dev/symbol/swimming-fish-right/)
- [ROBLOX NAMES](https://fairy-lace-symbols-92.pages.dev/es/roblox-names/)
- [SYM 1D454](https://kawaii-kaomoji-hub-51.pages.dev/symbol/sym-1d454/)
- [SYM 26FD](https://theeduplaycampen.pages.dev/symbol/sym-26fd/)
- [SYM 1D45C](https://vintage-script-symbols-65.pages.dev/symbol/sym-1d45c/)
- [SYM 1F642](https://daintystar-font-studio-48.pages.dev/symbol/sym-1f642/)
- [SYM 1F972](https://fairy-lace-symbols-92.pages.dev/symbol/sym-1f972/)
- [SYM 2733](https://gothic-bio-fonts-14.pages.dev/symbol/sym-2733/)
- [SYM 1D408](https://vintage-script-symbols-65.pages.dev/symbol/sym-1d408/)
- [SYM 1F62E](https://neon-hacker-text-25.pages.dev/symbol/sym-1f62e/)
- [SYM 1F618](https://chibi-emoticon-lab-65.pages.dev/symbol/sym-1f618/)
- [SYM 1D446](https://kawaii-kaomoji-hub-51.pages.dev/symbol/sym-1d446/)
- [SYM 26C4](https://cyber-clan-tags-36.pages.dev/symbol/sym-26c4/)
- [SYM 1D40A](https://pastel-moe-emoticons-55.pages.dev/symbol/sym-1d40a/)
- [SYM 1FAE1](https://soft-pastel-unicode-78.pages.dev/symbol/sym-1fae1/)
- [HEARTS](https://glitch-font-studio-46.pages.dev/vi/hearts/)
- [VIRGO ZODIAC MAIDEN](https://balletcore-unicode-67.pages.dev/symbol/virgo-zodiac-maiden/)
- [SYM 2687](https://clean-line-emojis-77.pages.dev/symbol/sym-2687/)
- [SYM 1D481](https://kawaii-kaomoji-hub-31.pages.dev/symbol/sym-1d481/)
- [SYM 1D486](https://zen-arrow-symbols-99.pages.dev/symbol/sym-1d486/)
- [SYM 1D423](https://cyber-clan-tags-55.pages.dev/symbol/sym-1d423/)
- [SYM 2631](https://techno-hacker-text-43.pages.dev/symbol/sym-2631/)
- [SYM 26B9](https://vintage-script-symbols-65.pages.dev/symbol/sym-26b9/)
- [SYM 1D422](https://cyber-clan-tags-36.pages.dev/symbol/sym-1d422/)
- [KAOMOJI](https://ballet-core-symbols-11.pages.dev/es/kaomoji/)
- [SYM 26FB](https://synth-dystopia-text-20.pages.dev/symbol/sym-26fb/)
- [SYM 1F610](https://minimal-star-symbols-87.pages.dev/symbol/sym-1f610/)
- [PINWHEEL STAR](https://subtle-sparkle-text-86.pages.dev/symbol/pinwheel-star/)
- [SYM 26CD](https://occult-rune-symbols-64.pages.dev/symbol/sym-26cd/)
- [SYM 1F626](https://glitch-font-studio-46.pages.dev/symbol/sym-1f626/)
- [ARROWS LINES](https://zen-arrow-symbols-99.pages.dev/ja/arrows-lines/)
- [WHITE FLORETTE BLOSSOM](https://moe-soft-emoticons-41.pages.dev/symbol/white-florette-blossom/)
- [TRENDING](https://fairy-lace-symbols-92.pages.dev/trending/)
- [SYM 1F61D](https://minimal-star-symbols-32.pages.dev/symbol/sym-1f61d/)
- [MUSIC WEATHER](https://coquette-aesthetic-symbols-51.pages.dev/vi/music-weather/)
- [SYM 1D48D](https://vintage-angel-text-38.pages.dev/symbol/sym-1d48d/)
- [NATURE FLOWERS](https://clean-mono-fonts-64.pages.dev/ja/nature-flowers/)
- [SYM 1D49D](https://gothic-bio-fonts-14.pages.dev/symbol/sym-1d49d/)
- [SYM 1F614](https://angelic-bow-symbols-76.pages.dev/symbol/sym-1f614/)
- [SYM 1D425](https://kawaii-kaomoji-hub-31.pages.dev/symbol/sym-1d425/)
- [SYM 2646](https://kawaii-kaomoji-hub-31.pages.dev/symbol/sym-2646/)
- [SYM 26E2](https://occult-rune-symbols-64.pages.dev/symbol/sym-26e2/)
