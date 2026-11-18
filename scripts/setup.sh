#!/usr/bin/env bash
# Usage: ./scripts/setup.sh <owner>/<repo> [reviewer-username]
# Creates the repo, pushes the code, creates demo/production environments,
# and protects main (PR + passing CI required).
set -euo pipefail
REPO="${1:?owner/repo}"
REVIEWER="${2:-$(gh api user -q .login)}"
cd "$(dirname "$0")/.."

sed -i.bak "s/OWNER_PLACEHOLDER/$REVIEWER/" .github/CODEOWNERS && rm .github/CODEOWNERS.bak
[ -d .git ] || { git init -q -b main && git add -A && git commit -qm "Initial commit: trade validation service"; }
gh repo create "$REPO" --private --source . --push

gh api -X PUT "repos/$REPO/environments/demo" >/dev/null
RID=$(gh api "users/$REVIEWER" -q .id)
gh api -X PUT "repos/$REPO/environments/production" --input - >/dev/null <<EOF
{"reviewers":[{"type":"User","id":$RID}],"deployment_branch_policy":{"protected_branches":true,"custom_branch_policies":false}}
EOF

gh api -X PUT "repos/$REPO/branches/main/protection" --input - >/dev/null <<EOF
{"required_status_checks":{"strict":true,"contexts":["test"]},
 "enforce_admins":false,
 "required_pull_request_reviews":{"required_approving_review_count":0,"require_code_owner_reviews":false},
 "restrictions":null}
EOF
echo "Done: https://github.com/$REPO"
