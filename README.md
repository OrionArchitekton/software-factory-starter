# Software Factory Starter (One Task, One File, One Rule)

Companion starter repo for the YouTube episode:
**Build Your First AI Software Factory with Claude Code (Start Small)**

## The 3-File Factory
1. `task.md`: One bounded task with explicit acceptance criteria.
2. `RULES.md`: One short rule file (isolated git worktree, tests first, second-model review, receipt).
3. `check.sh`: One verification gate that runs unit tests + an adversarial cross-check and emits `receipt.json`.

## Quickstart
```bash
git worktree add ../sf-work -b work/add-partial-refunds
cd ../sf-work
# Ask Claude Code to implement task.md following RULES.md
./check.sh
# Use REVIEWER=codex ./check.sh to run Codex CLI as the second-model reviewer
```
