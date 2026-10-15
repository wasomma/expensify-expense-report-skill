"""Turn Gmail messages (saved get_message FULL_CONTENT results) into receipt PDFs.

Usage (Windows paths shown with forward slashes; quote paths that contain spaces):
  python gmail_html_to_pdf.py --work C:/Users/<you>/AppData/Local/Temp/claude/er-work ^
      --out "<receipts root>/0126_Example Trip" ^
      --item <tool-result.txt> "Ride 1 - 0101 Home to Airport" "$42.14" ^
      --item <tool-result.txt> "Flights - <airline> <locator> via <agency>" "$566.81" --trim-after "Card Number"

Each --item takes: the saved tool-result file (JSON from get_message FULL_CONTENT; the
Gmail connector writes it under ~/.claude/projects/<project>/<session>/tool-results/
when the result is large, or write the JSON yourself), the output name without
extension, and a string that must appear in the PDF text (usually the total).
--trim-after keeps pages up to and including the first page containing that text
(travel-agency confirmations often carry several pages of terms after the payment block).

Requires: Google Chrome (preferred) or Microsoft Edge for the headless print, pdftotext
on PATH, PyMuPDF (fitz). Keep --work short: paths over ~240 characters break Edge and
Python on Windows. Copy saved tool results into --work first if their path is long.
"""
import argparse, html, json, os, subprocess, sys, time

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


def load_message(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    return json.loads(raw[raw.find("{"):])


def to_html(msg):
    body = msg.get("htmlBody") or msg.get("html_body") or ""
    if not body:
        body = "<pre>" + html.escape(msg.get("plaintextBody") or msg.get("plaintext_body") or "") + "</pre>"
    if "<html" not in body.lower():
        body = "<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>" + body + "</body></html>"
    elif "charset" not in body.lower() and "<head>" in body:
        body = body.replace("<head>", "<head><meta charset='utf-8'>", 1)
    return body


def print_pdf(html_path, pdf_path):
    # Chrome prints synchronously. Edge 141 (2026-10) returns before the file lands, or
    # writes nothing at all without its own profile dir, so it is only the fallback.
    exe = CHROME if os.path.exists(CHROME) else EDGE
    url = "file:///" + html_path.replace("\\", "/")
    # A separate profile dir keeps the headless browser from handing off to a running
    # instance of the same browser (which exits 0 without writing the PDF).
    profile = os.path.join(os.path.dirname(os.path.abspath(html_path)), "_edge-profile")
    cmd = [exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={profile}",
           "--virtual-time-budget=8000", f"--print-to-pdf={pdf_path}", url]
    subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    for _ in range(40):  # Edge may still be writing after the launcher exits
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            return True
        time.sleep(0.25)
    return os.path.exists(pdf_path)


def trim_after(pdf_path, marker):
    import fitz
    d = fitz.open(pdf_path)
    last = next((i for i, p in enumerate(d) if marker in p.get_text()), None)
    if last is None or last == d.page_count - 1:
        d.close()
        return d.page_count if last is None else last + 1
    out = fitz.open()
    out.insert_pdf(d, from_page=0, to_page=last)
    d.close()
    tmp = pdf_path + ".tmp"
    out.save(tmp)
    out.close()
    os.replace(tmp, pdf_path)
    return last + 1


def pdf_text(pdf_path):
    r = subprocess.run(["pdftotext", pdf_path, "-"], capture_output=True, timeout=60)
    return r.stdout.decode("utf-8", "replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", required=True, help="short scratch folder for html files")
    ap.add_argument("--out", required=True, help="trip folder for the PDFs")
    ap.add_argument("--item", nargs=3, action="append", metavar=("MSG_JSON", "NAME", "EXPECT"), required=True)
    ap.add_argument("--trim-after", default=None, help="keep pages through the first page containing this text")
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    ok_all = True
    for src, name, expect in a.item:
        msg = load_message(src)
        html_path = os.path.join(a.work, name + ".html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(to_html(msg))
        pdf_path = os.path.join(a.out, name + ".pdf")
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        made = print_pdf(html_path, pdf_path)
        pages = trim_after(pdf_path, a.trim_after) if (made and a.trim_after) else None
        found = made and (expect in pdf_text(pdf_path))
        ok_all &= bool(found)
        print(f"{'PASS' if found else 'FAIL'}  {name}.pdf  subject={msg.get('subject')!r}  pages={pages}  expect={expect}")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
