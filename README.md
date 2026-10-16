# Expensify expense-report skill (Claude Code & Google Antigravity)

A dual-harness agent skill (for **Claude Code** and **Google Antigravity**) that does the tedious part of a travel expense report: it finds the trip in your Gmail, turns the booking confirmations, rideshare receipts, hotel folios and carrier bill into receipt PDFs, reconciles them against your own coding conventions, asks you the handful of questions a human would ask, and enters every line with its receipt into your draft report in New Expensify. It stops before Submit. You click that.

It was built for one traveler's real workflow and then generalized: everything personal lives in a config file on your machine that a setup interview writes for you. Nothing in this repo knows who you are.

## What it assumes

- You pay on personal cards and get reimbursed (no corporate card on the report).
- Your receipts arrive in a personal Gmail account.
- Your company uses New Expensify (new.expensify.com), and you create the draft report yourself before the trip.
- You run either:
  - **Claude Code** (with the **Claude in Chrome** extension and the **Gmail** connector), or
  - **Google Antigravity** (using Antigravity's built-in `/browser` Chrome automation, plus either a Gmail MCP server or Gmail's browser `.eml` "Show original" view).

## Safety rules the skill never bends

- It never clicks Submit.
- It never types a password or magic code; when a site wants a login, it stops and asks you to sign in in that tab.
- It shows you every proposed line and waits for your answers before entering anything.
- It keeps only the last four digits of any card, and only in your local config.
- It reads your personal Gmail only (through the connector or your personal Gmail tab); it does not open your work mailbox unless you ask.

## Requirements

| Need | Notes |
|---|---|
| Agent harness | **Claude Code** desktop app or **Google Antigravity** |
| Browser automation | **Claude in Chrome** extension (Claude Code) or built-in `/browser` Chrome session (Antigravity) |
| Personal Gmail access | **Gmail connector / MCP** (`search_threads`, `get_message`) or **personal Gmail in Chrome** (`Show original` `.eml` parsed by the helper scripts) |
| Google Chrome | Used headlessly to print emails to PDF (Edge works less reliably) |
| Python 3 with PyMuPDF | `pip install pymupdf` (handles PDF trimming, merging, and text verification) |
| `pdftotext` (optional) | Part of poppler / Git for Windows (`/mingw64/bin`); only needed if `pymupdf` is absent |

Windows is the tested platform. The Chrome recipe is browser-side and should carry over to macOS; the scripts take forward-slash paths.

## Install

### Claude Code

From inside a Claude Code session:

```
/plugin marketplace add wasomma/expensify-expense-report-skill
/plugin install expensify-expense-report@expensify-expense-report-skill
```

Or from a shell:

```bash
claude plugin marketplace add wasomma/expensify-expense-report-skill
claude plugin install expensify-expense-report@expensify-expense-report-skill
```

If you have no GitHub SSH key, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` first so the clone goes over HTTPS. Updates: `/plugin marketplace update expensify-expense-report-skill`.

Manual alternative: clone the repo and copy `skills/expense-report` into `~/.claude/skills/expense-report`.

### Google Antigravity

Clone or copy the repository into your Antigravity plugins directory (the root `plugin.json` is discovered automatically):

```bash
git clone https://github.com/wasomma/expensify-expense-report-skill ~/.gemini/config/plugins/expensify-expense-report
```

Both harnesses share the same configuration file at `~/.claude/expense-report/config.yaml` (with `~/.config/expense-report/config.yaml` as a fallback).

## First run: the setup interview

Say something like "set up my expense report skill", or run `/expensify-expense-report:expense-report`. With no config present the skill runs the interview in [setup-interview.md](skills/expense-report/references/setup-interview.md): it checks the tools, asks about your accounts, workspace, approver, cards (last four only), receipt folders, booking senders and policy, reads the category names from your own Expensify workspace, writes `~/.claude/expense-report/config.yaml`, and does a dry run on a past trip so you can compare its reconciliation with what you actually submitted. The template with every field explained is [config.example.yaml](config.example.yaml).

## Everyday use

1. Create the draft report in Expensify as you normally do, and sign in to Expensify in Chrome.
2. Tell the agent: "fill out my expense report for the <event> trip".
3. It finds the trip in Gmail, builds the receipt PDFs into your trip folder, and shows you a table of proposed lines plus the standard questions with defaults (rides without receipts, evening rides, per diem span, the carrier bill, the approval screenshot, the report title). Answer in one line or ask for the questions one at a time.
4. It enters the lines with receipts, verifies the report total, and tells you what is still open. The reconciliation file in the trip folder is its checkpoint; if the session dies, the next one resumes from it.
5. You attach anything only you have (paste the approval screenshot into chat) and click Submit.

## How it works

- **Gmail**: vendor-sender searches in a date window, then the final receipt emails fetched as HTML (or `.eml` RFC 822 original) and printed to PDF with headless Chrome; attachments pulled out of the RAW MIME / `.eml` message, so nothing needs a manual browser download.
- **Reconciliation**: one markdown table per report, written before entry and updated after every line.
- **Expensify**: driven in Chrome through **Claude in Chrome** or **Antigravity `/browser`**. The receipt step hands the file to Expensify's own upload zone through `#probeX` and a synthetic `DataTransfer` drop event, because the page ignores programmatic file inputs. Dates and categories are picked through the real calendar and picker. Every form is read back before Create is clicked. Details in [expensify-web-entry.md](skills/expense-report/references/expensify-web-entry.md).

## Known limits

- Corporate cards and mixed reports are out of scope.
- Travel-agency and rideshare websites need your login each time; the emails are enough and are what approvers have accepted.
- Expensify flags manual expenses with "Awaiting merge with card transaction" and sometimes "Date differs from scanned receipt". Both are notices, not violations; the skill can clear the first on request.
- Per diem rates are read-only once a line exists; a wrong subrate means delete and recreate.

## Contributing

Keep the repo free of personal data: no names, emails, addresses, card fragments, report IDs or employer details, including in examples. Run `python tools/pii_scan.py` before opening a pull request; add private names to a terms file outside the repo and pass it with `--terms`. When you verify or change a browser recipe, say so with a date in the reference file, since Expensify's UI moves. Bump `version` in both `.claude-plugin/plugin.json` and `plugin.json` with every change that users should pick up; installed copies stay on the cached version until the marketplace or plugin directory is updated.

## License

MIT. See [LICENSE](LICENSE).
