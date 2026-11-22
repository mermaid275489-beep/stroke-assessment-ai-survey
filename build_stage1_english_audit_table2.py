from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


ROOT = Path(r"D:\Stroke")
OUTDIR = ROOT / "stage1_outputs"
GUIDELINE_BOOK = ROOT / "Guideline Summary.xlsx"
BRIDGE_BOOK = ROOT / "Bridge_matrix_v5_final.xlsx"
AUDIT_OUTPUT = OUTDIR / "Stage1_English_Source_Audit_and_Cleaned_Data.xlsx"
WORD_OUTPUT = OUTDIR / "Table2_Computational_Feature_Framework_Draft.docx"

REMOVED_TOOLS = {
    "Japan Stroke Scale - Motor (JSS-M)",
    "Japan Stroke Scale - severity (JSS)",
    "Simple Test for Evaluating Hand Function (STEF)",
}

REMOVED_GUIDELINE_PREFIXES = (
    "JSS Stroke Treatment Guideline",
    "Clinical Mgmt Guideline 2nd ed - Ch8 Rehabilitation",
    "Acute Ischaemic Stroke Dx/Tx 2023",
    "Clinical Mgmt Guideline 2nd ed - Ch5 ICH / Ch6 SAH",
    "Cerebrovascular Prevention Guideline 2024",
)

FAMILY_ORDER = [
    "Temporal and event measures",
    "Spatial and trajectory measures",
    "Joint and segment kinematics",
    "Inter-segment and relational measures",
    "Trajectory-derived movement quality",
]

FAMILY_RULES = {
    "Temporal and event measures": [
        r"\btime\b", r"duration", r"cadence", r"frequency", r"\bcount", r"attempt",
        r"completion", r"complete", r"phase", r"segment", r"timing", r"\bspeed\b",
        r"velocity", r"\brate\b", r"hold", r"second", r"minute", r"repetition",
        r"cycle", r"transition", r"event", r"start", r"stop", r"rest", r"seat-off",
    ],
    "Spatial and trajectory measures": [
        r"trajectory", r"\bpath\b", r"distance", r"displacement", r"position", r"endpoint",
        r"target", r"clearance", r"deviation", r"step length", r"stride length", r"reach",
        r"excursion", r"proximity", r"transport", r"inter-ankle", r"height", r"location",
    ],
    "Joint and segment kinematics": [
        r"joint", r"angle", r"\brom\b", r"flexion", r"extension", r"rotation", r"abduction",
        r"adduction", r"keypoint", r"kinematic", r"wrist", r"finger", r"ankle", r"knee",
        r"\bhip\b", r"shoulder", r"elbow", r"trunk", r"pelvis", r"body tilt", r"posture",
    ],
    "Inter-segment and relational measures": [
        r"symmetr", r"bilateral", r"left/right", r"\bl/r\b", r"coupling", r"relative phase",
        r"alignment", r"synergy", r"inter-limb", r"weight shift", r"support pattern",
        r"affected side", r"hemipleg", r"nonparetic", r"paretic", r"trunk strategy",
    ],
    "Trajectory-derived movement quality": [
        r"smooth", r"\bjerk\b", r"quality", r"variability", r"efficiency", r"compensation",
        r"dysmetria", r"tremor", r"sway", r"instability", r"balance loss", r"control",
        r"continuity", r"abnormal", r"coordination", r"strategy", r"failure", r"\bmiss\b",
        r"\bdrop\b", r"slip", r"erratic", r"recovery", r"accuracy",
    ],
}

NON_KINEMATIC_TERMS = (
    "assistance/supervision",
    "risk-judgment",
    "applied force/tactile",
    "tone/reflex",
    "self-report",
    "multi-domain neurological examination",
)

