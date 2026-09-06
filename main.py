#!/usr/bin/env python3
"""SingBox Node Crawler & Subscription Pipeline for awesome-vpn."""

import argparse
import logging
import os
import sys

from dotenv import load_dotenv

# Load secrets: .secrets takes priority, .env as fallback
load_dotenv(".secrets")
load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "core", "parsers"))

from core.matrix.exporter import MatrixExporter
from core.pipeline import NodePipeline

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def save_singbox(output_dir: str, nodes: list) -> str:
    """Backwards-compatible export helper."""
    exporter = MatrixExporter(output_dir)
    return exporter.export_curated_singbox(nodes)


def save_clash(output_dir: str, nodes: list) -> str:
    """Backwards-compatible export helper."""
    exporter = MatrixExporter(output_dir)
    return exporter.export_curated_clash(nodes)


def save_all(output_dir: str, nodes: list, source_links: dict) -> str:
    """Backwards-compatible export helper."""
    exporter = MatrixExporter(output_dir)
    return exporter.export_curated_base64(nodes, source_links)


def main():
    parser = argparse.ArgumentParser(
        description="SingBox Node Crawler & Subscription Matrix Pipeline"
    )
    parser.add_argument("--validate", action="store_true", help="Validate nodes with Sing-box")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    parser.add_argument("--workers", type=int, default=10, help="Number of fetch workers")
    parser.add_argument(
        "--validate-workers",
        type=int,
        default=30,
        help="Number of validation workers (default 30)",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Local mode: skip direct TCP checks that fail behind GFW",
    )
    args = parser.parse_args()

    is_ci = os.getenv("GITHUB_ACTIONS") == "true"
    local_mode = args.local or not is_ci
    if local_mode:
        logger.info("Mode: LOCAL (direct TCP checks disabled — GFW environment)")
    else:
        logger.info("Mode: CI (full validation including direct TCP checks)")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = args.output if os.path.isabs(args.output) else os.path.join(base_dir, args.output)

    try:
        max_nodes = int(os.getenv("MAX_NODES", "80"))
    except (ValueError, TypeError):
        max_nodes = 80

    pipeline = NodePipeline(
        base_dir=base_dir,
        output_dir=output_dir,
        validate=args.validate,
        local_mode=local_mode,
        workers=args.workers,
        validate_workers=args.validate_workers,
        max_nodes=max_nodes,
    )

    result = pipeline.run()
    logger.info("\n" + "=" * 60)
    logger.info(f"Pipeline finished successfully! Curated: {result['curated_count']} nodes.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
