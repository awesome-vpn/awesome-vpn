# Security Policy

## Supported Versions

We currently provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| master  | :white_check_mark: |
| < master| :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

### How to Report

1. **Do NOT** open a public issue
2. Email security concerns to: [maintainer email - to be configured]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Fix Released**: Depends on severity
  - Critical: 7 days
  - High: 30 days
  - Medium: 90 days
  - Low: Next release

### Security Best Practices for Users

1. **Do not commit credentials** - Never commit API keys, tokens, or passwords
2. **Use environment variables** - Store sensitive data in GitHub Secrets
3. **Validate inputs** - All user inputs are validated to prevent injection
4. **Keep dependencies updated** - Run `pip install --upgrade` regularly
5. **Review third-party nodes** - Nodes are crawled from public sources; use at your own risk

## Known Security Considerations

### Proxy Node Security

- Nodes are crawled from public Telegram channels and URLs
- We validate node connectivity but cannot guarantee node operator trustworthiness
- **Recommendation**: Use these nodes only for non-sensitive browsing
- Consider using your own private nodes for sensitive activities

### Data Privacy

- This tool does not collect or transmit user data
- All validation happens locally or in your own GitHub Actions
- GeoIP database (GeoLite2) is downloaded locally and not uploaded

## Security-Related Configuration

### GitHub Secrets

Required secrets for GitHub Actions:

- `TELEGRAM_CHANNELS` - List of Telegram channels to crawl
- `EXTRA_URLS` - Additional URLs to fetch (optional)

### Recommended Repository Settings

1. Enable **Dependabot alerts**
2. Enable **Secret scanning**
3. Require **signed commits** for contributions
4. Enable **Branch protection** on master

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the issue and determine its severity
2. Prepare a fix and test it
3. Release the fix as soon as possible
4. Publicly disclose the issue after the fix is released

## Acknowledgments

We thank the security researchers and community members who have helped improve the security of this project.
