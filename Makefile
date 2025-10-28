# ---- Ledger Paths ----
LEDGER := reports/ledger.md
ARCHIVE_DIR := archives
PUBLIC_DIR := docs/public
REDACTOR := scripts/redact_public.py
STAMP := $(shell python3 - <<'PY'\nfrom datetime import datetime as d; print(d.now().strftime("%Y%m%d_%H%M"))\nPY)

# ---- Ledger Ops ----
archive-ledger:
	@mkdir -p $(ARCHIVE_DIR)
	@cp $(LEDGER) $(ARCHIVE_DIR)/ledger_$(STAMP).md
	@echo "Archived to $(ARCHIVE_DIR)/ledger_$(STAMP).md"

# Usage: make new-ledger-epoch EPOCH=epoch_0005 TITLE="Cycle 5 — Observatory Panels & Narrative Linkage"
new-ledger-epoch:
	@[ -n "$$EPOCH" ] && [ -n "$$TITLE" ] || (echo "Usage: make new-ledger-epoch EPOCH=epoch_XXXX TITLE='...'" && exit 2)
	@printf "\n---\n\n## [%s] %s\n**Date:** %s\n**Mode:** Deep Build\n**Signal:** —\n**Resonance:** —\n**Entropy:** —\n\n**Summary:**\n(brief notes)\n\n**Next:**\n- \n\n" "$$EPOCH" "$$TITLE" "$$(date +%Y-%m-%d)" >> $(LEDGER)
	@echo "Appended new epoch stub to $(LEDGER)"

validate-ledger:
	@grep -qE '^## \\[epoch_[0-9]{4}\\]' $(LEDGER) || (echo "Ledger invalid: missing '## [epoch_XXXX]' headers"; exit 2)
	@grep -qE '^\\*\\*Date:\\*\\* ' $(LEDGER) || (echo "Ledger invalid: missing '**Date:**' fields"; exit 2)

snapshot-public: $(REDACTOR)
	@mkdir -p $(PUBLIC_DIR)
	@python3 $(REDACTOR) $(LEDGER) $(PUBLIC_DIR)/ledger_public.md
	@echo "Wrote $(PUBLIC_DIR)/ledger_public.md (INTERNAL blocks stripped)"

# Public snapshot sanity (blocks TODO/WIP/etc)
PUBLIC_MD := docs/public/ledger_public.md
BAD_STRINGS := "TODO" "WIP" "DRAFT" "FIXME" "<!-- INTERNAL -->" "<!-- /INTERNAL -->"
validate-public:
	@[ -f $(PUBLIC_MD) ] || (echo "Missing $(PUBLIC_MD). Run: make snapshot-public"; exit 2)
	@ok=1; \
	for s in $(BAD_STRINGS); do \
	  if grep -n "$$s" $(PUBLIC_MD) >/dev/null 2>&1; then \
	    echo "❌ Found forbidden marker in $(PUBLIC_MD): $$s"; ok=0; \
	  fi; \
	done; \
	if [ $$ok -eq 1 ]; then echo "✅ $(PUBLIC_MD) is clean"; else exit 2; fi

ledger-ci: validate-ledger snapshot-public
	@echo "Ledger validated and public snapshot generated."

public-ci: snapshot-public validate-public
	@echo "Public snapshot generated and validated."
