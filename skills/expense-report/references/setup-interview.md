# Setup interview (first run)

Run this when `~/.claude/expense-report/config.yaml` (or `~/.config/expense-report/config.yaml`) is missing, when a required field is blank, or when the user asks to redo setup. The goal is a config file that lets later runs work without asking the same questions again, plus one dry run so the user sees what the skill produces before trusting it.

Ask in groups, one group per message, each question with a marked default. Use the question tool (`ask_question` / `AskUserQuestion`) when the harness has one; otherwise ask in plain text. Accept "defaults" as an answer to a whole group. Do not ask for anything that is not used by the workflow.

## 0. Tool check (before the questions)

Verify each item and tell the user what is missing. Nothing below needs credentials.

| Need | How to verify | If missing |
|---|---|---|
| Browser automation (Claude in Chrome or Antigravity `/browser`) | `mcp__claude-in-chrome__tabs_context_mcp` returns a tab group, or Antigravity `/browser` (`open_browser_url` / `list_browser_pages`) is available | In Claude Code, ask the user to install the Claude in Chrome extension; in Antigravity, use `/browser` |
| Personal Gmail access (Gmail MCP connector or browser `.eml` fallback) | `search_threads` with `newer_than:1d` returns threads, or in Antigravity confirm the user can sign in to personal Gmail in a browser tab | Connect the Gmail MCP connector, or sign in to personal Gmail in Chrome when prompted |
| Google Chrome (headless print) | `C:\Program Files\Google\Chrome\Application\chrome.exe` exists (or the macOS/Linux equivalent) | Edge is the fallback but returns before writing on current builds |
| Python 3 with PyMuPDF | `python -c "import fitz"` | `pip install pymupdf` |
| pdftotext on PATH | `pdftotext -v` | Install poppler (Git for Windows ships one in `/mingw64/bin`) |

## 1. Identity and accounts

1. Name as Expensify displays it. (No default.)
2. Work email used to sign in to Expensify. (No default.)
3. How Expensify sign-in works: company SSO through the work email (default), a magic code emailed to the work address, or the Google button. With SSO the Google button fails ("requires SAML"); the user types the work email and completes SSO in the Chrome tab.
4. Personal Gmail address that receives travel receipts. (No default.)
5. Should the agent ever search the work mailbox in Chrome? Default: no; the user supplies anything that only exists there.

## 2. Expensify workspace

6. Workspace name the report is submitted in. (Read it from the "Submits to" line on the create-expense form if the user is unsure.)
7. Approver the report submits to. (Same source.)
8. Does the user create the draft report before the trip? Default: yes; the agent adds lines to that draft and never creates a second report. If no, the agent creates the report from the first expense and says so.
9. Report title pattern. Default: `<Event> <Mon> / Cell Bill <Mon>`; the agent proposes a title and the user confirms the rename.

## 3. Payment

10. Any company card? If yes, stop: this skill only handles reimbursable spend on personal cards, and mixed reports need a different flow.
11. Personal cards, label and last four digits only: which card books flights and hotels, which card pays rides. The last four are used to tell the user's receipts apart from family or shared profiles.

## 4. Home base

12. Home city and airport. Default: derive from the most recent rideshare receipt's pickup address and the first flight's origin, then confirm.
13. Addresses to recognise in ride receipts (office, usual venues). Optional.

## 5. Receipts on disk

14. Receipts root folder (one subfolder per report). Default: `Documents/Expense Reports/<year>`.
15. Folder naming pattern. Default: `NNYY_<trip name>` where NN is the running report number for the year.
16. Short scratch folder for the PDF step. Default: `C:/Users/<you>/AppData/Local/Temp/claude/er-work`.

## 6. Booking sources

17. Travel-agency confirmation sender (card travel service, corporate booking tool). Default: find it by searching Gmail for `"your trip" OR "itinerary" newer_than:180d` and asking the user which sender is theirs.
18. Airlines, hotel chains, rideshare apps, phone carrier. Default: whatever the last 180 days of Gmail show from `references/receipt-sources.md`'s sender list; confirm the list with the user.

## 7. Policy

19. Per diem: claimed? Default: yes, destination subrate, quantity = nights, none for same-day local events.
20. Cell phone: claimed monthly? Default: yes, flat amount the user names (or full bill), international roaming add-ons claimed in full as a separate line, receipt = the carrier's "bill is ready" email.
21. Meals: receipts for team meals, or per diem only? Default: receipts.
22. Management approval line: required? Default: yes, a `$0.00` line whose receipt is a screenshot of the approver's reply; the user pastes the image into chat or drops it in the trip folder.
23. Anything the approver has trimmed or asked for before (for `policy.notes`).

## 8. Categories (from the user's own Expensify)

With the user signed in, open `https://new.expensify.com/create/submit/start/1/<any draft reportID>/manual`, click Category, and read every `[role=option]` text (type a letter in the picker's Search box to page through the full list; only recent categories render without searching). Propose the mapping for airfare, ride, hotel, per diem, cell, meal, approval, training and misc, and confirm it. Store the exact category names.

## 9. Write the config

Write `~/.claude/expense-report/config.yaml` from `config.example.yaml` with the answers. Show the user the file path and remind them it holds personal details and must never be committed. Create the receipts root if it does not exist.

## 10. Dry run

Pick the user's most recent completed report (they name the trip or folder) and run steps 1 to 3 of the workflow only: discover the trip in Gmail, capture the receipts into a scratch copy of the folder, write the reconciliation table, and compare it with what they actually submitted. Differences become `policy.notes` or corrections to the sender lists. Do not enter anything in Expensify during the dry run. Finish by telling the user how to start a real run: name the trip or the folder.
