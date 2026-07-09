#!/usr/bin/env bash
# make-toy-repo.sh — build a scratch git repo for conductor dev tests.
#
# Usage: ./make-toy-repo.sh <target-dir>
#
# Produces a tiny project with:
#   - plan.md            a 2-unit plan (unit-b depends on unit-a) whose objectives embed the
#                        `<path> => <content>` lines that tests/mock-codex knows how to apply
#   - check-a.sh         unit-a's verification: a.txt must contain exactly "alpha"
#   - check-b.sh         unit-b's verification: b.txt must contain exactly "beta", and a.txt
#                        must exist (the dependency)
#   - AGENTS.md          declares the fast gate (the check scripts) so gate discovery finds it
#
# Deterministic red-gate scenario: run with MOCK_CODEX_FAIL="unit-b:1" so the first
# implementation of unit-b writes wrong content and check-b.sh fails with an actionable error —
# exercising the verbatim-handback fix loop.

set -eu
TARGET="${1:?usage: make-toy-repo.sh <target-dir>}"
mkdir -p "$TARGET"
cd "$TARGET"

git init -q -b master

cat > check-a.sh <<'EOF'
#!/bin/sh
got="$(cat a.txt 2>/dev/null || echo '<missing>')"
if [ "$got" = "alpha" ]; then echo "check-a OK"; exit 0; fi
echo "check-a FAILED: a.txt must contain exactly 'alpha', got: $got" >&2
exit 1
EOF

cat > check-b.sh <<'EOF'
#!/bin/sh
[ -f a.txt ] || { echo "check-b FAILED: a.txt missing (unit-b depends on unit-a)" >&2; exit 1; }
got="$(cat b.txt 2>/dev/null || echo '<missing>')"
if [ "$got" = "beta" ]; then echo "check-b OK"; exit 0; fi
echo "check-b FAILED: b.txt must contain exactly 'beta', got: $got" >&2
exit 1
EOF
chmod +x check-a.sh check-b.sh

cat > AGENTS.md <<'EOF'
# Toy project

Fast gate: `./check-a.sh && ./check-b.sh` (run only the check script(s) named by the unit under
test when gating a single unit). Heavy gate: same commands — this project has no slow suite.
EOF

cat > plan.md <<'EOF'
# Toy plan: two files

## Unit 1: unit-a — create a.txt
- Files: a.txt (create)
- Acceptance criteria: a.txt contains exactly the word alpha. Set the file content via:
  a.txt => alpha
- Verification: ./check-a.sh
- Dependencies: none

## Unit 2: unit-b — create b.txt
- Files: b.txt (create)
- Acceptance criteria: b.txt contains exactly the word beta. Set the file content via:
  b.txt => beta
- Verification: ./check-b.sh
- Dependencies: unit-a (b's check requires a.txt to exist)
EOF

git add -A
git commit -qm "toy project scaffold"

echo "Toy repo ready at: $(pwd)"
echo "Plan: $(pwd)/plan.md"
echo "Red-gate scenario: MOCK_CODEX_FAIL='unit-b:1'"
