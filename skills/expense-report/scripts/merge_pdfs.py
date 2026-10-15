"""Merge PDFs in order into one file (Expensify holds one receipt per expense).

Usage:
  python merge_pdfs.py "<output.pdf>" "<first.pdf>" "<second.pdf>" ...
"""
import sys
import fitz


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    out_path, inputs = sys.argv[1], sys.argv[2:]
    out = fitz.open()
    for p in inputs:
        d = fitz.open(p)
        out.insert_pdf(d)
        d.close()
    out.save(out_path)
    print(f"wrote {out_path} ({out.page_count} pages)")


if __name__ == "__main__":
    main()
