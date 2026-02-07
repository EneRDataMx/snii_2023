"""Inspect column names of every raw Excel file, sorted by year."""

import pathlib
import re
import pandas as pd

RAW_DIR = pathlib.Path(__file__).resolve().parent.parent / "data" / "001_raw"

rows = []
for f in RAW_DIR.glob("*.xlsx"):
    match = re.search(r"(\d{4})\.xlsx$", f.name)
    if not match:
        continue
    year = int(match.group(1))
    cols = list(pd.read_excel(f, nrows=0).columns)
    rows.append((year, f.name, cols))

rows.sort(key=lambda r: r[0])

for year, fname, cols in rows:
    print(f"\n{'='*72}")
    print(f"Year : {year}")
    print(f"File : {fname}")
    print(f"Cols ({len(cols)}): {cols}")
