"""Extract attachments from a Gmail message fetched with get_message messageFormat="RAW".

The Gmail connector has no attachment download tool, but RAW returns the whole MIME
message base64url-encoded in the "raw" field. The tool saves large results to a file;
pass that file here.

Usage:
  python gmail_raw_attachments.py <raw-result.txt> "<output folder>" [--rename "New name.pdf"] [--only pdf]

Prints each saved file with its size. --rename applies when exactly one attachment matches.
"""
import argparse, base64, email, json, os, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--rename", default=None)
    ap.add_argument("--only", default=None, help="extension filter, e.g. pdf")
    a = ap.parse_args()
    with open(a.src, encoding="utf-8") as f:
        raw = f.read()
    data = json.loads(raw[raw.find("{"):])
    b = data["raw"]
    b += "=" * (-len(b) % 4)
    msg = email.message_from_bytes(base64.urlsafe_b64decode(b))
    saved = []
    for part in msg.walk():
        fn = part.get_filename()
        if not fn:
            continue
        if a.only and not fn.lower().endswith("." + a.only.lower()):
            continue
        payload = part.get_payload(decode=True)
        if not payload:
            continue
        saved.append((fn, payload))
    if not saved:
        print("no attachments found")
        sys.exit(1)
    os.makedirs(a.out, exist_ok=True)
    for fn, payload in saved:
        name = a.rename if (a.rename and len(saved) == 1) else fn.replace("\n", " ").strip()
        dest = os.path.join(a.out, name)
        with open(dest, "wb") as f:
            f.write(payload)
        print(f"saved {dest} ({len(payload)} bytes)")


if __name__ == "__main__":
    main()
