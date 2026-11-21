#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
SHA="$(git rev-parse --short HEAD)"
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
BASE="${BASE_BRANCH:-main}"
REVIEWER="${REVIEWER:-invariant}"

if [ "$BRANCH" = "main" ]; then
  echo "BLOCKED: Never run factory work directly on main. Use a git worktree." >&2
  exit 2
fi

echo "==> [1/3] Running unit tests (pytest)"
set +e
PYTEST_OUT="$(python3 -m pytest -q 2>&1)"
PYTEST_RC=$?
set -e
echo "$PYTEST_OUT"

echo "==> [2/3] Running adversarial cross-check (mode: $REVIEWER)"
set +e
REVIEW_JSON="$(python3 tools/adversarial_check.py --base "$BASE" --mode "$REVIEWER" 2>&1)"
REVIEW_RC=$?
set -e
echo "$REVIEW_JSON"

STATUS="PASS"
if [ "$PYTEST_RC" -ne 0 ] || [ "$REVIEW_RC" -ne 0 ]; then
  STATUS="BLOCKED"
fi

echo "==> [3/3] Writing receipt.json ($STATUS)"
python3 - "$BRANCH" "$SHA" "$TIMESTAMP" "$PYTEST_RC" "$REVIEW_RC" "$STATUS" "$PYTEST_OUT" "$REVIEW_JSON" <<'PY'
import json, sys

branch, sha, ts, pytest_rc, review_rc, status, pytest_out, review_raw = sys.argv[1:9]
try:
    review = json.loads(review_raw)
except Exception:
    review = {"verdict": "ERROR", "blocking": 1, "raw": review_raw.strip()}

receipt = {
    "status": status,
    "branch": branch,
    "commit": sha,
    "timestamp_utc": ts,
    "unit_tests": {
        "exit_code": int(pytest_rc),
        "summary": pytest_out.strip().splitlines()[-1] if pytest_out.strip() else "",
    },
    "adversarial_review": review,
}
with open("receipt.json", "w", encoding="utf-8") as fh:
    json.dump(receipt, fh, indent=2)
    fh.write("\n")
print(json.dumps(receipt, indent=2))
PY

[ "$STATUS" = "PASS" ]