TABLE_ROWS = {
    "Temporal and event measures": {
        "definition": "Observable events and time-indexed task structure, including initiation, completion, phase transitions, duration, repetition and cadence.",
        "context": "Sit-to-stand; 10-m walk; turning; object transfer; moving the hand from the shoulder to the knee.",
        "variables": "Event timestamps; duration; completion and attempt counts; cadence; phase time; linear speed.",
        "input": "Video with a known frame rate; audio or prolonged capture for selected tasks.",
    },
    "Spatial and trajectory measures": {
        "definition": "Positions and paths of body keypoints or objects in image coordinates or calibrated physical space.",
        "context": "Shoulder-to-knee hand transfer; forward reach; foot trajectory and toe clearance during gait.",
        "variables": "Wrist or foot trajectory; displacement; path length; endpoint error; reach distance; toe clearance.",
        "input": "Video; spatial calibration or multiview/3D capture when metric distances are required.",
    },
    "Joint and segment kinematics": {
        "definition": "Geometric motion of joints and body segments derived from tracked landmarks.",
        "context": "Elbow flexion; arm elevation; knee range of motion; trunk lean during sitting or standing.",
        "variables": "Joint angle; range of motion; angular velocity and acceleration; segment orientation.",
        "input": "Full-body or region-focused video with an appropriate view; calibration when required.",
    },
    "Inter-segment and relational measures": {
        "definition": "Relations between body segments, bilateral time series or successive movement phases.",
        "context": "Bilateral gait symmetry; shoulder-elbow coupling; trunk compensation during reaching.",
        "variables": "Symmetry index; relative phase; joint coupling; segment alignment; temporal coordination.",
        "input": "Simultaneous visibility of relevant segments and both sides; synchronized views when needed.",
    },
    "Trajectory-derived movement quality": {
        "definition": "Higher-order descriptors calculated from trajectories and their temporal derivatives.",
        "context": "Reaching smoothness; movement fragmentation; path efficiency; compensatory trunk motion.",
        "variables": "Normalized jerk; velocity-peak count; path-length ratio; variability; compensation amplitude.",
        "input": "Stable landmark tracking with adequate frame rate; calibrated or 3D capture for selected metrics.",
    },
}


GUIDELINE_AUDIT = [
    {
        "Audit ID": "G01",
        "Region": "Korea",
        "Original record": "CPG Stroke Rehabilitation Part 1 (Motor) 2022",
        "Issuing body": "Korean Society for NeuroRehabilitation",
        "Original/source-language status": "Record was labelled Korean in the working file.",
        "English candidate": "Clinical Practice Guideline for Stroke Rehabilitation in Korea-Part 1: Rehabilitation for Motor Function (2022)",
        "Relationship and currency": "Official English full-text publication of the same guideline; published 2023.",
        "Decision": "RETAIN - replace citation with English full text",
        "Reason": "Full English body, recommendations and methods are available from the issuing society journal.",
        "DOI / official URL": "10.12786/bn.2023.16.e18 | https://www.e-bnr.org/search.php?code=0176BN&id=10.12786%2Fbn.2023.16.e18&vmode=FULL&where=aview",
    },
    {
        "Audit ID": "G02",
        "Region": "Korea",
        "Original record": "CPG Stroke Rehabilitation Part 2 2024/25",
        "Issuing body": "Korean Society for NeuroRehabilitation",
        "Original/source-language status": "Record was labelled as a partial summary in the working file.",
        "English candidate": "Clinical Practice Guideline for Stroke Rehabilitation in Korea-Part 2: Rehabilitation for Motor and Sensory Function (2024)",
        "Relationship and currency": "Official English full-text publication of the same guideline; published 2025.",
        "Decision": "RETAIN - replace citation with English full text",
        "Reason": "Full English body and recommendation table are available; Korean recommendations are supplementary material.",
        "DOI / official URL": "10.12786/bn.2025.18.e7 | https://www.e-bnr.org/pdf/10.12786/bn.2025.18.e7",
    },
    {
        "Audit ID": "G03",
        "Region": "Japan",
        "Original record": "JSS Stroke Treatment Guideline 2021 (revised 2025)",
        "Issuing body": "Japan Stroke Society",
        "Original/source-language status": "Japanese full text; English title only.",
        "English candidate": "No current official English full-text edition located.",
        "Relationship and currency": "The official 2025 revision remains Japanese.",
        "Decision": "REMOVE",
        "Reason": "Fails the English-full-text eligibility rule.",
        "DOI / official URL": "https://www.jsts.gr.jp/img/guideline2021_kaitei2025_kaiteikoumoku.pdf",
    },
    {
        "Audit ID": "G04",
        "Region": "China (mainland)",
        "Original record": "Clinical Management Guideline, 2nd ed., Chapter 8 Rehabilitation (2023)",
        "Issuing body": "Chinese Stroke Association",
        "Original/source-language status": "Chinese body with bilingual title and English abstract.",
        "English candidate": "English 2019 stroke-rehabilitation update (older edition).",
        "Relationship and currency": "Same issuing body and scope, but superseded by the Chinese 2023 second edition.",
        "Decision": "REMOVE",
        "Reason": "No current English full-text equivalent; an English abstract and a superseded edition are insufficient.",
        "DOI / official URL": "10.3969/j.issn.1673-5765.2023.09.010 | older English DOI 10.1136/svn-2019-000321",
    },
    {
        "Audit ID": "G05",
        "Region": "China (mainland)",
        "Original record": "Chinese Guideline for Diagnosis and Treatment of Acute Ischemic Stroke 2023",
        "Issuing body": "Chinese Society of Neurology / Chinese Stroke Society",
        "Original/source-language status": "Chinese body with English title and abstract.",
        "English candidate": "No official same-edition English full text located.",
        "Relationship and currency": "The CSA 2023 English ischaemic guideline is issued by a different guideline committee and is screened separately.",
        "Decision": "REMOVE",
        "Reason": "Fails the English-full-text rule; a different issuer's guideline is not treated as its translation.",
        "DOI / official URL": "10.3760/cma.j.cn113694-20240410-00221 | https://rs.yiigle.com/CN115399202004/1504708.htm",
    },
    {
        "Audit ID": "G06",
        "Region": "China (mainland)",
        "Original record": "Clinical Management Guideline, 2nd ed., Chapters 5 ICH and 6 SAH (2023)",
        "Issuing body": "Chinese Stroke Association",
        "Original/source-language status": "Chinese full-text chapters.",
        "English candidate": "English 2019 ICH and SAH updates.",
        "Relationship and currency": "Same issuing body and broad scope, but both English versions predate the 2023 second edition.",
        "Decision": "REMOVE",
        "Reason": "No current English full-text equivalent; superseded English editions are not substituted.",
        "DOI / official URL": "Older English DOIs: 10.1136/svn-2020-000433 (ICH); 10.1136/svn-2019-000296 (SAH)",
    },
    {
        "Audit ID": "G07",
        "Region": "China (mainland)",
        "Original record": "Cerebrovascular Disease Prevention Guideline 2024",
        "Issuing body": "National Health Commission of China",
        "Original/source-language status": "Chinese official full text.",
        "English candidate": "No official English full-text edition located.",
        "Relationship and currency": "No current same-issuer English equivalent identified.",
        "Decision": "REMOVE",
        "Reason": "Fails the English-full-text eligibility rule.",
        "DOI / official URL": "https://drugs.dxy.cn/pc/clinicalGuidelines/ygmk_lwtlFy1dNlNB8GdRqA",
    },
    {
        "Audit ID": "G08",
        "Region": "China (mainland)",
        "Original record": "New English candidate screened independently",
        "Issuing body": "Chinese Stroke Association Stroke Guidelines Writing Committee",
        "Original/source-language status": "English full text.",
        "English candidate": "Chinese Stroke Association guidelines for clinical management of ischaemic cerebrovascular diseases: executive summary and 2023 update",
        "Relationship and currency": "Current 2023 English update; not presented as a translation of the CMA 2023 guideline.",
        "Decision": "ADD - independent eligible English guideline",
        "Reason": "Current official English full text from the CSA guideline committee; relevant scales already occur in the retained library.",
        "DOI / official URL": "10.1136/svn-2023-002998 | https://svn.bmj.com/content/8/6/e3",
    },
]


