"""Extract attachments from a Gmail message (get_message messageFormat="RAW" JSON or .eml file).

The Gmail connector has no attachment download tool, but RAW returns the whole MIME
message base64url-encoded in the "raw" field. You can also pass a raw RFC 822 .eml file
downloaded from Gmail's "Show original" view in the browser.

Usage:
  python gmail_raw_attachments.py <raw-result.txt-or-msg.eml> "<output folder>" [--rename "New name.pdf"] [--only pdf]

Prints each saved file with its size. --rename applies when exactly one attachment matches.
"""
import argparse, base64, email, json, os, sys


def load_mime_message(path):
    with open(path, "rb") as f:
        raw_bytes = f.read()
    raw_text = raw_bytes.decode("utf-8", "replace")
    brace = raw_text.find("{")
    if not path.lower().endswith(".eml") and brace != -1:
        try:
            data = json.loads(raw_text[brace:])
            if isinstance(data, dict) and "raw" in data:
                b = data["raw"]
                b += "=" * (-len(b) % 4)
                return email.message_from_bytes(base64.urlsafe_b64decode(b))
        except json.JSONDecodeError:
            pass
    return email.message_from_bytes(raw_bytes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--rename", default=None)
    ap.add_argument("--only", default=None, help="extension filter, e.g. pdf")
    a = ap.parse_args()
    msg = load_mime_message(a.src)
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
