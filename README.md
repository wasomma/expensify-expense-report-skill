# Expensify expense-report skill for Claude Code

A Claude Code skill that does the tedious part of a travel expense report: it finds the trip in your Gmail, turns the booking confirmations, rideshare receipts, hotel folios and carrier bill into receipt PDFs, reconciles them against your own coding conventions, asks you the handful of questions a human would ask, and enters every line with its receipt into your draft report in New Expensify. It stops before Submit. You click that.

It was built for one traveler's real workflow and then generalized: everything personal lives in a config file on your machine that a setup interview writes for you. Nothing in this repo knows who you are.

## What it assumes

- You pay on personal cards and get reimbursed (no corporate card on the report).
- Your receipts arrive in a personal Gmail account.
- Your company uses New Expensify (new.expensify.com), and you create the draft report yourself before the trip.
- You run Claude Code in the desktop app with the **Claude in Chrome** extension and the **Gmail** connector.

## Safety rules the skill never bends

- It never clicks Submit.
- It never types a password or magic code; when a site wants a login, it stops and asks you to sign in in that tab.
- It shows you every proposed line and waits for your answers before entering anything.
- It keeps only the last four digits of any card, and only in your local config.
- It reads your personal Gmail through the connector only; it does not open your work mailbox unless you ask.

## Requirements

| Need | Notes |
|---|---|
| Claude Code desktop app | Skills and the Chrome extension both run there |
| Claude in Chrome extension | Signed in to the Chrome profile you use for Expensify |
| Gmail connector | Connected to the personal account that receives receipts |
| Google Chrome | Used headlessly to print emails to PDF (Edge works less reliably) |
| Python 3 with PyMuPDF | `pip install pymupdf` |
| `pdftotext` on PATH | Part of poppler; Git for Windows ships one |

Windows is the tested platform. The Chrome recipe is browser-side and should carry over to macOS; the scripts take forward-slash paths.

## Install

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

## First run: the setup interview

Say something like "set up my expense report skill", or run `/expensify-expense-report:expense-report`. With no config present the skill runs the interview in [setup-interview.md](skills/expense-report/references/setup-interview.md): it checks the tools, asks about your accounts, workspace, approver, cards (last four only), receipt folders, booking senders and policy, reads the category names from your own Expensify workspace, writes `~/.claude/expense-report/config.yaml`, and does a dry run on a past trip so you can compare its reconciliation with what you actually submitted. The template with every field explained is [config.example.yaml](config.example.yaml).

## Everyday use

1. Create the draft report in Expensify as you normally do, and sign in to Expensify in Chrome.
2. Tell Claude: "fill out my expense report for the <event> trip".
3. It finds the trip in Gmail, builds the receipt PDFs into your trip folder, and shows you a table of proposed lines plus the standard questions with defaults (rides without receipts, evening rides, per diem span, the carrier bill, the approval screenshot, the report title). Answer in one line or ask for the questions one at a time.
4. It enters the lines with receipts, verifies the report total, and tells you what is still open. The reconciliation file in the trip folder is its checkpoint; if the session dies, the next one resumes from it.
5. You attach anything only you have (paste the approval screenshot into chat) and click Submit.

## How it works

- **Gmail**: vendor-sender searches in a date window, then the final receipt emails fetched as HTML and printed to PDF with headless Chrome; attachments pulled out of the RAW MIME message, so nothing needs a browser download.
- **Reconciliation**: one markdown table per report, written before entry and updated after every line.
- **Expensify**: driven through Claude in Chrome. The receipt step hands the file to Expensify's own upload zone through a synthetic drop event, because the page ignores programmatic file inputs. Dates and categories are picked through the real calendar and picker. Every form is read back before Create is clicked. Details in [expensify-web-entry.md](skills/expense-report/references/expensify-web-entry.md).

## Known limits

- Corporate cards and mixed reports are out of scope.
- Travel-agency and rideshare websites need your login each time; the emails are enough and are what approvers have accepted.
- Expensify flags manual expenses with "Awaiting merge with card transaction" and sometimes "Date differs from scanned receipt". Both are notices, not violations; the skill can clear the first on request.
- Per diem rates are read-only once a line exists; a wrong subrate means delete and recreate.

## Contributing

Keep the repo free of personal data: no names, emails, addresses, card fragments, report IDs or employer details, including in examples. Run `python tools/pii_scan.py` before opening a pull request; add private names to a terms file outside the repo and pass it with `--terms`. When you verify or change a browser recipe, say so with a date in the reference file, since Expensify's UI moves.

## License

MIT. See [LICENSE](LICENSE).