SCALE_AUDIT = [
    {
        "Tool": "Japan Stroke Scale - Motor (JSS-M)",
        "Original provenance": "Japan Stroke Society guideline and Japanese official scale page",
        "English instrument/manual evidence": "English article titles and abstracts exist, but the official administration and weighted scoring materials are Japanese.",
        "Decision": "REMOVE",
        "Effect on bridge matrix": "Remove 1 tool-level row.",
        "Evidence URL": "https://www.jsts.gr.jp/storokescale/jss-m.html",
    },
    {
        "Tool": "Japan Stroke Scale - severity (JSS)",
        "Original provenance": "Japan Stroke Society guideline and Japanese official scale page",
        "English instrument/manual evidence": "The official item definitions, administration instructions and scoring form are Japanese.",
        "Decision": "REMOVE",
        "Effect on bridge matrix": "Remove 1 tool-level row.",
        "Evidence URL": "https://www.jsts.gr.jp/storokescale/jss.html",
    },
    {
        "Tool": "Modified Tardieu Scale (MTS)",
        "Original provenance": "Chinese 2023 rehabilitation guideline",
        "English instrument/manual evidence": "A formal English instrument specification provides velocity definitions, reaction-quality grades, R1/R2 scoring, equipment and administration details; StrokEDGE recommends use across stroke settings.",
        "Decision": "RETAIN - reclassify as supplementary English measurement source",
        "Effect on bridge matrix": "Retain 1 tool-level row; remove Chinese guideline provenance.",
        "Evidence URL": "https://www.sralab.org/rehabilitation-measures/tardieu-scalemodified-tardieu-scale | https://www.ncbi.nlm.nih.gov/books/NBK585580/table/ch9.Tab4/",
    },
    {
        "Tool": "Stroke Upper Limb Capacity Scale (SULCS)",
        "Original provenance": "Dutch score form in the supplementary working set",
        "English instrument/manual evidence": "The developer institution provides an official five-page English score form with all 10 tasks, administration instructions, equipment and scoring rules.",
        "Decision": "RETAIN - replace Dutch source with official English form",
        "Effect on bridge matrix": "Retain 1 tool-level row and update provenance in the cleaned copy.",
        "Evidence URL": "https://www.maartenskliniek.nl/media/0jjbhjrq/scorelijst-en.pdf",
    },
    {
        "Tool": "Frenchay Arm Test (FAT)",
        "Original provenance": "Dutch protocol in the supplementary working set",
        "English instrument/manual evidence": "The original English primary publication defines the five pass/fail tasks and scoring; complete English task specifications are available in English stroke-rehabilitation publications.",
        "Decision": "RETAIN - replace Dutch source with English primary source",
        "Effect on bridge matrix": "Retain 1 tool-level row and update provenance in the cleaned copy.",
        "Evidence URL": "10.1136/jnnp.50.6.714 | https://jnnp.bmj.com/content/50/6/714",
    },
    {
        "Tool": "Manual Function Test (MFT)",
        "Original provenance": "National Rehabilitation Center for the Disabled, Japan",
        "English instrument/manual evidence": "The issuing center provides a 49-page English WHO-collaborating-centre manual with task specifications, grading and score forms.",
        "Decision": "RETAIN - confirmed complete official English manual",
        "Effect on bridge matrix": "Retain 8 item rows and normalize the English source citation.",
        "Evidence URL": "https://www.rehab.go.jp/english/pdf/E08.pdf",
    },
    {
        "Tool": "Brunnstrom Recovery Stages",
        "Original provenance": "English-origin recovery framework; primary book was cited but not locally supplied",
        "English instrument/manual evidence": "The primary source is the English monograph Movement Therapy in Hemiplegia (1970); full six-stage definitions are also reported in peer-reviewed English literature.",
        "Decision": "RETAIN - formal English primary source identified",
        "Effect on bridge matrix": "Retain 1 tool-level row; flag the monograph for library retrieval before submission.",
        "Evidence URL": "Brunnstrom S. Movement Therapy in Hemiplegia. Harper & Row; 1970. | https://pmc.ncbi.nlm.nih.gov/articles/PMC4979857/",
    },
    {
        "Tool": "Simple Test for Evaluating Hand Function (STEF)",
        "Original provenance": "Unspecified supplementary source; Japanese-origin commercial test",
        "English instrument/manual evidence": "An English manufacturer page and English validation articles describe the tasks, but no complete official English checklist and age-referenced time-to-score conversion table was located.",
        "Decision": "REMOVE",
        "Effect on bridge matrix": "Remove 1 task-level row.",
        "Evidence URL": "https://www.sakaimed.co.jp/english/stef.html | 10.1016/j.jht.2017.09.007",
    },
]


