# 0004: Stateful Longevity and Self-Healing Ledgers

To achieve maximum node reliability and prevent crawler degradation over time, we transition from purely stateless single-run pinging to a stateful closed-loop architecture featuring exponential backoff channel revival, automated ledger garbage collection, radar repository health auto-pruning, and node longevity tracking with multi-day survival bonuses.

## Considered Options

- **Permanent source freezing**: Simple, but irreversibly drops channels suffering temporary outages and allows inactive channels to bloat the ledger forever without garbage collection.
- **Stateless quality ranking**: Tests nodes solely on instantaneous round-trip time without remembering past uptime, allowing ephemeral short-lived nodes to crowd out proven multi-day persistent servers.

## Consequences

- **Channel Ledger self-healing**: Channels dormant for over 7 days are periodically re-probed in low-frequency slots, and channels with zero lifetime yield dormant over 30 days are automatically garbage-collected.
- **Node stability prioritization**: Nodes surviving across consecutive daily runs earn longevity bonus multipliers, ensuring that the Curated Pool contains a balanced mixture of battle-tested stable servers and high-bandwidth fresh nodes.
- **Self-pruning GitHub Radar**: Repositories returning HTTP 404 or remaining unupdated for prolonged cycles are marked dormant and bypassed.
