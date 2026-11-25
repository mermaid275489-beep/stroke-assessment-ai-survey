"""Build docs/data/entries.json for the website's assessment explorer.

Source: v5/Supplementary Data 1.xlsx (sheets Mapping_entries and Feature_family_mapping).
Full scoring criteria and source citations are deliberately left out; see the spreadsheet for them.

Run from the repository root:  python docs/data/build_entries.py
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "v5" / "Supplementary Data 1.xlsx"
OUT = Path(__file__).resolve().parent / "entries.json"

FAMILY_SHORT = {
    "Temporal and event measures": "Temporal & event",
    "Spatial and trajectory measures": "Spatial & trajectory",
    "Joint and segment kinematics": "Joint & segment kinematics",
    "Inter-segment and relational measures": "Inter-segment & relational",
    "Trajectory-derived quality measures": "Trajectory-derived quality",
    "Trajectory-derived movement quality": "Trajectory-derived quality",
}


def clean(v):
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s.lower() in {"none", "none required", "-", "n/a"} else s


def main():
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)

    fam = defaultdict(set)
    for row in list(wb["Feature_family_mapping"].iter_rows(values_only=True))[1:]:
        family, ids = row[0], row[4]
        if not family or not ids:
            continue
        for eid in re.findall(r"E\d{3}", str(ids)):
            fam[eid].add(FAMILY_SHORT.get(family.strip(), family.strip()))

    rows = list(wb["Mapping_entries"].iter_rows(values_only=True))
    head = [str(h).strip() for h in rows[0]]
    col = {h: i for i, h in enumerate(head)}

    def get(r, name):
        return r[col[name]] if name in col else None

    entries = []
    for r in rows[1:]:
        eid = clean(get(r, "Entry ID"))
        if not eid:
            continue
        entries.append({
            "id": eid,
            "tool": clean(get(r, "Tool")),
            "unit": clean(get(r, "Mapping unit")),
            "item": clean(get(r, "Item")),
            "task": clean(get(r, "Item / task")),
            "info": clean(get(r, "Score-defining information type")),
            "avail": str(get(r, "Video availability") or "").strip(),
            "availWhy": clean(get(r, "Availability rationale")),
            "missing": clean(get(r, "Information not available from video")),
            "altSource": clean(get(r, "Supplementary source")),
            "recording": clean(get(r, "Recording requirements")),
            "features": clean(get(r, "Representative machine-observable features")),
            "comp": str(get(r, "Computability of visible criteria") or "").strip(),
            "compWhy": clean(get(r, "Computability rationale")),
            "families": sorted(fam.get(eid, [])),
        })

    OUT.write_text(json.dumps({"source": SRC.name, "entries": entries}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    print(len(entries), "entries;", len({e["tool"] for e in entries}), "tools")
    print("availability", Counter(e["avail"] for e in entries))
    print("computability (Full)", Counter(e["comp"] for e in entries if e["avail"] == "Full"))
    print("computability (Partial)", Counter(e["comp"] for e in entries if e["avail"] == "Partial"))
    print("families", Counter(f for e in entries for f in e["families"]))
    print("written", OUT, OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
