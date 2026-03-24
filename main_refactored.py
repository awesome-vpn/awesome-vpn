#!/usr/bin/env python3
"""
Awesome VPN Crawler - Refactored Entry Point
Clean architecture with separated concerns.
"""

import os
import sys
import argparse
import logging

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pipeline import Pipeline

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Awesome VPN Crawler (Refactored)')
    parser.add_argument('--validate', action='store_true', help='Enable validation')
    parser.add_argument('--output', type=str, default='output', help='Output directory')
    parser.add_argument('--workers', type=int, default=24, help='Fetch workers')
    parser.add_argument('--validate-workers', type=int, default=50, help='Validation workers')
    parser.add_argument('--no-prescreen', action='store_true', help='Disable TCP pre-screening')
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = args.output if os.path.isabs(args.output) else os.path.join(base_dir, args.output)

    # Load configuration
    import json
    config_path = os.path.join(base_dir, 'config', 'sources.json')
    with open(config_path, 'r') as f:
        sources = json.load(f)

    # Load from environment (Secrets)
    tg_secret = os.getenv('TELEGRAM_CHANNELS', '')
    telegram_channels = [c.strip() for c in tg_secret.split(',') if c.strip()]
    extra_urls = [u.strip() for u in os.getenv('EXTRA_URLS', '').splitlines() if u.strip()]

    sources_config = {
        'urls': sources.get('urls', []),
        'telegram_channels': telegram_channels,
        'extra_urls': extra_urls
    }

    # Run pipeline
    pipeline = Pipeline(
        enable_validation=args.validate,
        workers=args.workers,
        validate_workers=args.validate_workers,
        tcp_prescreen=not args.no_prescreen,
        base_dir=base_dir
    )

    nodes = pipeline.run(sources_config, output_dir)
    logger.info(f"\n✅ Complete: {len(nodes)} nodes exported")

    return 0 if nodes else 1


if __name__ == "__main__":
    sys.exit(main())
