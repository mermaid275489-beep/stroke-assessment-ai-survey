from pathlib import Path
import re
from collections import OrderedDict

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from openpyxl import load_workbook


ROOT = Path(r"D:\Stroke")
BRIDGE = ROOT / "Bridge_matrix_v5_final.xlsx"
OLD_DOCX = ROOT / "Section_3_2_All_Assessment_Tools_Supplementary_Word_Draft_Revised.docx"
OUTPUT = ROOT / "Table2_AI_Feature_Bridge_Working_Draft.docx"

COMPONENTS = OrderedDict(
    [
        ("ROM", "range of motion"),
        ("Strength", "muscle strength and power"),
        ("Coord", "coordination and selective motor control"),
        ("Balance", "balance and postural control"),
        ("Dexterity", "manual dexterity"),
        ("Gait", "gait and mobility"),
        ("Quality", "movement quality and compensation"),
    ]
)

FALLBACK_ABBR = {
    "10-Metre Walk Test": "10MWT",
    "2-Minute Walk Test": "2MWT",
    "6-Minute Walk Test": "6MWT",
    "Action Research Arm Test": "ARAT",
    "Berg Balance Scale": "BBS",
    "Box and Block Test": "BBT",
    "Brunel Balance Assessment": "BBA",
    "Chedoke Arm and Hand Activity Inventory": "CAHAI",
    "Community Balance & Mobility Scale": "CB&M",
    "Dynamic Gait Index": "DGI",
    "Elderly Mobility Scale": "EMS",
    "Five Times Sit-to-Stand": "5TSTS",
    "Frenchay Arm Test": "FAT",
    "Function In Sitting Test": "FIST",
    "Functional Gait Assessment": "FGA",
    "Functional Reach Test": "FRT",
    "Jebsen-Taylor Hand Function Test": "JTHFT",
    "Manual Function Test": "MFT",
    "Modified Emory Functional Ambulation Profile": "mEFAP",
    "Nine-Hole Peg Test": "9HPT",
    "Short Physical Performance Battery": "SPPB",
    "Simple Test for Evaluating Hand Function": "STEF",
    "Six-Spot Step Test": "SSST",
    "Stroke Upper Limb Capacity Scale": "SULCS",
    "Timed Up and Go": "TUG",
    "Tinetti / POMA": "POMA",
    "Tinetti/POMA": "POMA",
    "Trunk Control Test": "TCT",
    "Trunk Impairment Scale (TIS, Verheyden)": "TIS",
    "Wolf Motor Function Test": "WMFT",
    "Barthel Index": "BI",
    "Brunnstrom Recovery Stages": "BRS",
    "Chedoke-McMaster Stroke Assessment": "CMSA",
    "Composite Spasticity Index": "CSI",
    "Fugl-Meyer LE (FMA-LE)": "FMA-LE",
    "Fugl-Meyer UE (FMA-UE)": "FMA-UE",
    "Functional Ambulation Category": "FAC",
    "Functional Independence Measure": "FIM",
    "Japan Stroke Scale --- Motor (JSS-M)": "JSS-M",
    "Japan Stroke Scale --- severity (JSS)": "JSS",
    "Medical Research Council (MRC) muscle scale": "MRC",
    "Modified Ashworth Scale (MAS)": "MAS",
    "modified Rankin Scale (mRS)": "mRS",
    "Modified Tardieu Scale (MTS)": "MTS",
    "Motor Assessment Scale (MAS) (MAS-motor)": "MAS-motor",
    "Motricity Index": "MI",
    "NIH Stroke Scale (NIHSS)": "NIHSS",
    "Scale for Contraversive Pushing (SCP)": "SCP",
    "Shoulder Abduction Finger Extension (SAFE) score": "SAFE",
    "STREAM": "STREAM",
    "Stroke Impairment Assessment Set (SIAS)": "SIAS",
    "ABILHAND": "ABILHAND",
    "Activities-specific Balance Confidence (ABC)": "ABC",
    "Activity Measure for Post-Acute Care (AM-PAC)": "AM-PAC",
    "Falls Efficacy Scale (FES)": "FES",
    "Motor Activity Log (MAL)": "MAL",
    "Stroke Impact Scale (SIS)": "SIS",
    "Rivermead Mobility Index (RMI)": "RMI",
}


