# Coding conventions

Values in angle brackets come from `~/.claude/expense-report/config.yaml`.

## Where things live
- Receipts: `<receipts.root>/<folder_pattern>/`, receipts only, plus the `_<NN><YY> reconciliation.md` checkpoint this skill writes.
- Expensify: New Expensify (new.expensify.com), workspace `<expensify.workspace>`, "Submits to `<expensify.approver>`". Reports the user approves for other people appear in the same lists; ignore them.
- The user pre-creates the draft report before the trip (`expensify.precreated_drafts`). Auto-named drafts look like "<Name> Expenses on"; find the user's own draft in the reports list (From = the user, status Draft) and add lines to it. Do not create a second report.

## Payment
- No corporate card. Everything is Cash / Reimbursable.
- Flights and hotels: booked through `<sources.travel_agency>` on the travel card ending `<payment.cards[travel].last4>`; one confirmation email per booking with a "Total Trip Cost" or "Total Cost".
- Rides: paid with the rides card ending `<payment.cards[rides].last4>`. Rideshare apps send a "charge summary" first and the final "Thanks for riding/tipping" receipt later, sometimes the next morning; use the final receipt. Rides on a family or shared profile (subject tag, different rider name, paid by the user) are personal unless the user says otherwise.

## Line coding

| Line | Merchant | Category | Description pattern | Notes |
|---|---|---|---|---|
| Airfare | airline | `<categories.airfare>` | "ORD-BOS round trip Sep 21-22 (conf XXXXXX) to attend <event> in person" | Amount = the agency's total trip cost. Seat upgrades paid with miles are not claimed. |
| Ride | Uber / Lyft | `<categories.ride>` | route and date, e.g. "Home to Convention Center, <event> day 1" | one line per ride; tips included in the total |
| Hotel | hotel name | `<categories.hotel>` | "Hotel, 1 night Sep 21-22 (conf ..., prepaid via <agency>)" | date = checkout; receipt = agency confirmation merged with the folio |
| Disruption hotel | hotel name | `<categories.hotel>` | say why: "Unplanned overnight: return flight disrupted; flew home next morning" | |
| Per diem | auto: "Domestic US, <start> to <end>" | `<categories.per_diem>` | "N days of travel, <dates> (<event>, <city>)" | Per diem tab, destination subrate per `policy.per_diem`, quantity per `policy.per_diem.quantity`. Date = last travel day. |
| Cell | carrier | `<categories.cell>` | "Sep/Oct Monthly Cell (<carrier> bill dated Sep 25, total $X)" | amount per `policy.cell.amount`; roaming add-ons as a separate full line if `policy.cell.roaming_in_full`. Date = bill date. One bill per report. |
| Management approval | `<policy.approval_line.merchant>` | `<categories.approval>` | "mgmt approval" | $0.00 line whose receipt is the approver's reply (screenshot or email print), dated the day of the reply. The user supplies it. |
| Team meal | restaurant | `<categories.meal>` | "Team dinner, <event>" | photo of the receipt; note the tip if it is on the slip |
| Training / exam | vendor | `<categories.training>` | "<cert> exam fee" | rides along with whatever report is open |

Report title pattern: `<policy.title_pattern>`, e.g. "VCTS Solutioning Session Aug / Cell Bill Sep". Propose a title; rename only with the user's agreement.

## Standard questions to ask after reconciling (with defaults)
1. Rides without a receipt in Gmail: default not claimed unless the user drops a receipt in the folder.
2. Rides to or from an evening venue: default claimed when the user confirms a work dinner; the ride home is claimed either way.
3. Disruption hotel vs airline voucher: default claim the hotel the user booked, note the disruption in the description.
4. Rebooked flight with no new fare in Gmail: default airfare stays the original total.
5. Per diem span: default first travel day to last travel day, quantity per config, destination subrate; none for a same-day local event.
6. Carrier bill: default the configured flat amount with the "bill is ready" email as receipt, one bill per report; if the latest bill already went on the previous report, no cell line.
7. Management approval: default the user drops the screenshot into the folder or pastes it in chat.
8. Registration or badge fees paid personally: default none unless a receipt exists.
9. Report title: propose one following the pattern.
10. Entry: default enter everything now, stop before Submit.

## Watch-outs
- A booking expensed early (flights-only report before the trip) must not be claimed again on the trip report. Check the previous folder and the paid reports list.
- Two-traveler bookings: record which share is claimed in the reconciliation file.
- Expensify shows "Awaiting merge with card transaction" on manual expenses while it waits for a card feed that may not exist, and "Date differs from scanned receipt" when the receipt's charge date is the day after the expense. Both are notices, not violations; paid reports have carried them.
- Personal rides, meals and weekend trips in the same Gmail window are easy to sweep in by mistake. List them under "seen but not claimed" so the user can pull any back in.
