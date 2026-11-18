# BNP Paribas CIB - Basic SDLC on GitHub (≈20 min)

Story: a developer adds a rule to the *Trade Validation Service*, and ships it to Demo then Production with governance.

**Prep (once):** `./scripts/setup.sh <org>/cib-trade-validation <approver-username>`
(`demo` auto-deploys; `production` requires an approver; `main` is protected.)

## 1. Clone & run (3 min)
```bash
gh repo clone <org>/cib-trade-validation && cd cib-trade-validation
pip install -r requirements-dev.txt && python -m pytest -q
python -m app.main &   # curl localhost:8080/health
```
Talking point: same repo, same tooling for every CIB team; Codespaces/Dev Containers can replace local setup.

## 2. Branch & change with Copilot (5 min)
```bash
git switch -c feature/reject-weekend-settlement
```
In VS Code / Copilot Chat: *"Add a rule rejecting trades with settlement_date on a weekend in validate_trade, with tests."*
Show Agent mode, then Copilot code review on the PR.

## 3. Pull request (5 min)
```bash
git add -A && git commit -m "Reject weekend settlement dates" && git push -u origin HEAD
gh pr create --fill
```
Show: PR template, required `test` check, CodeQL, dependency review, Copilot review comments, branch protection blocking merge until green.

## 4. Merge → Demo → Production (5 min)
```bash
gh pr merge --squash
gh run watch
```
- `build`: image pushed to GHCR, tagged with commit SHA
- `deploy-demo`: automatic, smoke test
- `deploy-production`: **paused for approval** → approve in Actions UI (audit trail, who/when)

## 5. Wrap-up
Traceability PR→commit→image→deployment, environments with approvals, security scanning built in, Copilot across the flow.
Real targets: replace the echo steps in `deploy.yml` with Azure (OIDC login, Container Apps/AKS); use runner groups/self-hosted runners if required by BNP network policy.

## Reset between demos
Revert the feature commit; production approvals reset per run.
