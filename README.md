# Seventh Horizon

Operator-grade ecosystem for reproducible observability.

## Overview
Seventh Horizon coordinates multiple subsystems (UI, telemetry intake/sorting, reproducibility/CI, and a Kubernetes operator) behind a single, deterministic workflow. The repo keeps an **append-only ledger** as the canonical source of truth and generates a **public snapshot** for sharing.

- Canonical log (private): `reports/ledger.md`  
- Public snapshot (generated): `docs/public/ledger_public.md`  
- Submodule: `observatory-operator/` (Kubernetes controller)

## Repo Layout
/reports/            # append-only system ledger (private)
/docs/public/        # generated public snapshot
/scripts/            # helper scripts (e.g., redact_public.py)
/archives/           # timestamped ledger archives (gitignored)
/observatory-operator # git submodule (pinned SHA)
Makefile             # ledger ops + validation

## Make Targets
| target | purpose |
|--------|----------|
| `make snapshot-public` | Generate `docs/public/ledger_public.md` (redacts `<!-- INTERNAL -->` blocks) |
| `make validate-ledger` | Cheap schema checks on `reports/ledger.md` |
| `make validate-public` | Fails if public snapshot contains `TODO/WIP/DRAFT/INTERNAL` |
| `make ledger-ci` | Validate + regenerate public snapshot |
| `make archive-ledger` | Copy current ledger to `archives/ledger_YYYYMMDD_HHMM.md` |
| `make new-ledger-epoch EPOCH=epoch_0005 TITLE="Cycle 5 — Observatory Panels & Narrative Linkage"` | Append a new epoch stub |

## Submodules
Initialize after cloning:
git submodule update --init --recursive

## CI
`/.github/workflows/ledger-ci.yml` runs ledger validation and public snapshot generation on pull requests.

## Contribution & Governance
- Append to `reports/ledger.md`; do not rewrite history.
- Wrap sensitive notes with:
  <!-- INTERNAL -->
  ...private notes...
  <!-- /INTERNAL -->
- Use PRs for changes to CI, Makefile, or submodules.

Licensed under the Apache License, Version 2.0 — see the LICENSE file for details.