def normalize_ascii(value: object) -> str:
    text = str(value or "")
    return text.replace("\u2014", "-").replace("\u2013", "-").strip()


def status_from_row(row: dict[str, object], status_field: str) -> str:
    value = str(row.get(status_field) or "")
    if "\u53ef\u76f4\u63a5" in value:
        return "Quantifiable"
    if "\u4ee3\u7406" in value:
        return "Proxy only"
    if "\u65e0\u6cd5" in value:
        return "Unresolved"
    raise ValueError(f"Unrecognized mapping status: {value!r}")


def classify_item(row: dict[str, object], fields: dict[str, str]) -> tuple[dict[str, list[str]], bool]:
    combined = " | ".join(
        normalize_ascii(row.get(fields[key])).lower()
        for key in ("item", "watches", "phase", "score_info", "feature", "instruction")
    )
    matches: dict[str, list[str]] = {}
    for family, patterns in FAMILY_RULES.items():
        found = [pattern for pattern in patterns if re.search(pattern, combined)]
        if found:
            matches[family] = found

    score_info = normalize_ascii(row.get(fields["score_info"])).lower()
    status = status_from_row(row, fields["status"])
    boundary = any(term in score_info for term in NON_KINEMATIC_TERMS)

    if status != "Unresolved" and not matches:
        if "time/distance/count" in score_info:
            matches["Temporal and event measures"] = ["fallback: time/distance/count"]
            matches["Spatial and trajectory measures"] = ["fallback: time/distance/count"]
        elif "kinematic/movement-quality" in score_info:
            matches["Joint and segment kinematics"] = ["fallback: kinematic/movement-quality"]
        elif "assistance/supervision" in score_info or "risk-judgment" in score_info:
            matches["Temporal and event measures"] = ["fallback: visible task/helper event"]
            matches["Trajectory-derived movement quality"] = ["fallback: behavioral proxy"]
        elif "applied force/tactile" in score_info or "tone/reflex" in score_info:
            matches["Joint and segment kinematics"] = ["fallback: visible kinematic proxy"]
        elif "self-report" in score_info:
            matches["Trajectory-derived movement quality"] = ["fallback: behavioral proxy"]

    if status == "Unresolved":
        matches = {}
        boundary = True
    return matches, boundary


