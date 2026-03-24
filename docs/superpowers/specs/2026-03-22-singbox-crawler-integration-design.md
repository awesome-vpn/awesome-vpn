# Design Spec: SingBox-Crawler Integration into awesome-vpn

**Date:** 2026-03-22
**Status:** Approved

---

## Goal

Merge SingBox-Crawler into the awesome-vpn repo as a single open-source project. The crawler runs via GitHub Actions daily and outputs three subscription formats. Sensitive sources (Telegram channels, private URLs) are stored in GitHub Secrets and never appear in source code.

---

## Repo Structure (flat, no subdirectory)

```
awesome-vpn/
├── .github/workflows/daily.yml   # GitHub Actions workflow
├── core/
│   ├── parsers/                  # Protocol parsers (vmess/vless/ss/trojan/hy2/tuic)
│   ├── converters/
│   │   └── clash.py              # NEW: sing-box → Clash proxy converter
│   ├── spider.py
│   ├── deduplicator.py
│   ├── validator.py
│   ├── binary_manager.py
│   └── geo_utils.py
├── config/
│   ├── sources.json              # Public URL sources only (no Telegram)
│   └── sources.list              # Public URL sources (extended list)
├── main.py                       # Entry point (updated)
├── requirements.txt
├── .gitignore
├── all                           # Output: base64 subscription (existing)
├── sing-box.json                 # Output: sing-box outbounds JSON (new)
├── clash.yaml                    # Output: Clash proxies YAML (new)
├── README.md
└── README_CN.md
```

---

## GitHub Secrets

| Secret | Format | Purpose |
|--------|--------|---------|
| `TELEGRAM_CHANNELS` | `chan1,chan2,chan3` | Telegram channel names (comma-separated) |
| `EXTRA_URLS` | one URL per line (multiline) | Private/sensitive subscription URLs |

**Local development:** `sources.json` will NOT contain `telegram_channels` (removed for open-source). Local developers must set env vars via a `.env` file (loaded by `python-dotenv`). `.env` is in `.gitignore`.

---

## main.py Changes

`main.py` must reside at the repo root for `--output .` to resolve correctly.

1. **Load `.env` for local dev** (via `python-dotenv`, no-op if file absent):
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

2. **Secret injection** at startup:
   ```python
   tg_secret = os.getenv('TELEGRAM_CHANNELS', '')
   telegram_channels = [c.strip() for c in tg_secret.split(',') if c.strip()]
   # No fallback to sources.json — telegram_channels removed from that file

   extra_urls = [u.strip() for u in os.getenv('EXTRA_URLS', '').splitlines() if u.strip()]
   # Prepend to url_sources list before fetching
   ```

3. **Three output files** written to `--output` directory (default `.`):

   ```python
   # all — base64-encoded proxy links (one per line → join → base64)
   import base64
   raw = '\n'.join(links_output)
   encoded = base64.b64encode(raw.encode()).decode()
   write(output_dir / 'all', encoded)

   # sing-box.json — outbounds array only (not full config)
   write(output_dir / 'sing-box.json', json.dumps({"outbounds": valid_nodes}))

   # clash.yaml — proxies list
   from core.converters.clash import to_clash_proxies
   proxies = to_clash_proxies(valid_nodes)
   write(output_dir / 'clash.yaml', yaml.dump({"proxies": proxies}))
   ```

---

## Clash Converter (`core/converters/clash.py`)

Converts sing-box outbound dicts → Clash proxy dicts.

| sing-box type | Clash type | Key field mappings |
|--------------|-----------|-------------------|
| vmess | vmess | server, port, uuid, alterId, cipher, tls, network, ws-opts |
| vless | vless | server, port, uuid, flow, tls, network, ws-opts, reality-opts |
| shadowsocks | ss | server, port, password, cipher |
| trojan | trojan | server, port, password, sni, skip-cert-verify |
| hysteria2 | hysteria2 | server, port, password, sni, skip-cert-verify |
| tuic | tuic | server, port, uuid, password, congestion-controller, alpn |

Nodes that cannot be converted (unsupported type) are skipped with a `logging.debug()` message.

