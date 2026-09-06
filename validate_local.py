#!/usr/bin/env python3
"""CLI tool for local dual-engine validation (Sing-box & Mihomo) with TUN bypass."""

import argparse
import json
import logging
import os
import sys

from core.dual_validator import DualValidator, detect_physical_interface

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("DualValidator")


def main():
    parser = argparse.ArgumentParser(
        description="Local Dual-Engine Validator (Sing-box & Mihomo) with Virtual NIC (TUN) Bypass"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="sing-box.json",
        help="Input sing-box.json file (default: sing-box.json)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="Concurrent validation workers (default: 8)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max number of nodes to test (default: 50, 0 for all)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Timeout in seconds for each test request (default: 5.0s)",
    )
    parser.add_argument(
        "--interface",
        type=str,
        default=None,
        help="Explicit network interface to bind (default: auto-detected physical interface)",
    )
    args = parser.parse_args()

    iface = args.interface or detect_physical_interface()

    print("\n" + "=" * 80)
    print("🚀 Awesome VPN — Local Dual-Engine Usability Validator (Sing-box + Mihomo)")
    print("=" * 80)
    print(f"🛡️  Physical Interface: {iface} (Bypassing Clash Verge TUN virtual adapter)")
    print("🎯 Target URL:          https://www.google.com/generate_204")
    print(f"📂 Input Source:        {args.input}")

    if not os.path.exists(args.input):
        print(f"❌ Error: File not found: {args.input}")
        sys.exit(1)

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    outbounds = data.get("outbounds", [])
    nodes = [n for n in outbounds if n.get("type") not in ("urltest", "selector", "direct")]

    if args.limit > 0:
        nodes = nodes[: args.limit]

    print(f"🔍 Testing {len(nodes)} candidate nodes...\n")

    validator = DualValidator(interface=iface, timeout=args.timeout)

    header = (
        f"{'#':<3} | {'Node Tag':<32} | {'Type':<6} | {'Sing-box':<14} | {'Mihomo':<14} | Status"
    )
    print("-" * 85)
    print(header)
    print("-" * 85)

    results = []
    sb_passed = 0
    mh_passed = 0
    both_passed = 0

    # Sequential display or fast parallel
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(validator.test_node_dual, n): n for n in nodes}
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            res = future.result()
            results.append(res)

            sb_ok = res["singbox"]["ok"]
            sb_str = (
                f"✅ {res['singbox']['latency_ms']}ms"
                if sb_ok
                else f"❌ {res['singbox']['error'][:8]}"
            )

            mh_ok = res["mihomo"]["ok"]
            mh_str = (
                f"✅ {res['mihomo']['latency_ms']}ms"
                if mh_ok
                else f"❌ {res['mihomo']['error'][:8]}"
            )

            if sb_ok:
                sb_passed += 1
            if mh_ok:
                mh_passed += 1
            if sb_ok and mh_ok:
                both_passed += 1
                status = "🌟 DUAL OK"
            elif sb_ok or mh_ok:
                status = "⚠️ SINGLE OK"
            else:
                status = "❌ BLOCKED"

            tag_display = res["tag"][:30]
            print(
                f"{i:<3} | {tag_display:<32} | {res['type']:<6} | {sb_str:<14} | {mh_str:<14} | {status}"
            )

    print("-" * 85)
    print("\n" + "=" * 80)
    print("📊 DUAL-ENGINE VERIFICATION SUMMARY")
    print("=" * 80)
    total = len(results)
    print(f"Total Tested:         {total}")
    print(f"Sing-box Accessible:  {sb_passed}/{total} ({sb_passed / max(1, total) * 100:.1f}%)")
    print(f"Mihomo Accessible:    {mh_passed}/{total} ({mh_passed / max(1, total) * 100:.1f}%)")
    print(f"Dual-Engine Verified: {both_passed}/{total} ({both_passed / max(1, total) * 100:.1f}%)")

    # Save report
    out_dir = "output"
    os.makedirs(out_dir, exist_ok=True)
    report_path = os.path.join(out_dir, "dual_test_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "interface": iface,
                "total": total,
                "singbox_passed": sb_passed,
                "mihomo_passed": mh_passed,
                "both_passed": both_passed,
                "results": results,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"\n📁 Detailed dual-engine test report saved to: {report_path}\n")


if __name__ == "__main__":
    main()
