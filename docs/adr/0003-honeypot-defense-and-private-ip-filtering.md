# 0003: Honeypot Defense and RFC Private IP Filtering

To protect the CI runner and end-user local networks from malicious node injection, all candidate nodes resolving to loopback (127.0.0.0/8), RFC 1918 private subnets, RFC 4193 IPv6 ULA, or known honeypot endpoints are rejected at the prescreen phase, and client configurations enforce direct LAN isolation rules.

## Considered Options

- **Naive string matching**: Only checked hardcoded strings (e.g. `8.8.8.8`), leaving RFC 1918 subnets and internal addresses vulnerable to SSRF.

## Consequences

- Prevents CI environment network enumeration during validation.
- Builds trust among users by guaranteeing that subscribed nodes cannot hijack or scan their local home networks.
