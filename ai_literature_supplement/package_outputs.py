from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(OUT / name, dtype=str, low_memory=False).fillna("")


def format_sheet(ws) -> None:
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(wrap_text=True, vertical="top")
    for column in ws.columns:
        values = [str(cell.value or "") for cell in list(column)[:200]]
        width = max([len(value) for value in values] + [10])
        ws.column_dimensions[column[0].column_letter].width = min(width + 2, 42)


def write_book(path: Path, sheets: dict[str, pd.DataFrame]) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        for name, frame in sheets.items():
            safe = frame.copy()
            for column in safe.columns:
                safe[column] = safe[column].map(
                    lambda value: value[:30000]
                    if isinstance(value, str) and len(value) > 30000
                    else value
                )
            safe.to_excel(writer, sheet_name=name[:31], index=False)
        workbook = writer.book
        for ws in workbook.worksheets:
            format_sheet(ws)


def build_status() -> pd.DataFrame:
    search_log = read_csv("search_log.csv")
    rows = []
    for _, row in search_log.iterrows():
        rows.append(
            {
                "database": row["database"],
                "source_stream": row["source_stream"],
                "status": row["status"],
                "reported_count": row["reported_count"],
                "retrieved_count": row["retrieved_count"],
                "complete_retrieval": row["complete_retrieval"],
                "note": "PubMed retrieval completed from the recorded query." if row["complete_retrieval"] == "True" else "PubMed retrieval was incomplete; do not use this stream as a locked count.",
            }
        )
    for stream in [
        "gait_mobility",
        "upper_limb_dexterity",
        "trunk_balance_compensation",
        "strength_power",
    ]:
        rows.append(
            {
                "database": "OpenAlex",
                "source_stream": stream,
                "status": "not completed",
                "reported_count": "",
                "retrieved_count": "0",
                "complete_retrieval": "False",
                "note": "Public cross-disciplinary attempt returned HTTP 429; no OpenAlex records were merged.",
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    search_log = read_csv("search_log.csv")
    known = read_csv("known_item_testing.csv")
    flow = read_csv("prisma_flow_counts.csv")
    decisions = read_csv("decision_counts.csv")
    status = build_status()

    master = read_csv("master_screening_library.csv")
    extraction = read_csv("component_evidence_extraction.csv")
    figure_source = read_csv("figure2_source_data.csv")

    search_log.to_csv(ROOT / "search_log_full.csv", index=False, encoding="utf-8-sig")
    search_log_workbook = search_log.copy()
    search_log_workbook["query_full_file"] = "search_log_full.csv"
    search_log_workbook["query"] = search_log_workbook["query"].astype(str).str.slice(0, 30000)

    status.to_csv(OUT / "public_source_status.csv", index=False, encoding="utf-8-sig")
    screening_status = OUT / "screening_status.md"
    screening_status.write_text(
        "# AI motion-analysis evidence library status\n\n"
        "The current library is a machine-assisted title/abstract screening pool. "
        "No Tier A study has been locked for Figure 2 until full-text review and adjudication are completed.\n\n"
        f"- Unique records after deduplication: {len(master):,}\n"
        f"- Tier A title/abstract candidates: {(master['automated_screening_decision'] == 'include_candidate_tier_a').sum():,}\n"
        f"- Tier B title/abstract candidates: {(master['automated_screening_decision'] == 'include_candidate_tier_b').sum():,}\n"
        f"- Uncertain records: {(master['automated_screening_decision'] == 'uncertain').sum():,}\n"
        "- OpenAlex: not merged because the public API returned HTTP 429 during the run.\n"
        "- Subscription exports from Embase, IEEE Xplore, Scopus/WoS and CINAHL: not yet supplied.\n",
        encoding="utf-8",
    )

    write_book(
        ROOT / "search_log.xlsx",
        {
            "search_log": search_log_workbook,
            "source_status": status,
            "known_item_testing": known,
            "flow_counts": flow,
            "decision_counts": decisions,
        },
    )
    write_book(ROOT / "master_screening_library.xlsx", {"screening_library": master})
    write_book(ROOT / "component_evidence_extraction.xlsx", {"extraction": extraction})
    write_book(ROOT / "figure2_source_data.xlsx", {"figure_source": figure_source})


if __name__ == "__main__":
    main()
