from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from build_screened_ai_table import (
    add_text,
    set_cell_margins,
    set_cell_shading,
    set_col_widths,
    set_repeat_table_header,
    set_table_borders,
)


ROOT = Path(r"D:\Stroke")
OUTPUT = ROOT / "Table2_Clinical_to_AI_Bridge_Compact_Revised.docx"


BLOCK_A = [
    [
        "Joint mobility and range of motion",
        "Active excursion; FMA-UE/LE and reach",
        "Joint angle; excursion; velocity",
        "D / P",
        "Post-stroke kinematics; joint-angle extraction",
        "View/calibration; passive ROM not video-derived",
    ],
    [
        "Muscle strength and force production",
        "Force generation; FMA, MRC and sit-to-stand",
        "Rise time; acceleration; weight-shift symmetry",
        "P; direct with sensors",
        "Proxy studies; force/EMG validation",
        "Video is indirect",
    ],
    [
        "Coordination and selective motor control",
        "Timing, sequencing and accuracy; FMA and ARAT",
        "Smoothness; coupling; timing; endpoint error",
        "P",
        "Post-stroke trajectories; task analysis",
        "Not a direct neural measure",
    ],
    [
        "Balance and postural control",
        "Stability, transfer and recovery; BBS, TIS and Mini-BESTest",
        "Sway; COM/COP; symmetry; recovery",
        "D / P",
        "Post-stroke sway; balance classification",
        "Risk/assistance need context",
    ],
    [
        "Manual dexterity and upper-limb task execution",
        "Grasp, pinch and manipulation; ARAT, BBT and 9HPT",
        "Hand pose; interaction; task time",
        "D / P",
        "Upper-limb pose; task analysis",
        "Tactile/force need sensors",
    ],
    [
        "Gait and functional mobility",
        "Speed, endurance, turns and transitions; FAC, 10MWT, 6MWT and DGI",
        "Speed; cadence; step timing; turns",
        "D / P",
        "Post-stroke gait; ambulation estimation",
        "Endurance needs longer trials",
    ],
    [
        "Movement quality and compensation (modifier)",
        "Smoothness, symmetry and compensation",
        "Smoothness; asymmetry; trunk shift",
        "Modifier",
        "Cross-component kinematics; quality analysis",
        "Not a separate score domain",
    ],
]

BLOCK_B = [
    [
        "Assistance / supervision",
        "Help, cueing and supervision; FAC, BI and FIM",
        "Helper contact; aid use; task completion",
        "Proxy",
        "Video context; event analysis",
        "Task-specific validation needed",
    ],
    [
        "Risk judgment",
        "Balance loss and safety; BBS, Mini-BESTest and DGI",
        "Sway; recovery step; obstacle contact",
        "Proxy",
        "Video/pose; event detection",
        "Not the clinical risk judgment",
    ],
    [
        "Applied force / tactile",
        "Force, resistance and touch; FMA and WMFT",
        "Force/pressure; contact timing",
        "Direct sensors / Proxy video",
        "Force/pressure/EMG; instrumented validation",
        "Tactile sensation not video-derived",
    ],
    [
        "Tone / reflex",
        "Passive resistance and reflex response; FMA and NIHSS",
        "No direct motion feature",
        "Not derivable",
        "No validated motion-only equivalent",
        "Examiner/physiology required",
    ],
    [
        "Self-report",
        "Ability, confidence and difficulty; SIS and ABILHAND",
        "No score-equivalent feature",
        "Not derivable",
        "Behavioral proxy; no score equivalence",
        "Questionnaire/interview required",
    ],
]


def add_block_row(table, label):
    cells = table.add_row().cells
    # Keep six physical cells so the fixed-width table remains valid after
    # pagination and can be audited by standard table-geometry checks.
    for cell in cells:
        set_cell_margins(cell, top=75, start=90, bottom=75, end=90)
        set_cell_shading(cell, "D9E2F3")
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    add_text(cells[0], label, bold=True, size=8.0)


def add_data_cell(cell, text, column_index):
    """Format the evidence column as short, readable evidence phrases."""
    if column_index == 4:
        text = text.replace("; ", ";\n")
        set_cell_margins(cell, top=100, start=90, bottom=100, end=90)
    else:
        set_cell_margins(cell)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
    add_text(cell, text, size=7.45)
    if column_index == 4:
        paragraph = cell.paragraphs[0]
        paragraph.paragraph_format.line_spacing = 1.12


def make_docx():
    doc = Document()
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Inches(11)
    section.page_height = Inches(8.5)
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)
    doc.styles["Normal"].font.name = "Times New Roman"
    doc.styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    doc.styles["Normal"].font.size = Pt(8.5)

    cap = doc.add_paragraph()
    cap.paragraph_format.space_after = Pt(3)
    run = cap.add_run("Table 2. Orthogonal bridge from clinical score definitions to machine-observable features.")
    run.bold = True
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(9)

    intro = doc.add_paragraph(
        "The six primary movement components follow Table 1; quality and compensation is a cross-component modifier. "
        "Non-kinematic score information is shown separately. Evidence labels summarize the supporting motion-analysis evidence; counts are item-level mappings."
    )
    intro.paragraph_format.space_after = Pt(4)
    for r in intro.runs:
        r.font.name = "Times New Roman"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        r.font.size = Pt(8)

    headers = [
        "Component / score-defining information",
        "Clinical anchor and representative items",
        "AI-supported observable feature(s)",
        "Mapping status / item counts",
        "Evidence basis / validation need",
        "Boundary / residual gap",
    ]
    table = doc.add_table(rows=1, cols=6)
    table.autofit = False
    set_table_borders(table)
    set_repeat_table_header(table.rows[0])
    widths = [1.42, 2.12, 1.90, 1.72, 1.28, 1.56]
    for cell, text in zip(table.rows[0].cells, headers):
        set_cell_margins(cell)
        set_cell_shading(cell, "EDEDED")
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        add_text(cell, text, bold=True, size=7.8)

    add_block_row(table, "A. Primary movement components")
    for row in BLOCK_A:
        cells = table.add_row().cells
        for column_index, (cell, text) in enumerate(zip(cells, row)):
            add_data_cell(cell, text, column_index)

    add_block_row(table, "B. Non-kinematic score-defining information")
    for row in BLOCK_B:
        cells = table.add_row().cells
        for column_index, (cell, text) in enumerate(zip(cells, row)):
            add_data_cell(cell, text, column_index)

    # Geometry is applied after every row has been added.
    set_col_widths(table, widths)

    note = doc.add_paragraph()
    note.paragraph_format.space_before = Pt(3)
    note.paragraph_format.space_after = Pt(0)
    note.add_run("Notes. ").bold = True
    note.add_run(
        "D, Direct; P, Proxy; N, Not derivable. These describe measurability from the available sensing setup, not clinical validity. "
        "D20 / P20 / N4 denotes 20 direct, 20 proxy and 4 non-derivable item mappings, not studies. Counts overlap across components. "
        "Evidence labels summarize post-stroke kinematics, pose/event detection, force/EMG or proxy studies. A proxy is observable or inferable, but requires task-specific validation and does not reproduce the official score. "
        "Quality and compensation is a cross-component modifier; tone/reflex and self-report remain outside motion-only measurement."
    )
    for r in note.runs:
        r.font.name = "Times New Roman"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        r.font.size = Pt(7.6)

    doc.save(OUTPUT)


if __name__ == "__main__":
    make_docx()
    print(OUTPUT)
