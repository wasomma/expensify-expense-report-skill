---
name: expense-report
description: Build and enter a reimbursable expense report in Expensify (classic www.expensify.com by default; New Expensify only as a fallback) from the user's Gmail receipts. Use whenever the user mentions an expense report, ER, Expensify, reimbursement, per diem, a cell-phone claim, or receipts for a work trip, or names a folder under their receipts root. On first use it runs a setup interview that records accounts, workspace, cards, folders and policy in a local config file. It then finds the trip in Gmail, turns emails and attachments into receipt PDFs, reconciles them against the user's conventions, asks the standard questions, and enters every line with its receipt into the pre-created draft report in Chrome (via Claude in Chrome or Antigravity /browser), stopping before Submit.
---

# Expense report (Expensify)

Reproduces, end to end, the manual process of a traveler who fronts costs on personal cards and submits one report per trip in Expensify: find the receipts in Gmail, turn them into PDFs, reconcile, enter the lines with receipts, stop before Submit.

## Ground rules (not configurable)

- Never click **Submit**. Leave the report in Draft and tell the user; they submit. Creating, editing and deleting lines in their own draft is fine.
- The user signs in to Expensify, Gmail, rideshare and card sites themselves. Never type credentials. If a site shows a login page, stop and ask them to sign in in that tab, then continue.
- Read personal Gmail through the Gmail connector (`search_threads`, `get_thread`, `get_message`) when available. When running in Antigravity without a Gmail MCP connector, use the personal Gmail account in a browser tab (`mail.google.com` + "Show original" `.eml` download) after confirming the user is signed in to their personal Gmail there. Never search the work mailbox unless the user explicitly asks for that mailbox.
- Never write full card numbers, CVCs or account numbers into files you create. Last four digits are fine.
- Show the user every proposed line (date, merchant, amount, category, description, receipt) and get their answers to the standard questions before entering anything.
- Drive Expensify in a real Chrome session using Claude in Chrome (`mcp__claude-in-chrome__*`) or Antigravity's `/browser` toolset (`open_browser_url`, `execute_browser_javascript`, `upload_file_to_browser`), never an isolated non-Chrome embedded preview.
- Use **classic www.expensify.com** for everything: opening or creating the report, entering lines, Mark As Cash, checks (2026-11-19). New Expensify (new.expensify.com) froze the Chrome tab on several reports, once as soon as the create-expense URL loaded. Open it only for a step classic cannot do, and tell the user first.

## Configuration

Everything personal or company-specific lives in `~/.claude/expense-report/config.yaml` (or `~/.config/expense-report/config.yaml` as fallback; template: `config.example.yaml` at the repo root). Read it at the start of every run. If it is missing or has blank required fields, run `references/setup-interview.md` first. Config values are referenced below as `config.<section>.<key>`. Never copy them into files that could be committed.

## Workflow

### 0. Session setup
1. Read the config. `change_directory` to `config.receipts.root` (the folder that holds one subfolder per report).
2. Find or confirm the trip folder (`config.receipts.folder_pattern`). If `_<report number> reconciliation.md` exists inside it, read it first: it is the checkpoint and tells you what is already entered.
3. Read `references/conventions.md` for coding rules and `references/receipt-sources.md` for Gmail queries.

### 1. Discover the trip in Gmail
Search personal Gmail for the booking confirmations, airline emails, rideshare receipts, hotel folios and the carrier bill in the trip window, using the senders in `config.sources`. Build the itinerary: dates, flights, hotels, rides. Search for disruptions too (airline hotel vouchers, rebookings). Note gaps (a ride with no receipt) instead of inventing lines. A trip with no flights or hotel is normal for a local event: the rides alone define it.

### 2. Capture receipts into the trip folder
- Email bodies become PDFs with `scripts/gmail_html_to_pdf.py` (headless Chrome).
  - **With a Gmail MCP connector:** Fetch each message with `get_message` `FULL_CONTENT` (or `RAW`); copy large saved tool-result files from `~/.claude/projects/<project>/<session>/tool-results/` into the short work folder (`config.receipts.work_dir`) first so Windows path-length limits do not break Python.
  - **In Antigravity without a Gmail MCP connector:** Save each message's raw RFC 822 `.eml` from Gmail's "Show original" / "Download original" view (`https://mail.google.com/mail/u/<slot>/?ui=2&view=om&th=<msg_id>`) into `config.receipts.work_dir`.
  - Travel-agency confirmations carry pages of boilerplate: pass `--trim-after "Card Number"` (or whatever text ends the payment page) to keep only the itinerary and payment pages.
