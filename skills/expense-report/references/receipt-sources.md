# Receipt sources

All queries run against the personal Gmail account:
- **When a Gmail MCP connector is available** (Claude Desktop/Code or Antigravity with a Gmail MCP server): use `search_threads`, then `get_thread` with `PLAIN_TEXT` to read, `get_message` with `FULL_CONTENT` for the HTML body, and `RAW` for attachments. Results over the size limit are saved to a file under `~/.claude/projects/<project>/<session>/tool-results/`; copy them to the short work folder and read them with Python (`json.load`), never by pasting.
- **When running in Antigravity without a Gmail MCP connector:** ask the user to sign in to their personal Gmail account in a browser tab (`https://mail.google.com/mail/u/0/` or `/u/1/` so it stays separate from any work Google session), run the search queries below in Gmail's search bar, and fetch each needed message's raw RFC 822 `.eml` from Gmail's "Show original" view (`?ui=2&view=om&th=<message_id>`) into the short work folder (`config.receipts.work_dir`). Both `scripts/gmail_html_to_pdf.py` and `scripts/gmail_raw_attachments.py` accept `.eml` files directly alongside Gmail MCP JSON files.

## Find the trip window
- Searching on the event name usually returns nothing; the trip is found by vendor emails instead.
- Broad sweep for a date range: `after:YYYY/MM/DD before:YYYY/MM/DD -category:promotions -category:social` and scan subjects. Exclude the rideshare sender once you have its receipts to keep the sweep readable.
- Weekday clusters of rides between home and one address, with no flights, are a local event; confirm the venue and dates with a quick web search before naming the trip.

## By vendor (senders come from `config.sources`)

| Vendor | Query | What it yields |
|---|---|---|
| Travel agency / card travel service | `from:<sources.travel_agency> "Confirmed: your trip"` | one email per booking: flights (total trip cost, ticket number, confirmation code, seats) and hotels (total cost, confirmation number, dates). Booked the day before travel is normal. |
| Airline | `from:<sources.airlines>` | purchase receipts (seat upgrades, often paid with miles: not reimbursable), check-in reminders (flight number and times), disruption hotel vouchers (contain a virtual card number: never turn one into a receipt file). |
| Rideshare | `from:<sources.rideshare> after:... before:...` | per ride: a "charge summary" first, then the final "Thanks for riding/tipping" receipt with payment card and route. Subjects may carry profile tags such as "[Personal]" or "[Family]". Use the final receipt. Food-delivery orders from the same sender are personal. |
| Hotel chain | `from:<sources.hotels>` | "We hope you enjoyed your stay" with the folio PDF attached (folio shows a $0 balance for prepaid stays). Some chains send no folio; use the agency confirmation. |
| Carrier | `from:<sources.carrier> "bill is ready"` | monthly, shows the total amount due. |
| Lyft / taxi / parking / baggage / registration | `(lyft OR taxi OR shuttle OR parking OR baggage OR registration) after:... before:...` | usually empty; confirms a gap. |

## What never arrives in personal Gmail
- Management approval (team chat, or the work mailbox in Chrome's Google session).
- Rides paid by colleagues, hotel-provided shuttles.
- Event registration paid by the company.
- The carrier's full PDF bill (the user downloads it if the email is not enough).

## Gmail connector & browser notes
- No attachment download tool in the Gmail MCP connector. Use `get_message` with `messageFormat: "RAW"` (or a raw `.eml` file from Gmail's "Show original" view); the MIME parts contain the PDF/image attachments, and `scripts/gmail_raw_attachments.py` extracts them.
- `get_thread` does not support RAW; `get_message` does.
- When using the Gmail MCP connector, Chrome's Google session typically holds only the work account—do not navigate Gmail in Chrome for personal mail unless running the browser `.eml` fallback with the user signed in to their personal Gmail tab.