def header_lookup(headers: list[object]) -> dict[str, str]:
    string_headers = [str(h) for h in headers]

    def by_prefix(prefix: str) -> str:
        return next(h for h in string_headers if h.startswith(prefix))

    return {
        "tool": by_prefix("Tool"),
        "item_no": by_prefix("Item #"),
        "item": by_prefix("Item / task"),
        "watches": by_prefix("What clinician watches for"),
        "phase": by_prefix("Task phase / movement component"),
        "score_info": by_prefix("Score-defining information type"),
        "status": by_prefix("AI can directly judge?"),
        "feature": by_prefix("Recommended AI video feature"),
        "instruction": by_prefix("Feature-extraction instruction"),
        "source": by_prefix("Source PDF"),
        "source_locator": by_prefix("Source page/section/item locator"),
        "source_completeness": by_prefix("Source completeness"),
        "verification": by_prefix("Verification status"),
    }


def load_clean_bridge() -> tuple[list[str], list[dict[str, object]], dict[str, str]]:
    workbook = openpyxl.load_workbook(BRIDGE_BOOK, data_only=True)
    sheet = workbook["Bridge_matrix_v5"]
    values = list(sheet.values)
    headers = [str(value) for value in values[0]]
    fields = header_lookup(headers)
    rows = [dict(zip(headers, row)) for row in values[1:]]
    clean = [dict(row) for row in rows if normalize_ascii(row[fields["tool"]]) not in REMOVED_TOOLS]
    source_replacements = {
        "Modified Tardieu Scale": (
            "English MTS instrument specification (RehabMeasures Database)",
            "Velocity definitions; reaction-quality grades; R1/R2 scoring",
            "Complete English administration and scoring specification",
            "English source replacement verified",
        ),
        "Stroke Upper Limb Capacity Scale (SULCS)": (
            "Official SULCS English score form - Sint Maartenskliniek",
            "English form pp. 1-5; 10 tasks and start/stop rules",
            "Complete official English form and instructions",
            "Dutch source replaced with official English score form",
        ),
        "Frenchay Arm Test (FAT)": (
            "Heller et al. 1987 English primary publication; DOI 10.1136/jnnp.50.6.714",
            "Five pass/fail tasks; total score 0-5",
            "Complete English task and scoring specification",
            "Dutch source replaced with English primary source",
        ),
        "Manual Function Test (MFT)": (
            "English Rehabilitation Manual 8 (National Rehabilitation Center for the Disabled, Japan; WHO collaborating centre)",
            "Manual sections 1[2]-1[4], pp. 2-9",
            "Complete official English manual, task criteria and score form",
            "Official English manual verified",
        ),
        "Brunnstrom Recovery Stages": (
            "Brunnstrom S. Movement Therapy in Hemiplegia. Harper & Row; 1970 (English primary monograph)",
            "Six recovery stages for arm, hand and leg",
            "Formal English primary source identified; obtain library copy before submission",
            "English primary source identified; retrieval flag retained",
        ),
    }
    for row in clean:
        tool = normalize_ascii(row[fields["tool"]])
        if tool in source_replacements:
            source, locator, completeness, verification = source_replacements[tool]
            row[fields["source"]] = source
            row[fields["source_locator"]] = locator
            row[fields["source_completeness"]] = completeness
            row[fields["verification"]] = verification
    assert len(rows) == 193, len(rows)
    assert len(clean) == 190, len(clean)
    assert len({normalize_ascii(row[fields["tool"]]) for row in clean}) == 55
    return headers, clean, fields


