# Entering lines in New Expensify in Chrome (Claude in Chrome & Antigravity `/browser`)

Verified on `new.expensify.com` (2026-10-15). All DOM selectors, React value setters, and the `#probeX` + synthetic `DataTransfer` `DragEvent('drop')` receipt upload work identically across **Claude in Chrome** and **Google Antigravity (`/browser`)**.

## Harness Tool Equivalence

| Action | Claude in Chrome (`mcp__claude-in-chrome__*`) | Google Antigravity (`/browser` tools) |
|---|---|---|
| Open / navigate URL | `tabs_context_mcp` + `navigate` | `open_browser_url` (or `list_browser_pages` / `select_browser_page`) |
| Find / inspect DOM elements | `find` / `read_page` | `read_browser_page` / `get_dom_tree` / `execute_browser_javascript` |
| Read visible page text | `get_page_text` | `read_browser_page` or `execute_browser_javascript` (`document.body.innerText`) |
| Run page JavaScript | `javascript_tool` | `execute_browser_javascript` |
| Click / type / scroll | `computer` (`left_click`, `type`, `key`, `scroll`) | `click_browser_pixel`, `type_browser_text`, `press_browser_key`, `scroll_browser_page` (or JS `.click()`) |
| Populate `#probeX` file input | `file_upload` on the `#probeX` ref | `upload_file_to_browser` targeting `#probeX` (`input#probeX`) |
| Batch multiple actions | `browser_batch` | Sequential or batched `/browser` calls / combined JS |

In Claude Code, load the tools in one ToolSearch: `tabs_context_mcp`, `navigate`, `computer`, `find`, `read_page`, `get_page_text`, `javascript_tool`, `browser_batch`, `file_upload`, `tabs_create_mcp`, `tabs_close_mcp`.

## Setup
1. Open or attach to the browser (`tabs_context_mcp` in Claude in Chrome, or `open_browser_url` in Antigravity), then navigate to `https://new.expensify.com/home`. If the sign-in page appears ("Phone or email"), stop and ask the user to sign in in that tab. With company SSO the Google button fails with "requires SAML"; the user types the work email and completes SSO. Sessions expire between days.
2. Reports list: `https://new.expensify.com/search?q=type%3Aexpense-report%20status%3Aall`. Find the user's draft row (From = the user, status Draft) and click its **View** button; the report opens in a right pane at `/search/r/<reportID>`. Keep the reportID. A JS `.click()` on the row does not open it; the ref/pixel click on View does.
3. Read the page text (`get_page_text` or `read_browser_page`) on a report pane to see every line (date, merchant, description, category, amount) plus the total. Use it to verify after each line.

## Create a manual line (airfare, rides, hotels, cell, approval)
1. Navigate directly to `https://new.expensify.com/create/submit/start/1/<reportID>/manual`. A full navigation resets page-level patches (step 2), so repeat them every time.
2. Run this JavaScript once per page load: patch every `input[type=file]` so `.click()` is a no-op (prevents the native picker, which the browser automation cannot see), and add a probe input:
   ```js
   for (const el of document.querySelectorAll('input[type=file]')) { el.click=function(){}; }
   if(!document.getElementById('probeX')){ const t=document.createElement('input'); t.type='file'; t.id='probeX'; t.setAttribute('aria-label','ProbeX'); t.style.cssText='position:fixed;top:40px;left:0;z-index:99999;width:200px;height:30px'; document.body.appendChild(t); }
   ```
3. Locate "Amount textbox, Merchant textbox, Description textbox, Category button, Date combobox, 'Upload receipt' button, ProbeX file input, and 'Create expense' button" (`find` in Claude in Chrome, or DOM inspection in Antigravity). These are the only targets a line needs.
4. Text fields: click the field and type (`computer type` or `type_browser_text`). Verify with JS: `document.querySelector('[aria-label="Amount"]').value` (and Merchant, Description).
5. Date: typing into the combobox does nothing. Click it to open the calendar, then JS-click the day: `[...document.querySelectorAll('button,[role=button]')].find(e=>(e.getAttribute('aria-label')||'').includes('October 12, 2026')).click()`. Verify `[aria-label="Date"]` reads `2026-10-12`. The calendar opens on the current month; use its month arrows for older dates.
6. Category: click the Category button, then JS-click the option: `[...document.querySelectorAll('[role=option]')].find(e=>e.innerText.trim()==='<category name>').click()`. Only recently used categories render without searching; for a new one, click the picker's "Search" textbox, type part of the name, then click the option. Verify the Category button's aria-label reads "Category, <name>".
   - The $0.00 approval line works exactly like any other manual line: amount 0.00, merchant and description per config, the approval category, date of the approval, PNG screenshot as receipt.
