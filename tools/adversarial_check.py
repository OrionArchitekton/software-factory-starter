"""Adversarial cross-check for the 3-file software factory starter.

In production, run with `--mode codex` so a second model audits `task.md` + `git diff`
independently of the builder. The default `--mode invariant` runs an independent
property check (separate from the builder's own unit tests) so anyone can test the
fail-closed receipt gate locally without an extra API key.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from billing.models import Order
from billing.refunds import RefundService


def run_invariant_probe() -> dict:
    findings: list[dict] = []
    svc = RefundService(orders={"ord_101": Order(order_id="ord_101", amount_cents=10000)})

    try:
        r1 = svc.process_refund("ord_101", 6000, "k_part_1")
        if r1.amount_cents != 6000:
            findings.append(
                {
                    "severity": "BLOCKING",
                    "rule": "partial-refund-amount",
                    "detail": f"First $60 refund returned {r1.amount_cents} cents.",
                }
            )
    except Exception as exc:
        findings.append(
            {
                "severity": "BLOCKING",
                "rule": "first-partial-refund",
                "detail": f"Valid $60 refund on $100 order failed: {exc}",
            }
        )
        return {"reviewer": "invariant-probe", "verdict": "BLOCKED", "blocking": len(findings), "findings": findings}

    try:
        r2 = svc.process_refund("ord_101", 6000, "k_part_2")
        findings.append(
            {
                "severity": "BLOCKING",
                "rule": "cumulative-over-refund",
                "file": "billing/refunds.py",
                "detail": (
                    "Cumulative partial refunds exceeded the $100.00 order: "
                    f"$60.00 + ${r2.amount_cents / 100:.2f} = ${svc.refunded_total('ord_101') / 100:.2f} refunded."
                ),
                "repro": "process_refund('ord_101', 6000, 'k1') then process_refund('ord_101', 6000, 'k2')",
            }
        )
    except ValueError:
        pass

    replay_svc = RefundService(orders={"ord_101": Order(order_id="ord_101", amount_cents=10000)})
    replay_svc.process_refund("ord_101", 6000, "k_part_1")
    replay = replay_svc.process_refund("ord_101", 6000, "k_part_1")
    if not replay.replayed or replay_svc.refunded_total("ord_101") != 6000:
        findings.append(
            {
                "severity": "BLOCKING",
                "rule": "idempotent-replay",
                "detail": "Replaying idempotency key k_part_1 altered refunded total or lost replayed=True.",
            }
        )

    verdict = "PASS" if not findings else "BLOCKED"
    return {
        "reviewer": "adversarial-cross-check",
        "verdict": verdict,
        "blocking": len(findings),
        "findings": findings,
    }


def run_codex_review(base: str) -> dict:
    diff = subprocess.check_output(["git", "diff", f"{base}...HEAD"], text=True)
    task = (ROOT / "task.md").read_text(encoding="utf-8")
    prompt = (
        "You are an adversarial code reviewer. Compare task.md against this git diff. "
        "Return strict JSON: {\"reviewer\": \"codex\", \"verdict\": \"PASS\"|\"BLOCKED\", "
        "\"blocking\": <int>, \"findings\": [{\"severity\": \"BLOCKING\", \"file\": ..., \"detail\": ...}]}.\n\n"
        f"TASK:\n{task}\n\nDIFF:\n{diff}\n"
    )
    out = subprocess.check_output(["codex", "exec", prompt], text=True)
    return json.loads(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="main")
    parser.add_argument("--mode", choices=("invariant", "codex"), default="invariant")
    args = parser.parse_args()

    result = run_codex_review(args.base) if args.mode == "codex" else run_invariant_probe()
    print(json.dumps(result, indent=2))
    return 0 if result.get("verdict") == "PASS" and result.get("blocking", 1) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
