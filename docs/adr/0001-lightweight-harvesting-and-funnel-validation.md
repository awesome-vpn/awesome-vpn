# 0001: Lightweight Harvesting and Tiered Funnel Validation

To achieve high project adoption on GitHub while staying within free GitHub Actions CI/CD quotas, we reject heavy crawling frameworks (Scrapy, Firecrawl) in favor of lightweight session-based Telegram topology expansion with a persistent Channel Ledger, a GitHub Radar registry for active proxy repositories, and a tiered prescreen funnel before Sing-box process validation.

## Considered Options

- **Full-web browser-based scraping (Firecrawl/Scrapy)**: Heavy resource footprint, requires headless browsers and proxy pools, triggers Cloudflare/bot blocks in CI.
- **Unbounded Telegram recursive crawling**: High risk of Telegram 429 rate limiting, spam channel proliferation, and wasted CI time.
- **All-node Sing-box process spawning**: Spawning thousands of individual sing-box processes causes CI timeout and file-descriptor exhaustion.

## Consequences

- **Channel Ledger state persistence**: The CI workflow must persist and commit updated channel metrics (`channels.json`) or store them in artifact cache to avoid losing ledger history between runs.
- **High throughput under budget**: The multi-tier funnel discards ~80% of dead nodes via fast TCP handshake checks, capping sing-box process validation to the top candidate slice (e.g. 300-500 nodes) and keeping execution under 10 minutes.
- **Subscription Matrix output**: The pipeline will output distinct feeds (Curated Top-N, Raw Pool, and Protocol-specific feeds like Hysteria2 and Reality) alongside an automated telemetry badge in the README.
