"""Scan a folder for things that should never be in a public repo.

Usage:
  python tools/pii_scan.py [folder] [--terms private-terms.txt] [--allow allowlist.txt]

Built-in patterns: email addresses, long digit runs (card, account and report IDs),
"ending 1234"-style card fragments, US phone numbers, street addresses, and
C:\\Users\\<name> paths. --terms adds your own case-insensitive words (names, employer,
cities); keep that file outside the repo. --allow lists exact lines to ignore.
Exit code 1 when anything is found.
"""
import argparse, os, re, sys

PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "long-number": re.compile(r"(?<![\w/.-])\d{12,19}(?![\w/.-])"),
    "card-fragment": re.compile(r"\b(ending|x|xx|\*{2,}|•{2,})\s?\d{4}\b", re.I),
    "phone": re.compile(r"\(?\b\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b"),
    "street": re.compile(r"\b\d{1,5} [A-Z][A-Za-z]+( [A-Z][A-Za-z]+)? (St|Ave|Rd|Blvd|Dr|Pl|Ln|Way|Trl|Sq|Ct)\b"),
    "user-path": re.compile(r"[A-Za-z]:[\\/]Users[\\/](?!<you>|you\b|<name>)[\w.-]+", re.I),
}
SKIP_DIRS = {".git", "__pycache__", "node_modules"}
TEXT_EXT = {".md", ".py", ".yaml", ".yml", ".json", ".txt", ".toml", ".cfg", ".ini", ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder", nargs="?", default=".")
    ap.add_argument("--terms", default=None)
    ap.add_argument("--allow", default=None)
    a = ap.parse_args()
    terms = []
    if a.terms:
        with open(a.terms, encoding="utf-8") as f:
            terms = [t.strip() for t in f if t.strip() and not t.startswith("#")]
    allow = set()
    if a.allow:
        with open(a.allow, encoding="utf-8") as f:
            allow = {l.rstrip("\n") for l in f if l.strip()}
    term_re = re.compile("|".join(r"\b" + re.escape(t) + r"\b" for t in terms), re.I) if terms else None
    hits = 0
    for root, dirs, files in os.walk(a.folder):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fn in files:
            if os.path.splitext(fn)[1].lower() not in TEXT_EXT:
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, encoding="utf-8") as f:
                    lines = f.read().splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            for n, line in enumerate(lines, 1):
                if line.strip() in allow:
                    continue
                for name, rx in PATTERNS.items():
                    for m in rx.finditer(line):
                        print(f"{path}:{n}: [{name}] {m.group(0)}")
                        hits += 1
                if term_re:
                    for m in term_re.finditer(line):
                        print(f"{path}:{n}: [term] {m.group(0)}  |  {line.strip()[:120]}")
                        hits += 1
    print(f"{hits} finding(s)")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