def cleaned_guideline_set() -> list[dict[str, str]]:
    workbook = openpyxl.load_workbook(GUIDELINE_BOOK, data_only=True)
    sheet = workbook["Guideline_summary"]
    rows = list(sheet.values)[1:]
    region = ""
    clean: list[dict[str, str]] = []
    for raw_region, document, doc_type, decision in rows:
        if raw_region:
            region = str(raw_region)
        if not document or not str(decision or "").startswith("INCLUDE"):
            continue
        document_ascii = normalize_ascii(document)
        if any(document_ascii.startswith(prefix) for prefix in REMOVED_GUIDELINE_PREFIXES):
            continue
        if document_ascii.startswith("CSBPR Rehabilitation 2025"):
            for part in ("Part 1", "Part 2", "Part 3"):
                clean.append({
                    "Region": region,
                    "Guideline / document": f"CSBPR Rehabilitation 2025 - {part}",
                    "Type": "Rehabilitation",
                    "English full-text status": "Retained from existing English-eligible set",
                    "Decision": "INCLUDE",
                    "Official English source": "Existing project source",
                })
            continue
        if document_ascii.startswith("CPG Stroke Rehabilitation Part 1"):
            document_ascii = "Clinical Practice Guideline for Stroke Rehabilitation in Korea - Part 1: Rehabilitation for Motor Function (2022)"
            source = "https://doi.org/10.12786/bn.2023.16.e18"
        elif document_ascii.startswith("CPG Stroke Rehabilitation Part 2"):
            document_ascii = "Clinical Practice Guideline for Stroke Rehabilitation in Korea - Part 2: Rehabilitation for Motor and Sensory Function (2024)"
            source = "https://doi.org/10.12786/bn.2025.18.e7"
        else:
            source = "Existing project source"
        clean.append({
            "Region": region,
            "Guideline / document": document_ascii,
            "Type": normalize_ascii(doc_type),
            "English full-text status": "Verified English full text" if region == "Korea" else "Retained from existing English-eligible set",
            "Decision": "INCLUDE",
            "Official English source": source,
        })

    clean.append({
        "Region": "China (mainland)",
        "Guideline / document": "Chinese Stroke Association guidelines for clinical management of ischaemic cerebrovascular diseases: executive summary and 2023 update",
        "Type": "Acute and longitudinal ischaemic stroke management",
        "English full-text status": "Verified English full text; independently screened candidate",
        "Decision": "INCLUDE",
        "Official English source": "https://doi.org/10.1136/svn-2023-002998",
    })
    assert len(clean) == 28, len(clean)
    return clean


def add_sheet(workbook: openpyxl.Workbook, name: str, rows: list[dict[str, object]]) -> None:
    sheet = workbook.create_sheet(name)
    headers = list(rows[0].keys()) if rows else []
    sheet.append(headers)
    for row in rows:
        sheet.append([row.get(header) for header in headers])

    dark = "1F4E78"
    light = "D9EAF7"
    thin_gray = Side(style="thin", color="B7C3CE")
    for cell in sheet[1]:
        cell.fill = PatternFill("solid", fgColor=dark)
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    for row_idx in range(2, sheet.max_row + 1):
        if row_idx % 2 == 0:
            for cell in sheet[row_idx]:
                cell.fill = PatternFill("solid", fgColor=light)
        for cell in sheet[row_idx]:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = Border(bottom=thin_gray)
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for index, header in enumerate(headers, start=1):
        values = [str(sheet.cell(row, index).value or "") for row in range(1, min(sheet.max_row, 80) + 1)]
        width = min(max(len(header) + 2, max((len(value) for value in values), default=0) + 2), 42)
        sheet.column_dimensions[get_column_letter(index)].width = max(12, width)
    sheet.row_dimensions[1].height = 32


def build_audit_workbook(
    headers: list[str],
    clean_rows: list[dict[str, object]],
    fields: dict[str, str],
    item_mappings: list[dict[str, object]],
    count_rows: list[dict[str, object]],
) -> None:
    workbook = openpyxl.Workbook()
    workbook.remove(workbook.active)
    add_sheet(workbook, "Guideline_source_audit", GUIDELINE_AUDIT)
    add_sheet(workbook, "Scale_source_audit", SCALE_AUDIT)
    add_sheet(workbook, "Cleaned_guideline_set", cleaned_guideline_set())

    tool_counts = Counter(normalize_ascii(row[fields["tool"]]) for row in clean_rows)
    tool_rows = []
    for tool, count in sorted(tool_counts.items()):
        if tool == "Modified Tardieu Scale":
            provenance = "Supplementary English measurement source (reclassified)"
            source = "RehabMeasures MTS instrument specification"
        else:
            provenance = "Retained project tool library"
            source = "Existing English instrument/manual source in bridge matrix"
        tool_rows.append({
            "Tool": tool,
            "Item/component rows": count,
            "Post-cleaning provenance": provenance,
            "English instrument status": source,
        })
    add_sheet(workbook, "Cleaned_tool_set", tool_rows)

    bridge_rows = [{header: row.get(header) for header in headers} for row in clean_rows]
    add_sheet(workbook, "Cleaned_bridge_matrix", bridge_rows)
    add_sheet(workbook, "Item_feature_mapping", item_mappings)
    add_sheet(workbook, "Count_summary", count_rows)

    workbook.properties.title = "English-source audit and cleaned bridge data for Table 2"
    workbook.properties.subject = "Stage 1 review artifact; source files unchanged"
    workbook.save(AUDIT_OUTPUT)


def set_cell_text(cell, text: str, *, bold: bool = False, size: float = 7.4, color: str = "000000") -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.line_spacing = 1.0
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.name = "Arial"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = tc_pr.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        tc_pr.append(shading)
    shading.set(qn("w:fill"), fill)