7. Receipt (the only part that needs a trick):
   - Upload the PDF or PNG to the `#probeX` input (`file_upload` in Claude in Chrome, or `upload_file_to_browser` in Antigravity).
   - Click the "Upload receipt" control. It navigates to Expensify's Receipt page with an "Upload receipt / or drag and drop it here" zone. Its own file input ignores programmatic files.
   - Dispatch a drop on the zone:
     ```js
     const f=document.getElementById('probeX').files[0]; const dt=new DataTransfer(); dt.items.add(f);
     const target=[...document.querySelectorAll('[role=dialog] div')].find(el=>(el.innerText||'').trim().startsWith('Upload receipt') && el.querySelectorAll('*').length<40);
     const mk=t=>new DragEvent(t,{bubbles:true,cancelable:true,dataTransfer:dt});
     target.dispatchEvent(mk('dragenter')); target.dispatchEvent(mk('dragover')); target.dispatchEvent(mk('drop'));
     ```
     The form returns with a thumbnail. Confirm with JS: `document.body.innerText.includes('Upload receipt') === false` and a button whose aria-label contains "View attachment" exists.
   - Wrong file attached? Click the thumbnail, use **Replace** (opens the same drop zone), drop again.
8. Read the whole form back in one JS call (amount, merchant, description, date, category label, receipt present). Only then click "Create expense". Wait 5 s, then confirm the amount appears in the expenses list or report pane.
9. The page CSP blocks `fetch` to localhost, so a local file server does not help; the probe-input route is the working one.

## Two round trips per line
Batch 1: navigate + patch + `find` (refs). Batch 2: all of steps 4 to 8 up to the read-back. Batch 3: Create expense + verify + navigate and patch for the next line + `find`. Refs change on every navigation, so never reuse them across lines. If a mid-batch check fails, the following actions still run; put the read-back last and look at it before clicking Create.

## Per diem line
1. Navigate to `https://new.expensify.com/create/submit/start/1/<reportID>/per-diem`.
2. Click the destination (for example "Domestic US").
3. Time page: Start date and End date via the calendar (as above). Start time and End time open a clock page: click the hour digits, `ctrl+a`, type "05"; minutes, type "00"; the AM/PM toggle defaults to AM; click that page's Save. Then the time page's Save.
4. Subrate page: click "Subrate". The list has no search box and is virtualized. Scroll the list with `computer scroll` at the panel, 10 ticks at a time, and read `[role=option]` texts with JS until the destination city appears. `scroll_to` the ref, click it. Quantity per config (nights or days). Save. The "Standard" rate is usually lower than the city subrate; use the city.
5. Confirm details page: Description, Date (calendar), then "Create expense". Category is set to the per diem category automatically; merchant becomes "Domestic US, <start> to <end>".
6. Rates on a created per diem are read-only. To change the subrate, open the line, **More > Delete** (confirm in the modal), and recreate.

## Renaming the report
1. In the report pane, click the title button (the report name in the header); the details page opens at `/search/r/<reportID>/details`.
2. `find` and click the "Title, <current name>" row. The edit page opens with the Title textarea already focused. Do not click the textarea: a click blurs it and the typed text is lost.
3. `ctrl+a`, then `computer type` the new title. Verify with JS: `document.querySelector('textarea[aria-label="Title"]').value`.
4. Click Save through JS (`[...document.querySelectorAll('button')].find(b=>b.innerText.trim()==='Save').click()`); the details page returns showing the new title. `document.title` lags behind; read the body text instead.

## Clearing "Awaiting merge with card transaction"
Manual expenses sit in "pending match" waiting for a card-feed transaction; with no connected card it never comes. It is a notice, not a violation, and paid reports have carried it; clear it only if the user asks. Open any expense from the report pane (row button "View details", page `/search/view/<transactionID>`), click the **Mark as cash** button under the pending-match notice, then step through the report with the header pager ("2 of 9"): the pager container holds two buttons, `[prev, next]`, and a JS `.click()` on `next` works; refs go stale after each step. "Mark as cash" can also be clicked through JS by its text. The next button is disabled on the last expense (no wrap). "Date differs from scanned receipt" is a separate notice and stays unless the expense date is changed.

## Reading and cleaning up
- Expense detail pages are `/search/view/<transactionID>`; the header **More** menu holds Hold, Split, Merge, Duplicate, Move to report, Delete.
- The composer "+" inside the report pane is for tasks and attachments, not expenses.
- `location.href` and `location.pathname` are often redacted by the extension when the URL carries a search key; read `document.title` or the body text instead.
- Close the tabs you created except the report tab. The Chrome extension occasionally disconnects mid-batch; call `tabs_context_mcp`, check the page state with JS, and continue from where it stopped.
