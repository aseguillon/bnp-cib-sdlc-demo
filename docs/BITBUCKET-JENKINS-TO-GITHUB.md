# From Bitbucket + Jenkins to GitHub: SDLC concept map

## 1. Concept mapping

| Today (Bitbucket / Jenkins) | GitHub | Where to see it in this repo |
|---|---|---|
| Project / Repository | Organization / Repository | repo itself |
| Pull request + default reviewers | Pull request + CODEOWNERS + required reviews | `.github/CODEOWNERS`, branch protection |
| Branch permissions / merge checks | Branch protection or Rulesets | Settings > Branches |
| Jenkins job triggered by webhook | Workflow `on: pull_request / push` | `.github/workflows/*.yml` |
| `Jenkinsfile` | Workflow YAML in the same repo | `legacy/Jenkinsfile` vs `ci.yml` |
| Jenkins agent / label | `runs-on` (GitHub-hosted or self-hosted runners, runner groups) | `runs-on:` |
| Shared Library | Reusable workflows + composite actions | section 3 |
| Jenkins credentials | Secrets / Variables, OIDC to cloud (no stored keys) | `secrets.GITHUB_TOKEN` |
| `input` approval step | Environment with required reviewers | `deploy.yml` > production |
| Stages | Jobs (parallel by default, `needs:` for order) | `needs: build` |
| Plugins | Marketplace actions | `uses:` lines |
| Artifactory / Nexus | GitHub Packages / GHCR (or keep Artifactory, call it from a step) | build job |
| SonarQube | CodeQL + dependency review (Sonar action still possible) | `ci.yml` |
| Build status in Bitbucket | Required status checks on the PR | PR checks tab |
| Jira link (Bitbucket) | Jira integration, issue/PR references, GitHub Projects | PR template |
| Audit via Jenkins logs | Audit log, deployment history per environment | Repo > Environments |

## 2. Same pipeline, side by side

| Jenkins stage | GitHub Actions |
|---|---|
| `checkout scm` | `uses: actions/checkout@v4` |
| `sh 'pytest'` | `run: python -m pytest -q` |
| `when { branch 'main' }` | `on: push: branches: [main]` |
| `credentials('x')` | `${{ secrets.X }}` |
| `input message: 'Deploy to PROD?'` | `environment: production` + required reviewers |
| `post { failure { mail } }` | `if: failure()` step, or notifications |
| `parallel { ... }` | jobs run in parallel by default; `strategy.matrix` |

Run `hello-world.yml` to see each of these pieces at its simplest.

## 3. Replacing the Jenkins Shared Library

Central team publishes one workflow in an org repo, e.g. `cib-platform/.github`:

```yaml
# cib-platform/.github/.github/workflows/python-ci.yml
on:
  workflow_call:
    inputs:
      python-version: { type: string, default: "3.12" }
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "${{ inputs.python-version }}" }
      - run: pip install -r requirements-dev.txt && ruff check . && python -m pytest -q
```

Every team consumes it in 3 lines, and the platform team changes the standard in one place:

```yaml
jobs:
  ci:
    uses: cib-platform/.github/.github/workflows/python-ci.yml@v1
```

## 4. Migration path

1. **Inventory**: list repos and Jenkins jobs (Actions Importer `audit`).
2. **Migrate repos**: preserve history and PRs (GitHub Enterprise Importer, `gh gei`).
3. **Convert pipelines**: Actions Importer `dry-run` converts Jenkinsfiles to workflows; review by hand.
4. **Run in parallel**: keep Jenkins running read-only while Actions proves out.
5. **Governance as code**: org rulesets, CODEOWNERS, environments.
6. **Cut over**: archive the Bitbucket repo, disable the Jenkins jobs.

Commands for steps 1 to 3:
```bash
gh extension install github/gh-actions-importer
gh actions-importer audit jenkins --output-dir audit --server-url https://jenkins.cib.example.com
gh actions-importer dry-run jenkins --source-url <job-url> --output-dir out
gh extension install github/gh-gei
gh gei migrate-repo --bbs-server-url <url> --bbs-project <P> --bbs-repo <R> --github-org <org> --github-repo <R>
```

## 5. Network and security notes for a bank

- Self-hosted runners (or larger runners with private networking) inside the BNP network, grouped by team, so builds reach internal systems.
- OIDC federation to Azure and other clouds removes long-lived deploy credentials.
- Pin actions to a commit SHA and restrict allowed actions at org level.
- Secret scanning with push protection, CodeQL, and Dependabot results land on the PR.
