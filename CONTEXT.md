# Awesome VPN

Automated discovery, validation, and curation pipeline for high-usability free proxy nodes.

## Language

**Static Feed**:
A persistent, preconfigured URL or channel that is polled on every execution cycle.
_Avoid_: Fixed link, subscription source, seed URL

**Dynamic Harvester**:
A discovery worker that discovers previously unknown node sources through recursive graph traversal or search APIs.
_Avoid_: Web crawler, Scrapy bot, Firecrawl spider

**Telegram Topology Harvester**:
A discovery worker that extracts newly mentioned channels and forwarded sources from Telegram messages to expand the channel graph.
_Avoid_: TG crawler, channel scraper

**Channel Ledger**:
A persistent record tracking candidate Telegram channels, their consecutive failure counts, and historical yield of valid nodes for automated pruning and promotion.
_Avoid_: Channel blacklist, channel list, TG database

**Backoff Revival**:
A periodic reactivation probe for dormant or rate-limited sources after an exponential cooldown period.
_Avoid_: Unfreeze hack, manual reset

**Ledger Garbage Collection**:
The automated purging of dormant sources that have produced zero lifetime yield and exceeded retention limits.
_Avoid_: Channel cleanup, database prune

**GitHub Radar**:
A curated, regularly refreshed registry of active proxy-sharing repositories polled directly via raw links to discover newly published nodes without Search API rate-limit exhaustion.
_Avoid_: Git crawler, repo scraper

**GitHub Code Sniffer**:
A discovery worker that queries code hosting search APIs for freshly committed proxy links and configuration snippets.
_Avoid_: Git scraper, repo crawler

**Raw Pool**:
The unvalidated aggregate of unique candidate proxy links collected across all feeds and harvesters.
_Avoid_: Dirty nodes, candidate list, input buffer

**Prescreen Funnel**:
A tiered filtering pipeline that discards malformed links, blocklisted targets, and unresponsive TCP endpoints before heavy Sing-box verification.
_Avoid_: Fast filter, pre-validator

**Honeypot Filter**:
A security guard that detects and rejects candidate nodes resolving to private networks (RFC 1918/4193), loopback addresses, or known probe infrastructure.
_Avoid_: IP filter, blacklister

**Curated Pool**:
The sorted, latency-filtered, and deduplicated subset of nodes that passed active connectivity verification.
_Avoid_: Output nodes, valid nodes, filtered list

**Node Longevity Ledger**:
A persistent record tracking multi-day connectivity streaks and stability bonuses for verified proxy nodes across execution cycles.
_Avoid_: Node database, history cache, ping log

**Subscription Matrix**:
A multi-tier distribution model providing both a curated low-latency feed and protocol-specific endpoints (such as Hysteria2 and Reality) alongside an unfiltered raw pool.
_Avoid_: Link exports, output formats

**Orphan Distribution Branch**:
A dedicated Git branch with no shared commit history used exclusively to publish generated subscription artifacts without bloating the primary codebase repository.
_Avoid_: Build branch, output branch, release hack