- Email attachments (hotel folio PDFs, etc.) come out of `get_message` with `messageFormat: "RAW"` or out of the `.eml` file through `scripts/gmail_raw_attachments.py`. No manual browser attachment click-and-save is needed.
- Merge a booking confirmation and the hotel folio into one PDF with `scripts/merge_pdfs.py`; Expensify holds one receipt per expense.
- Verify every PDF with `pdftotext` for its total before using it. The script already checks for the expected string and prints PASS or FAIL per file.
- Name files by type and date, e.g. `Ride 1 - 0921 Home to Airport.pdf`, `Flights - <airline> <locator> via <agency>.pdf`, `Hotel 1 - <name> (confirmation + folio).pdf`. Keep a "(not claimed)" suffix on anything captured for the record only.
- Long scratch paths (over 240 characters) break Python and the headless browser; work in a short folder such as `C:\Users\<you>\AppData\Local\Temp\claude\er-work`. Output the PDFs straight into the trip folder.

### 3. Reconcile and ask
Write `_<report number> reconciliation.md` in the trip folder: one row per expected line (date, merchant, category, amount, description, receipt file, entered yes/no) plus the items seen but not claimed and the open items. Then give the user the table and the standard questions from `references/conventions.md`, each with a default. Users often answer "defaults accepted"; some want the questions one at a time, so offer that. Update the file as answers arrive; it is the resume point if the session dies.

### 4. Enter lines in Expensify
Follow the classic section of `references/expensify-web-entry.md` exactly (Claude in Chrome `mcp__claude-in-chrome__*` or Antigravity `/browser` tools). Summary: open `https://www.expensify.com/report?reportID=<reportID>`, Add Expenses > New Expense, type Merchant, Total and Description, set the date by JS-clicking the day in the jQuery UI calendar, search and click the category, JS-click the receipt box and upload the file to the `input[name=expense_attach]` it creates (no drop trick on classic), read the form back, then Save. Never press Escape in the form: it closes it unsaved. Per diem goes through the Per Diem tab with the destination subrate; classic's Per Diem tab is not yet verified, so check its amount before saving. Reload the report page after each line, check the total, and mark the line entered in the reconciliation file.

### 5. Verify and hand off
1. Reload the classic report page and read it: every line present once, amounts match the reconciliation, total matches, title matches the pattern in `config.policy.title_pattern` (rename if the user agreed). What the reloaded page shows is on the server.
2. Note Expensify's warnings ("Awaiting merge with card transaction", "Date differs from scanned receipt"); they do not block submission but tell the user. The first can be cleared with **Mark As Cash** in each line's Edit Expense dialog if the user asks (see the entry reference).
3. Update the reconciliation file with what is entered and what is still open (approval screenshot, missing receipts).
4. Report: lines entered, total, open items, and that Submit is theirs. Send a push notification if the harness offers one.
5. Close the tabs you opened except the Expensify report tab.

## What works and what does not

| Source or action | Status |
|---|---|
| Personal Gmail bodies to PDF | Works, no user action (headless Chrome; Edge returns before writing the PDF on current builds) |
| Gmail attachments (folio PDFs) | Works through the RAW message parse, no download prompt |
| Rideshare, airline, travel-agency, hotel and carrier emails | All capturable from Gmail |
| Expensify line creation with receipt | Works on classic www.expensify.com: upload straight to the `expense_attach` input, no drop trick (2026-11-19). The New Expensify drop-event recipe is kept as a fallback. |
| Expensify Mark As Cash | Works on classic, in each line's Edit Expense dialog (2026-11-19) |
| Expensify per diem | Works in New Expensify (destination subrate, quantity per `config.policy.per_diem.quantity`); classic Per Diem tab not yet verified |
| Expensify report rename | Recipe verified in New Expensify only; try classic first and record what works |
| Expensify report creation | Classic's Create Report button seen but not yet used; check workspace and approver on first use |
| Expensify Submit | Never; the user clicks it |
| Travel-agency and rideshare websites | Need the user's login each time; the emails suffice |
| Management approval evidence | Comes from chat or the work mailbox; the user supplies it (paste an image, drop a file in the folder) or asks for the work mailbox to be searched |
| Corporate cards | Not handled; the skill is for reimbursable personal-card spend |

## Files
- `references/setup-interview.md` — first-run interview that writes the config and does a dry run.
- `references/conventions.md` — line coding, per diem, cell, approvals, titles, the standard questions.
- `references/receipt-sources.md` — Gmail queries by sender and what never arrives in Gmail.
- `references/expensify-web-entry.md` — exact Chrome recipe: classic www.expensify.com (default: New Expense dialog, receipt upload, Mark As Cash), then the New Expensify fallback (receipt drop trick, per diem flow, rename, batching).
- `scripts/gmail_html_to_pdf.py`, `scripts/gmail_raw_attachments.py`, `scripts/merge_pdfs.py`.