def norm(text):
    text = "" if text is None else str(text)
    text = text.replace("&", "and").replace("—", "-").replace("–", "-")
    text = re.sub(r"[^a-z0-9]+", "", text.lower())
    return text


def clean(text):
    text = "" if text is None else str(text)
    text = text.replace("●", "").replace("★", "")
    text = text.replace("鈼?", "").replace("鈽?", "")
    text = text.replace("→", "->").replace("←", "<-").replace("—", "-").replace("–", "-")
    text = text.replace("°", " deg ").replace("×", " x ").replace("≥", ">=").replace("≤", "<=")
    text = text.replace("·", "; ").replace("↔", "<->").replace("§", "sec. ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clamp(text, limit=220):
    text = clean(text)
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(";", 1)[0].rstrip(" ,")
    return cut + "; ..."


def set_run_font(run, size=8.0, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Times New Roman")
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def set_cell_shading(cell, fill=None):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill or "FFFFFF")


def set_cell_margins(cell, top=45, start=45, bottom=45, end=45):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, v in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def set_cell_border(cell, **kwargs):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        if edge not in kwargs:
            continue
        edge_data = kwargs.get(edge)
        tag = "w:{}".format(edge)
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        for key in ["val", "sz", "space", "color"]:
            if key in edge_data:
                element.set(qn("w:{}".format(key)), str(edge_data[key]))


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def prevent_row_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)


def set_table_layout_fixed(table):
    tbl_pr = table._tbl.tblPr
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")


def set_cell_width(cell, width_inches):
    cell.width = Inches(width_inches)
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(int(width_inches * 1440)))
    tc_w.set(qn("w:type"), "dxa")