def set_cell_margins(cell, top: int = 55, start: int = 65, bottom: int = 55, end: int = 65) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin_name, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin_name}"))
        if node is None:
            node = OxmlElement(f"w:{margin_name}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_table_borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "bottom"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), "10")
        tag.set(qn("w:color"), "243746")
        borders.append(tag)
    for edge in ("left", "right", "insideV", "insideH"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "nil")
        borders.append(tag)


def set_row_top_border(row, color: str = "778899", size: str = "8") -> None:
    for cell in row.cells:
        tc_pr = cell._tc.get_or_add_tcPr()
        borders = tc_pr.first_child_found_in("w:tcBorders")
        if borders is None:
            borders = OxmlElement("w:tcBorders")
            tc_pr.append(borders)
        top = OxmlElement("w:top")
        top.set(qn("w:val"), "single")
        top.set(qn("w:sz"), size)
        top.set(qn("w:color"), color)
        borders.append(top)


def set_column_widths(table, widths: list[float]) -> None:
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            cell.width = Inches(width)
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.first_child_found_in("w:tcW")
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(int(width * 1440)))
            tc_w.set(qn("w:type"), "dxa")


def build_word(counts: dict[str, Counter], item_count: int, tool_count: int) -> None:
    document = Document()
    section = document.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Inches(11)
    section.page_height = Inches(8.5)
    section.top_margin = Inches(0.45)
    section.bottom_margin = Inches(0.45)
    section.left_margin = Inches(0.45)
    section.right_margin = Inches(0.45)

    normal = document.styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    normal.font.size = Pt(8)

    caption = document.add_paragraph()
    caption.paragraph_format.space_after = Pt(4)
    run = caption.add_run("Table 2. Computer-measurable feature framework linking clinical scale items to motion analysis.")
    run.bold = True
    run.font.name = "Arial"
    run.font.size = Pt(9)

    headers = [
        "Computer-measurable feature family",
        "Operational definition",
        "Representative clinical item or task context",
        "Computable variables",
        "Minimum required input",
        "Item mappings, n\nQ / P / U",
    ]
    table = document.add_table(rows=1, cols=6)
    table.autofit = False
    set_table_borders(table)
    set_repeat_header(table.rows[0])
    for cell, header in zip(table.rows[0].cells, headers):
        set_cell_margins(cell, top=75, bottom=75)
        set_cell_shading(cell, "D9E3E8")
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_text(cell, header, bold=True, size=7.2, color="172A3A")
    set_row_top_border(table.rows[0], color="243746", size="10")

    for family in FAMILY_ORDER:
        row = table.add_row()
        values = TABLE_ROWS[family]
        status_counts = counts[family]
        mapping = f"{status_counts['Quantifiable']} / {status_counts['Proxy only']} / {status_counts['Unresolved']}"
        texts = [family, values["definition"], values["context"], values["variables"], values["input"], mapping]
        for index, (cell, value) in enumerate(zip(row.cells, texts)):
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            if index == 0:
                set_cell_shading(cell, "EEF3F5")
            set_cell_text(cell, value, bold=index == 0, size=7.25)
        row.cells[5].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    boundary_row = table.add_row()
    set_row_top_border(boundary_row, color="657B86", size="9")
    boundary_counts = counts["Non-kinematic clinical information"]
    boundary_values = [
        "Non-kinematic clinical information (measurement boundary; not a sixth feature family)",
        "Score-defining information that ordinary motion video cannot reproduce, including force, passive resistance, tone, reflexes, sensation, pain, self-report and contextual clinical judgement.",
        "Manual muscle testing; passive stretch; sensory testing; pain or confidence ratings; need for hands-on assistance or supervision.",
        "No score-equivalent motion-only variable; visible behaviour may provide a task-specific proxy.",
        "Force, pressure or EMG sensors; instrumented objects; hands-on examination; clinician judgement; or patient-reported data.",
        f"{boundary_counts['Quantifiable']} / {boundary_counts['Proxy only']} / {boundary_counts['Unresolved']}",
    ]
    for index, (cell, value) in enumerate(zip(boundary_row.cells, boundary_values)):
        set_cell_margins(cell, top=70, bottom=70)
        set_cell_shading(cell, "F3F1EC" if index else "E6E1D7")
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
        set_cell_text(cell, value, bold=index == 0, size=7.15)
    boundary_row.cells[5].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    set_column_widths(table, [1.48, 1.73, 1.93, 1.72, 1.72, 1.00])

    note = document.add_paragraph()
    note.paragraph_format.space_before = Pt(4)
    note.paragraph_format.space_after = Pt(0)
    lead = note.add_run("Notes. ")
    lead.bold = True
    note.add_run(
        "Q, quantifiable from captured motion or directly computed kinematics; P, proxy only; U, unresolved from the target motion data. "
        "These labels describe technical observability, not equivalence to a validated clinical score. Task instructions are contextual metadata, not feature families: for example, moving the hand from the shoulder to the knee yields a wrist trajectory, completion time and trajectory-derived smoothness. "
        f"Items may map to more than one feature family; row totals therefore overlap and must not be summed as the number of unique scale items. Counts are based on {item_count} item/component mappings from {tool_count} English-eligible tools after source-language cleaning."
    )
    for run in note.runs:
        run.font.name = "Arial"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
        run.font.size = Pt(7.25)

    document.core_properties.title = "Draft Table 2 - computer-measurable feature framework"
    document.core_properties.subject = "Stage 1 Word draft; LaTeX not yet updated"
    document.save(WORD_OUTPUT)


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    headers, clean_rows, fields = load_clean_bridge()
    counts: dict[str, Counter] = defaultdict(Counter)
    item_mappings: list[dict[str, object]] = []

    for row in clean_rows:
        status = status_from_row(row, fields["status"])
        matches, boundary = classify_item(row, fields)
        for family in matches:
            counts[family][status] += 1
        if boundary:
            counts["Non-kinematic clinical information"][status] += 1

        mapping = {
            "Tool": normalize_ascii(row[fields["tool"]]),
            "Item #": row[fields["item_no"]],
            "Item / task": normalize_ascii(row[fields["item"]]),
            "Mapping status": status,
            "Task context (not a feature family)": normalize_ascii(row[fields["phase"]]),
        }
        for family in FAMILY_ORDER:
            mapping[family] = "Y" if family in matches else ""
            mapping[f"{family} - rule matches"] = "; ".join(matches.get(family, []))
        mapping["Non-kinematic boundary"] = "Y" if boundary else ""
        mapping["Score-defining information type"] = normalize_ascii(row[fields["score_info"]])
        mapping["Recommended AI feature"] = normalize_ascii(row[fields["feature"]])
        mapping["Manual review flag"] = "CHECK" if status != "Unresolved" and not matches else ""
        item_mappings.append(mapping)

    unclassified = [row for row in item_mappings if row["Manual review flag"] == "CHECK"]
    if unclassified:
        names = [(row["Tool"], row["Item #"], row["Item / task"]) for row in unclassified]
        raise AssertionError(f"Unclassified quantifiable/proxy rows: {names}")

    overall = Counter(status_from_row(row, fields["status"]) for row in clean_rows)
    count_rows = [
        {"Metric": "Included guideline documents", "Value": 28, "Definition / note": "Canada rehabilitation Parts 1-3 counted separately; one new CSA 2023 English guideline added."},
        {"Metric": "Regions represented", "Value": 9, "Definition / note": "Japan removed; mainland China retained through the independently eligible CSA English guideline."},
        {"Metric": "Guideline-derived distinct tools", "Value": 37, "Definition / note": "40 original tools minus JSS, JSS-M and MTS; MTS is retained through the supplementary English measurement stream."},
        {"Metric": "Canonical English-eligible tools", "Value": 55, "Definition / note": "58 original tools minus JSS, JSS-M and STEF."},
        {"Metric": "Cleaned item/component mappings", "Value": len(clean_rows), "Definition / note": "193 original mappings minus two Japan Stroke Scale rows and one STEF row."},
        {"Metric": "Overall quantifiable mappings", "Value": overall["Quantifiable"], "Definition / note": "Directly observable or computable from captured motion under the specified setup."},
        {"Metric": "Overall proxy-only mappings", "Value": overall["Proxy only"], "Definition / note": "Visible or computable proxy that does not reproduce the official score criterion."},
        {"Metric": "Overall unresolved mappings", "Value": overall["Unresolved"], "Definition / note": "Score-defining information unavailable from the target motion data."},
    ]
    for family in FAMILY_ORDER + ["Non-kinematic clinical information"]:
        count_rows.append({
            "Metric": family,
            "Value": f"Q {counts[family]['Quantifiable']} / P {counts[family]['Proxy only']} / U {counts[family]['Unresolved']}",
            "Definition / note": "Multi-label item mapping; family totals overlap." if family in FAMILY_ORDER else "Measurement boundary, not a sixth computational family.",
        })

    build_audit_workbook(headers, clean_rows, fields, item_mappings, count_rows)
    tool_count = len({normalize_ascii(row[fields["tool"]]) for row in clean_rows})
    build_word(counts, len(clean_rows), tool_count)
    print(f"Created: {AUDIT_OUTPUT}")
    print(f"Created: {WORD_OUTPUT}")
    print(f"Guidelines: 28; tools: {tool_count}; item/component mappings: {len(clean_rows)}")
    print(f"Overall status counts: {dict(overall)}")
    for family in FAMILY_ORDER + ["Non-kinematic clinical information"]:
        print(f"{family}: {dict(counts[family])}")


if __name__ == "__main__":
    main()
