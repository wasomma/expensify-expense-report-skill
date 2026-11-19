# Phases & Checkpoint State — `expensify-expense-report-skill`

## Approved Spec (2026-10-15): Dual-Harness Update (Claude Code + Antigravity)

1. **Gmail Fetching Strategy:** Support both Gmail MCP tools (`search_threads`, `get_thread`, `get_message`) when a Gmail connector/MCP is configured, and fall back to browser-driven Gmail (`mail.google.com` + `.eml` RFC 822 download parsed by `gmail_html_to_pdf.py` and `gmail_raw_attachments.py`) when running in Antigravity without a Gmail MCP.
2. **Browser Driving Strategy:** Map `expensify-web-entry.md` to both Claude in Chrome (`mcp__claude-in-chrome__*`) and Antigravity's built-in `/browser` tools (`open_browser_url`, `execute_browser_javascript`, `upload_file_to_browser`, `click_browser_pixel`), reusing the identical DOM JS and `#probeX` synthetic `DataTransfer` `DragEvent('drop')` recipes.
3. **Local Machine Setup:** Update the repo on branch `feat/dual-harness-antigravity`, register the plugin in `~/.gemini/config/plugins/expensify-expense-report`, and seed `~/.claude/expense-report/config.yaml` from the maintainer's existing private skill settings.

---

## Milestones

- [x] **Phase 1: Initial Open-Source Release (`fcd2f10`, `778fd18`)**
  - Generic skill, setup interview, config template, helper scripts, and `tools/pii_scan.py`.
- [x] **Phase 2: Dual-Harness Support (Claude Code + Google Antigravity) — *Complete***
  - [x] Create `CLAUDE.md` and `PHASES.md`.
  - [x] Add root `plugin.json` for Antigravity alongside `.claude-plugin/plugin.json`.
  - [x] Extend `scripts/gmail_html_to_pdf.py` and `scripts/gmail_raw_attachments.py` to accept raw `.eml` (RFC 822) files in addition to Gmail MCP JSON files.
  - [x] Update `skills/expense-report/SKILL.md`, `references/expensify-web-entry.md`, `references/receipt-sources.md`, `references/setup-interview.md`, `config.example.yaml`, and `README.md` for dual-harness operation.
  - [x] Verify scripts and run `python tools/pii_scan.py`.
  - [x] Seed `~/.claude/expense-report/config.yaml` and register `~/.gemini/config/plugins/expensify-expense-report`.
- [x] **Phase 2.1: Windows PowerShell / Antigravity Verification (`fix/pymupdf-text-fallback`)**
  - [x] Use `fitz` (PyMuPDF) first in `pdf_text()` in `scripts/gmail_html_to_pdf.py` (with fallback to `pdftotext` / Git for Windows `pdftotext.exe`) so PowerShell users don't need `pdftotext` on system `PATH`.
  - [x] Strip leading UTF-8 BOM (`\xef\xbb\xbf`) and whitespace in `scripts/gmail_html_to_pdf.py` and `scripts/gmail_raw_attachments.py` so `.eml` files saved by PowerShell `Set-Content -Encoding UTF8` parse RFC 822 headers cleanly.
  - [x] End-to-end headless Chrome PDF print + `fitz` text verification smoke test passed in PowerShell.
- [x] **Phase 2.2: Classic Expensify by default (`feat/classic-expensify-default`, v1.2.0, 2026-11-19)**
  - [x] New Expensify froze the Chrome tab on several reports; classic www.expensify.com is now the default for opening the report, entering lines, Mark As Cash and checks.
  - [x] Classic recipe in `references/expensify-web-entry.md`: New Expense dialog, jQuery UI date pick, category search, receipt upload to `input[name=expense_attach]` (no drop trick), Save, never Escape, Mark As Cash per line, server check by reloading the report page. New Expensify recipe kept as a fallback.
  - [ ] Still untried on classic: per diem, attendees, report rename, report creation, the category read in the setup interview, and the Antigravity `/browser` mapping.
- [x] **Phase 2.3: Ported maintainer fixes (`fix/port-private-fixes`, v1.3.0, 2026-11-19)**
  - [x] `trim_after()` in `scripts/gmail_html_to_pdf.py` read `page_count` after `close()` and raised `ValueError` whenever the marker was missing or on the last page.
  - [x] New Expensify fallback: confirm lines on the classic report page, move in-app with `history.pushState` instead of full reloads, JS by aria-label for fields and Upload receipt, visible Save on rename, Create report flow, Attendees picker, deleting lines from a draft, per diem times can stay at 12:00 AM, JS time limit on long loops.
  - [x] New config flag `expensify.always_mark_as_cash` (default false) with setup-interview question 10; when true the agent clears "Awaiting merge" on every line before hand-off.

