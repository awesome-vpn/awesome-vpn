# 0002: Orphan Distribution Branch for Subscription Delivery

To prevent repository bloat from high-frequency automated updates, generated subscription artifacts and matrix feeds are published exclusively to an orphan `gh-pages` branch with history squashed/pruned, keeping the `master` source branch lightweight and clean.

## Considered Options

- **Direct commits to master**: Rapidly causes repository size to reach hundreds of megabytes within a year, making git clones sluggish.
- **GitHub Release asset uploads**: Functional, but lacks native GitHub Pages CDN multi-region edge caching and clean URL scheme routing.

## Consequences

- Endpoints are served directly via GitHub Pages CDN (e.g. `https://<org>.github.io/<repo>/...`), yielding lower download latencies.
- Local working trees and developer clones remain under 10 MB permanently.