def paragraph_text(cell, text, size=8.0, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 0.92
    lines = str(text or "").split("\n")
    for i, line in enumerate(lines):
        if i:
            p.add_run().add_break()
        run = p.add_run(line)
        set_run_font(run, size=size, bold=bold, italic=italic)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP


def read_abbr_and_components():
    abbr = {}
    coverage = {}
    doc = Document(OLD_DOCX)
    if doc.tables:
        for row in doc.tables[0].rows[1:]:
            vals = [clean(c.text) for c in row.cells]
            if len(vals) >= 3 and vals[1]:
                abbr[norm(vals[1])] = vals[2]
    if len(doc.tables) > 1:
        for row in doc.tables[1].rows[1:]:
            raw_vals = [c.text.strip() for c in row.cells]
            vals = [clean(v) for v in raw_vals]
            if len(vals) >= 10 and vals[1]:
                flags = raw_vals[3:10]
                coverage[norm(vals[1])] = [label for flag, label in zip(flags, COMPONENTS.values()) if flag]
    return abbr, coverage


def classify_components(row, tool_coverage):
    text = " ".join(
        clean(row.get(k, ""))
        for k in [
            "Item / task",
            "Task phase / movement component",
            "What clinician watches for",
            "Clinical meaning of abnormality",
            "Recommended AI video feature",
        ]
    ).lower()
    tags = []

    def add(label):
        if label not in tags:
            tags.append(label)

    if re.search(r"\b(range of motion|rom|joint angle|flexion|extension|dorsiflex|plantarflex|rotation|reach distance|head[- ]?turn|trunk rotation|active movement|passive motion)\b", text):
        add(COMPONENTS["ROM"])
    has_nonforce_construct = re.search(r"\b(passive|tone|spasticity|reflex|clonus|stretch resistance)\b", text)
    if not has_nonforce_construct and re.search(r"\b(strength|power|force|resistance|push[- ]?off|push up|sit[- ]?to[- ]?stand|stand[- ]?to[- ]?sit|rise|grip strength|manual muscle|weight[- ]?bearing)\b", text):
        add(COMPONENTS["Strength"])
    if re.search(r"\b(coordination|selective|synerg|ataxia|dysmetria|finger[- ]?to[- ]?nose|heel[- ]?to[- ]?shin|inter[- ]?joint|coupling|tremor|trajectory|smoothness|timing|rhythm|motor control|alternating)\b", text):
        add(COMPONENTS["Coord"])
    if re.search(r"\b(balance|postur|sway|stabil|standing|sitting|eyes[- ]?closed|pushing|fall|recovery response|loss of balance|weight shift|weight[- ]?bearing|anticipatory|reactive)\b", text):
        add(COMPONENTS["Balance"])
    if re.search(r"\b(grasp|pinch|peg|block|finger[- ]?to[- ]?nose|object manipulation|manual dexterity|fine hand|hand function|finger extension|grip strength|hand use in task)\b", text):
        add(COMPONENTS["Dexterity"])
    gait_text = re.sub(r"\b(block[- ]transfer|object transfer|hand transfer)\b", "", text)
    if re.search(r"\b(gait|walk|walking|ambulation|step|stair|locomotion|mobility|transfer|bed mobility|turn|pivot|obstacle|sit[- ]?to[- ]?stand|stand[- ]?to[- ]?sit)\b", gait_text):
        add(COMPONENTS["Gait"])
    if re.search(r"\b(quality|compens|asymmetr|symmetr|alignment|strategy|deviation|abnormal|smooth|synerg|trajectory|support/assistance cues|movement pattern|movement quality)\b", text):
        add(COMPONENTS["Quality"])

    # Use the pre-existing scale-level coverage only when the item wording is too sparse.
    if not tags:
        tags = list(tool_coverage)
    return tags or [COMPONENTS["Quality"]]


def mapping_status(row):
    value = clean(row.get("AI can directly judge? (AI能否直接判定)", "")).lower()
    if "直接" in value or "direct" in value:
        return "Direct"
    if "代理" in value or "proxy" in value or "间接" in value:
        return "Proxy"
    return "Not derivable"


def evidence_status(row, status):
    anchor = clean(row.get("Literature anchor (v3)", "")).lower()
    grade = clean(row.get("Evidence grade (v3)", "")).lower()
    if any(x in anchor for x in ["video", "alphapose", "ai", "machine learning", "sms stroke"]):
        return "Candidate AI support - unverified"
    if any(x in anchor for x in ["winter", "rancho", "camera baseline", "verheyden", "reference"]):
        return "Conventional motion-analysis support"
    if "c3" in grade or "gap" in grade:
        return "Evidence gap"
    if status == "Not derivable":
        return "Evidence gap"
    return "AI evidence pending"


def source_text(row):
    pdf = clean(row.get("Source PDF", ""))
    locator = clean(row.get("Source page/section/item locator", ""))
    anchor = clean(row.get("Literature anchor (v3)", ""))
    if pdf:
        pdf = re.sub(r"\.pdf$", "", pdf, flags=re.I)
        pdf = pdf.replace("_", " ")
        pdf = clamp(pdf, 70)
    first = "Scale: " + pdf if pdf else "Scale source: recorded"
    if locator:
        first += "; " + clamp(locator, 52)
    second = "Bridge: " + clamp(anchor, 105) if anchor else "Bridge: " + clean(row.get("Mapping evidence basis (映射证据基础)", ""))
    return first + "\n" + second


def feature_text(row, status):
    feature = clean(row.get("Recommended AI video feature", ""))
    task = clean(row.get("Task phase / movement component", ""))
    info = clean(row.get("Score-defining information type (评分依赖信息类型)", ""))
    if status == "Not derivable" or "not video-observable" in feature.lower() or "no valid" in feature.lower():
        return "Modality: non-video or multimodal; task: " + clamp(task, 55) + "; no valid ordinary-video feature for the official score"
    if not feature:
        feature = "task detection and criterion-relevant movement features"
    modality = "video/pose (provisional)"
    if "force" in info.lower() or "tactile" in info.lower():
        modality = "video proxy; force/tactile input required for exact score"
    return "Modality: " + modality + "; task: " + clamp(task, 52) + "; features: " + clamp(feature, 145)


def configure_document(doc):
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Inches(11)
    section.page_height = Inches(8.5)
    section.top_margin = Inches(0.35)
    section.bottom_margin = Inches(0.35)
    section.left_margin = Inches(0.25)
    section.right_margin = Inches(0.25)
    section.header_distance = Inches(0.15)
    section.footer_distance = Inches(0.15)


def main():
    abbr_map, coverage_map = read_abbr_and_components()
    wb = load_workbook(BRIDGE, read_only=True, data_only=True)
    ws = wb["Bridge_matrix_v5"]
    headers = [clean(c.value) for c in ws[1]]
    rows = [dict(zip(headers, [c for c in row])) for row in ws.iter_rows(min_row=2, values_only=True)]
    assert len(rows) == 193, f"Expected 193 bridge rows, got {len(rows)}"

    doc = Document()
    configure_document(doc)
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    normal.font.size = Pt(8)

    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
    cap.paragraph_format.space_after = Pt(2)
    cap_run = cap.add_run("Table 2. Item-level clinical-to-AI feature mapping for post-stroke assessment tools.")
    set_run_font(cap_run, size=9, bold=True)

    status_note = doc.add_paragraph()
    status_note.paragraph_format.space_after = Pt(4)
    status_note.paragraph_format.line_spacing = 0.95
    note_run = status_note.add_run(
        "Working version. The AI-feature evidence layer is provisional: the current component-specific literature library remains at title/abstract screening, and full-text inclusion and adjudication are pending."
    )
    set_run_font(note_run, size=8, italic=True)

    headers_out = [
        "ID",
        "Scale item/task",
        "Clinical component(s)",
        "Score-defining information",
        "Candidate AI feature",
        "Mapping status",
        "AI-feature evidence",
        "Supporting source",
    ]
    widths = [0.30, 1.45, 1.25, 1.55, 2.20, 0.70, 1.25, 1.80]
    table = doc.add_table(rows=1, cols=len(headers_out))
    table.autofit = False
    table.allow_autofit = False
    set_table_layout_fixed(table)
    header = table.rows[0]
    set_repeat_table_header(header)
    for i, (cell, text) in enumerate(zip(header.cells, headers_out)):
        set_cell_width(cell, widths[i])
        set_cell_margins(cell, top=55, start=45, bottom=55, end=45)
        set_cell_shading(cell, "F2F2F2")
        paragraph_text(cell, text, size=8, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        set_cell_border(cell, top={"val": "single", "sz": 8, "color": "000000"}, bottom={"val": "single", "sz": 6, "color": "000000"}, left={"val": "nil"}, right={"val": "nil"})

    for idx, row in enumerate(rows, start=1):
        tool = clean(row.get("Tool", ""))
        abbr = abbr_map.get(norm(tool), FALLBACK_ABBR.get(tool, tool))
        item = clean(row.get("Item / task", ""))
        tool_key = norm(tool)
        base_coverage = coverage_map.get(tool_key, [])
        components = classify_components(row, base_coverage)
        status = mapping_status(row)
        evidence = evidence_status(row, status)
        values = [
            str(idx),
            abbr + " - " + clamp(item, 115),
            "\n".join(components),
            clamp(row.get("Score-defining information type (评分依赖信息类型)", ""), 145),
            feature_text(row, status),
            status,
            evidence,
            source_text(row),
        ]
        new_row = table.add_row()
        prevent_row_split(new_row)
        for i, (cell, value) in enumerate(zip(new_row.cells, values)):
            set_cell_width(cell, widths[i])
            set_cell_margins(cell, top=35, start=40, bottom=35, end=40)
            paragraph_text(cell, value, size=7.7, align=WD_ALIGN_PARAGRAPH.CENTER if i in [0, 5] else WD_ALIGN_PARAGRAPH.LEFT)
            borders = {"top": {"val": "nil"}, "bottom": {"val": "nil"}, "left": {"val": "nil"}, "right": {"val": "nil"}}
            if idx == len(rows):
                borders["bottom"] = {"val": "single", "sz": 8, "color": "000000"}
            set_cell_border(cell, **borders)

    notes = doc.add_paragraph()
    notes.paragraph_format.space_before = Pt(4)
    notes.paragraph_format.space_after = Pt(0)
    notes.paragraph_format.line_spacing = 0.95
    text = (
        "Notes. Clinical components are item-level analytical labels derived from the existing seven-component scheme; multiple labels may apply. "
        "Direct indicates that the official score-defining information is video-computable under the specified setup; Proxy indicates that video can provide a clinically meaningful movement proxy but not the complete official score; Not derivable indicates an in-principle non-video requirement. "
        "AI-feature evidence is provisional in this working version and is separated from the clinical-source evidence grade. AI-L0-L4 levels will be assigned only after full-text screening and adjudication."
    )
    run = notes.add_run(text)
    set_run_font(run, size=8, italic=False)

    doc.save(OUTPUT)
    print(f"saved {OUTPUT}")
    print(f"rows={len(rows)} tools={len({clean(r.get('Tool','')) for r in rows})}")


if __name__ == "__main__":
    main()
