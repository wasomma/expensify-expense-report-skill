---
name: expense-report
description: Build and enter a reimbursable expense report in New Expensify from the user's Gmail receipts. Use whenever the user mentions an expense report, ER, Expensify, reimbursement, per diem, a cell-phone claim, or receipts for a work trip, or names a folder under their receipts root. On first use it runs a setup interview that records accounts, workspace, cards, folders and policy in a local config file. It then finds the trip in Gmail, turns emails and attachments into receipt PDFs, reconciles them against the user's conventions, asks the standard questions, and enters every line with its receipt into the pre-created draft report through Claude in Chrome, stopping before Submit.
---

# Expense report (New Expensify)

Reproduces, end to end, the manual process of a traveler who fronts costs on personal cards and submits one report per trip in New Expensify: find the receipts in Gmail, turn them into PDFs, reconcile, enter the lines with receipts, stop before Submit.

## Ground rules (not configurable)

- Never click **Submit**. Leave the report in Draft and tell the user; they submit. Creating, editing and deleting lines in their own draft is fine.
- The user signs in to Expensify, Gmail, rideshare and card sites themselves. Never type credentials. If a site shows a login page, stop and ask them to sign in in that tab, then continue.
- Read personal Gmail only through the Gmail connector. The work mailbox is what Chrome's Google session holds; do not read it unless the user asks for that mailbox.
- Never write full card numbers, CVCs or account numbers into files you create. Last four digits are fine.
- Show the user every proposed line (date, merchant, amount, category, description, receipt) and get their answers to the standard questions before entering anything.
- Drive Expensify with Claude in Chrome (`mcp__claude-in-chrome__*`), never the in-app browser pane.

## Configuration

Everything personal or company-specific lives in `~/.claude/expense-report/config.yaml` (template: `config.example.yaml` at the repo root). Read it at the start of every run. If it is missing or has blank required fields, run `references/setup-interview.md` first. Config values are referenced below as `config.<section>.<key>`. Never copy them into files that could be committed.

## Workflow

### 0. Session setup
1. Read the config. `change_directory` to `config.receipts.root` (the folder that holds one subfolder per report).
2. Find or confirm the trip folder (`config.receipts.folder_pattern`). If `_<report number> reconciliation.md` exists inside it, read it first: it is the checkpoint and tells you what is already entered.
3. Read `references/conventions.md` for coding rules and `references/receipt-sources.md` for Gmail queries.

### 1. Discover the trip in Gmail
Search personal Gmail for the booking confirmations, airline emails, rideshare receipts, hotel folios and the carrier bill in the trip window, using the senders in `config.sources`. Build the itinerary: dates, flights, hotels, rides. Search for disruptions too (airline hotel vouchers, rebookings). Note gaps (a ride with no receipt) instead of inventing lines. A trip with no flights or hotel is normal for a local event: the rides alone define it.

### 2. Capture receipts into the trip folder
- Email bodies become PDFs with `scripts/gmail_html_to_pdf.py` (headless Chrome). Fetch each message with `get_message` `FULL_CONTENT`; the connector saves large results to a file, and the script reads that file. Copy those files into the short work folder (`config.receipts.work_dir`) first: their original path is often too long for Python on Windows. Travel-agency confirmations carry pages of boilerplate: pass `--trim-after "Card Number"` (or whatever text ends the payment page) to keep only the itinerary and payment pages.
- Email attachments (hotel folio PDFs, etc.) come out of `get_message` with `messageFormat: "RAW"` through `scripts/gmail_raw_attachments.py`. No browser download is needed.
- Merge a booking confirmation and the hotel folio into one PDF with `scripts/merge_pdfs.py`; Expensify holds one receipt per expense.
- Verify every PDF with `pdftotext` for its total before using it. The script already checks for the expected string and prints PASS or FAIL per file.
- Name files by type and date, e.g. `Ride 1 - 0921 Home to Airport.pdf`, `Flights - <airline> <locator> via <agency>.pdf`, `Hotel 1 - <name> (confirmation + folio).pdf`. Keep a "(not claimed)" suffix on anything captured for the record only.
- Long scratch paths (over 240 characters) break Python and the headless browser; work in a short folder such as `C:\Users\<you>\AppData\Local\Temp\claude\er-work`. Output the PDFs straight into the trip folder.

### 3. Reconcile and ask
Write `_<report number> reconciliation.md` in the trip folder: one row per expected line (date, merchant, category, amount, description, receipt file, entered yes/no) plus the items seen but not claimed and the open items. Then give the user the table and the standard questions from `references/conventions.md`, each with a default. Users often answer "defaults accepted"; some want the questions one at a time, so offer that. Update the file as answers arrive; it is the resume point if the session dies.

### 4. Enter lines in Expensify
Follow `references/expensify-web-entry.md` exactly. Summary: open the draft report, use the direct create URL, fill the Manual form, pick the date in the calendar, pick the category, attach the receipt by handing the file to Expensify's own Receipt page through a synthetic drop event (the plain file input is ignored), verify the form by reading it back, then Create expense. Per diem goes through the Per diem tab with the destination subrate. Verify the report total after each line and mark the line entered in the reconciliation file.

### 5. Verify and hand off
1. Read the report pane: every line present once, amounts match the reconciliation, total matches, title matches the pattern in `config.policy.title_pattern` (rename if the user agreed).
2. Note Expensify's warnings ("Awaiting merge with card transaction", "Date differs from scanned receipt"); they do not block submission but tell the user. The first can be cleared with Mark as cash if the user asks (see the entry reference).
3. Update the reconciliation file with what is entered and what is still open (approval screenshot, missing receipts).
4. Report: lines entered, total, open items, and that Submit is theirs. Send a push notification if the harness offers one.
5. Close the tabs you opened except the Expensify report tab.

## What works and what does not

| Source or action | Status |
|---|---|
| Personal Gmail bodies to PDF | Works, no user action (headless Chrome; Edge returns before writing the PDF on current builds) |
| Gmail attachments (folio PDFs) | Works through the RAW message parse, no download prompt |
| Rideshare, airline, travel-agency, hotel and carrier emails | All capturable from Gmail |
| Expensify line creation with receipt | Works through Chrome with the drop-event recipe (PDF and PNG) |
| Expensify per diem | Works; pick the destination subrate, quantity per `config.policy.per_diem.quantity` |
| Expensify report rename, Mark as cash | Works; recipes in the entry reference |
| Expensify Submit | Never; the user clicks it |
| Travel-agency and rideshare websites | Need the user's login each time; the emails suffice |
| Management approval evidence | Comes from chat or the work mailbox; the user supplies it (paste an image, drop a file in the folder) or asks for the work mailbox to be searched |
| Corporate cards | Not handled; the skill is for reimbursable personal-card spend |

## Files
- `references/setup-interview.md` — first-run interview that writes the config and does a dry run.
- `references/conventions.md` — line coding, per diem, cell, approvals, titles, the standard questions.
- `references/receipt-sources.md` — Gmail queries by sender and what never arrives in Gmail.
- `references/expensify-web-entry.md` — exact Chrome recipe: receipt drop trick, per diem flow, rename, Mark as cash, batching.
- `scripts/gmail_html_to_pdf.py`, `scripts/gmail_raw_attachments.py`, `scripts/merge_pdfs.py`.
