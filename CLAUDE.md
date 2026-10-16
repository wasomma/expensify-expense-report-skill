# expensify-expense-report-skill

Open-source dual-harness skill (Claude Code + Google Antigravity) that builds and enters reimbursable New Expensify (`https://new.expensify.com`) expense reports from Gmail receipts while never clicking **Submit**.

## Repository Structure

* `plugin.json` — Root plugin manifest for Google Antigravity (`~/.gemini/config/plugins/expensify-expense-report`).
* `.claude-plugin/plugin.json` & `.claude-plugin/marketplace.json` — Plugin manifests for Claude Code.
* `config.example.yaml` — Template for user configuration at `~/.claude/expense-report/config.yaml` (or `~/.config/expense-report/config.yaml`).
* `skills/expense-report/SKILL.md` — Core skill entrypoint (compatible with both Claude Code and Antigravity).
* `skills/expense-report/references/`
  * `setup-interview.md` — First-run interactive setup interview to generate `config.yaml`.
  * `receipt-sources.md` — Gmail receipt search & retrieval (via Gmail MCP connector or browser `mail.google.com` + `.eml` download).
  * `conventions.md` — Reconciliation rules, standard questions, per diem, cell claims, and description conventions.
  * `expensify-web-entry.md` — Browser automation recipe for New Expensify supporting both Claude in Chrome (`mcp__claude-in-chrome__*`) and Antigravity (`/browser` tools), using the `#probeX` + synthetic `DataTransfer` `DragEvent('drop')` receipt upload pattern.
* `skills/expense-report/scripts/`
  * `gmail_html_to_pdf.py` — Converts Gmail `FULL_CONTENT` JSON or raw `.eml` files to PDF via headless Chrome/Edge, optionally trims trailing boilerplate pages with PyMuPDF (`fitz`), and verifies expected text via `pdftotext`.
  * `gmail_raw_attachments.py` — Extracts PDF/image attachments from Gmail `RAW` JSON or `.eml` RFC 822 files.
  * `merge_pdfs.py` — Merges hotel booking confirmation + folio PDFs into a single receipt PDF via PyMuPDF.
* `tools/pii_scan.py` — Mandatory pre-commit scanner that blocks personal names, emails, card numbers, and local paths from being committed to this public repository.

## Development & Safety Rules

1. **Mandatory PII Scan Before Commit:**
   Always run `python tools/pii_scan.py` from the repository root before staging or committing any change. Never commit real user names, corporate domains, full or last-4 card numbers (other than generic placeholders like `1234`/`5678`), or machine-specific user paths (`C:/Users/<real-name>/`).
2. **Never Click Submit:**
   All documentation and browser scripts must preserve the hard rule that the agent leaves the Expensify report in **Draft** / **Open** status for the human user to review and submit.
3. **Dual-Harness Parity:**
   Keep `SKILL.md` and `references/*.md` compatible with both Claude Code (`mcp__claude-in-chrome__*` + Gmail MCP) and Antigravity (`/browser` tools + Gmail MCP or browser `.eml` fallback).
