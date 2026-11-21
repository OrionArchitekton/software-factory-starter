# Software Factory Rules (3-File Starter)

1. **One Task, One Worktree:** Never edit `main` directly. Branch from `main` in an isolated worktree (`git worktree add`).
2. **Never Trust "Done" Without Proof:** Passing your own unit tests is necessary, not sufficient. Run `./check.sh` before claiming completion.
3. **Adversarial Cross-Check:** A second model (Codex) reviews `task.md` plus your `git diff` looking strictly for bugs your tests missed. Any `BLOCKING` finding fails the gate.
4. **Emit a Receipt:** `./check.sh` writes `receipt.json` with commit SHA, test counts, reviewer verdict, and timestamp. No clean receipt, no merge.