**VLESS + REALITY mapping** (non-trivial):
```python
# sing-box tls.reality → Clash reality-opts
if node.get('tls', {}).get('reality', {}).get('enabled'):
    reality = node['tls']['reality']
    proxy['reality-opts'] = {
        'public-key': reality.get('public_key', ''),
        'short-id':   reality.get('short_id', '')
    }
    proxy['client-fingerprint'] = node['tls'].get('utls', {}).get('fingerprint', 'chrome')
```

---

## New Public Sources (added to sources.list)

```
https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/sub_merge_base64.txt
https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/splitted/mixed
https://raw.githubusercontent.com/Everyday-VPN/Everyday-VPN/main/subscription/main.txt
https://raw.githubusercontent.com/barry-far/V2ray-Configs/main/All_Configs_Sub.txt
https://raw.githubusercontent.com/NiREvil/vless/main/sub/subs.txt
https://raw.githubusercontent.com/coldwater-10/V2Hub/main/sub
https://raw.githubusercontent.com/mheidari98/.proxy/main/all
https://raw.githubusercontent.com/yebekhe/TelegramV2rayCollector/main/sub/mix
https://raw.githubusercontent.com/Ashkan-m/v2ray/main/Sub.txt
```

---

## GitHub Actions Workflow

**Prerequisite:** In the repo → Settings → Actions → General → Workflow permissions, set to "Read and write permissions".

```yaml
name: Daily Crawler
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:

env:
  SING_BOX_VERSION: "1.10.7"   # pin version so cache key is stable

jobs:
  crawl:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }

      - name: Cache sing-box binary
        uses: actions/cache@v4
        with:
          path: bin/
          key: sing-box-${{ runner.os }}-${{ runner.arch }}-${{ env.SING_BOX_VERSION }}

      - name: Download GeoLite2-City.mmdb
        run: |
          mkdir -p config
          curl -sL "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb" \
            -o config/GeoLite2-City.mmdb

      - run: pip install -r requirements.txt

      - name: Run Crawler
        env:
          TELEGRAM_CHANNELS: ${{ secrets.TELEGRAM_CHANNELS }}
          EXTRA_URLS: ${{ secrets.EXTRA_URLS }}
          SING_BOX_VERSION: ${{ env.SING_BOX_VERSION }}
        run: python main.py --validate --workers 10 --output .

      - name: Verify outputs
        run: |
          [ -s all ] || (echo "ERROR: all is empty" && exit 1)
          [ -s sing-box.json ] || (echo "ERROR: sing-box.json is empty" && exit 1)
          [ -s clash.yaml ] || (echo "ERROR: clash.yaml is empty" && exit 1)

      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add all sing-box.json clash.yaml
          NODE_COUNT=$(python -c 'import json; print(len(json.load(open("sing-box.json"))["outbounds"]))')
          git diff --staged --quiet || \
            git commit -m "update: $(date +'%Y-%m-%d') - ${NODE_COUNT} nodes"
          git push
```

`GITHUB_TOKEN` (auto-provided by Actions) is sufficient — no personal `GH_TOKEN` needed, provided the workflow permissions prerequisite above is set.

---

## Subscription URLs (after merge)

| Format | URL |
|--------|-----|
| Base64 (universal) | `https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/main/all` |
| Sing-box | `https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/main/sing-box.json` |
| Clash | `https://raw.githubusercontent.com/awesome-vpn/awesome-vpn/main/clash.yaml` |

---

## Migration Steps

1. **Repo setup:** In awesome-vpn → Settings → Actions → General → set "Read and write permissions"
2. Copy `core/`, `config/`, `main.py`, `requirements.txt` from SingBox-Crawler → awesome-vpn root
3. Remove `telegram_channels` from `sources.json`; add `python-dotenv` to `requirements.txt`
4. Add new sources to `sources.list`
5. Add `core/converters/__init__.py` + `core/converters/clash.py`
6. Update `main.py`: dotenv load, secret injection, three output files, pass `SING_BOX_VERSION` env to `BinaryManager`
7. Replace `.github/workflows/daily.yml` with new workflow above
8. Update `.gitignore`: add `output/`, `config/GeoLite2-City.mmdb`, `.env`, `bin/`
9. Set GitHub Secrets: `TELEGRAM_CHANNELS` (comma-separated), `EXTRA_URLS` (multiline)
10. Commit all code changes; trigger workflow manually via `workflow_dispatch` to verify
