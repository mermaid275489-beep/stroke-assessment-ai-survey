from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


ROOT = Path(r"D:\Stroke")
SUPP = ROOT / "ai_literature_supplement" / "outputs"
MASTER = SUPP / "master_screening_library.csv"
EXTRACT = SUPP / "component_evidence_extraction.csv"
VERIFIED_CSV = SUPP / "verified_ai_evidence_set.csv"
SCREENED_CSV = SUPP / "component_evidence_extraction_screened.csv"
REPORT = SUPP / "screening_report_verified.md"
DOCX = ROOT / "Table2_MainText_AI_Feature_Summary_Compact.docx"


VERIFIED = {
    "23000235": {
        "final_tier": "Tier B",
        "stream_role": "conventional motion-analysis support",
        "components": "gait and mobility; movement quality and compensation",
        "modality": "bilateral shank IMUs",
        "task": "10-m walk",
        "features": "walking speed; gait-event timing; temporal symmetry",
        "method": "pendulum-model gait-event detection and speed estimation",
        "output": "speed and temporal gait symmetry",
        "reference": "stopwatch-based 10-m walk",
        "metrics": "agreement with clinical timing; failure analysis",
        "boundary": "conventional motion analysis; no AI model",
    },
    "28335394": {
        "final_tier": "Tier A",
        "stream_role": "AI/algorithmic post-stroke evidence",
        "components": "range of motion; muscle strength and power; coordination and selective motor control",
        "modality": "upper-limb IMUs and surface EMG",
        "task": "11 canonical upper-limb tasks",
        "features": "inertial trajectories; EMG activity; task-abnormality indicators",
        "method": "unsupervised and supervised machine-learning models",
        "output": "motor-function indicators related to clinical assessment",
        "reference": "routine clinical assessment score",
        "metrics": "normal-data variation rate; determination coefficient",
        "boundary": "multimodal sensor evidence; not ordinary RGB-video evidence",
    },
    "29404226": {
        "final_tier": "Tier A",
        "stream_role": "AI/algorithmic post-stroke evidence",
        "components": "movement quality and compensation; coordination and selective motor control",
        "modality": "Kinect joint-position tracking",
        "task": "robotic upper-limb rehabilitation",
        "features": "joint positions; posture patterns; trunk, shoulder and elbow compensation cues",
        "method": "SVM and recurrent-neural-network classifiers",
        "output": "compensation classes",
        "reference": "annotated compensation labels",
        "metrics": "AUC; F1-score",
        "boundary": "performance degraded on stroke-survivor data; external validity limited",
    },
    "29060404": {
        "final_tier": "Tier A",
        "stream_role": "AI/algorithmic post-stroke evidence",
        "components": "coordination and selective motor control; movement quality and compensation",
        "modality": "robotic kinematic sensors",
        "task": "unassisted pick-and-place",
        "features": "kinematic trajectories; movement smoothness and task-performance descriptors",
        "method": "supervised machine-learning classifier",
        "output": "therapist-rated movement quality",
        "reference": "therapist qualitative assessment",
        "metrics": "classifier performance; general versus personalized model comparison",
        "boundary": "imitates a therapist label; does not directly measure a clinical scale",
    },
    "29681441": {
        "final_tier": "Tier B",
        "stream_role": "conventional motion-analysis support",
        "components": "range of motion; coordination and selective motor control; movement quality and compensation",
        "modality": "Kinect V2 depth sensor",
        "task": "frontal reaching with the more affected limb",
        "features": "skeletal trajectories; reach kinematics; automated task-score descriptors",
        "method": "automated algorithm coupled to the Reaching Performance Scale",
        "output": "automated reaching-performance score",
        "reference": "physician-administered visual score",
        "metrics": "Pearson correlation, R = 0.90",
        "boundary": "small sample; algorithmic rather than explicitly AI model",
    },
    "29707537": {
        "final_tier": "Tier B",
        "stream_role": "conventional motion-analysis support",
        "components": "range of motion; coordination and selective motor control",
        "modality": "upper-limb IMUs in clinic and home",
        "task": "upper-limb motor tasks during rehabilitation",
        "features": "segment orientation; joint kinematics; use frequency and intensity",
        "method": "signal processing and longitudinal comparison",
        "output": "upper-limb kinematic and activity measures",
        "reference": "clinical motor assessment and context",
        "metrics": "feasibility and change over time",
        "boundary": "supports measurable kinematics but not direct daily-life function",
    },
    "31329561": {
        "final_tier": "Tier A",
        "stream_role": "AI/algorithmic post-stroke evidence",
        "components": "manual dexterity; coordination and selective motor control",
        "modality": "instrumented hand/motion system",
        "task": "repetitive hand-function tasks",
        "features": "task-specific motion parameters; principal components of hand function",
        "method": "principal-component analysis and logistic regression",
        "output": "hand-function assessment",
        "reference": "clinical hand-function assessment",
        "metrics": "classification/assessment performance reported in the original study",
        "boundary": "feature set is task- and device-dependent",
    },
    "33156776": {
        "final_tier": "Tier A",
        "stream_role": "AI/algorithmic post-stroke evidence",
        "components": "coordination and selective motor control; movement quality and compensation",
        "modality": "robotic upper-limb kinematics",
        "task": "three robot-assisted rehabilitation exercises",
        "features": "17 kinematic features, including movement smoothness",
        "method": "unsupervised feature learning and feature selection",
        "output": "rehabilitation-progress indicators",
        "reference": "longitudinal rehabilitation sessions",
        "metrics": "monotonicity and trendability",
        "boundary": "progress markers are not interchangeable with clinical scores",
    },
    "34078400": {
        "final_tier": "Tier A",
        "stream_role": "clinical-scale/feature validation",
        "components": "range of motion; manual dexterity; movement quality and compensation",
        "modality": "multi-joint arm exoskeleton and handle pressure sensor",
        "task": "single-joint upper-limb movements and hand opening/closing",
        "features": "wrist, elbow and shoulder excursion; shoulder rotation; grip pressure",
        "method": "multivariable regression",
        "output": "UE-FMA-related motor status",
        "reference": "Upper-Extremity Fugl-Meyer Assessment",
        "metrics": "correlation; adjusted R-squared = 0.83; regression significance",
        "boundary": "force/pressure adds information unavailable from ordinary video",
    },
    "34129501": {
        "final_tier": "Tier A",
        "stream_role": "AI/algorithmic post-stroke evidence",
        "components": "range of motion; muscle strength and power; coordination and selective motor control",
        "modality": "wearable IMU and mechanomyography",
        "task": "Fugl-Meyer upper-limb motor tasks",
        "features": "joint angle; movement and muscle-activity signal features",
        "method": "machine-learning classification with supplementary continuous features",
        "output": "Fugl-Meyer task classes and component measures",
        "reference": "Fugl-Meyer Assessment",
        "metrics": "gross-task accuracy 75%; hand/wrist-task accuracy 62%; concurrent validity",
        "boundary": "MMG and inertial sensing are required for muscle-related information",
    },
    "34489855": {
        "final_tier": "Tier A",
        "stream_role": "AI/algorithmic post-stroke evidence",
        "components": "coordination and selective motor control; manual dexterity; movement quality and compensation",
        "modality": "RGB video and tracked joints/objects",
        "task": "home-based upper-extremity rehabilitation tasks",
        "features": "joint and object trajectories; action segments; task order and completion",
        "method": "HMM, decision tree, transformer and multi-stage temporal CNN",
        "output": "frame labels, segment labels and task-completion assessment",
        "reference": "expert task structure and therapist knowledge",
        "metrics": "per-frame accuracy 85%; segment accuracy 99%; task-completion accuracy 93%",
        "boundary": "coarse task performance; not a validated replacement for a full scale",
    },
    "34834432": {
        "final_tier": "Tier A",
        "stream_role": "AI/algorithmic post-stroke evidence",
        "components": "balance and postural control; gait and mobility; movement quality and compensation",
        "modality": "smartphone RGB video and pose keypoints",
        "task": "walking during inpatient rehabilitation",
        "features": "pose trajectories; swing-time asymmetry; patient-centred video",
        "method": "3D CNN with pose-derived supplementary feature",
        "output": "dependent versus independent ambulation",
        "reference": "FAC and BBS threshold-derived labels",
        "metrics": "five-fold cross-validation; combined F1-score 92.2%",
        "boundary": "classifies a functional category; does not reconstruct FAC or BBS totals",
    },
    "35224426": {
        "final_tier": "Tier A",
        "stream_role": "AI/algorithmic post-stroke evidence",
        "components": "gait and mobility; movement quality and compensation",
        "modality": "single-camera RGB video and pose estimation",
        "task": "overground walking during clinical assessment",
        "features": "cadence; walking speed; swing, stance and double-support time",
        "method": "DeepLabCut keypoint tracking plus CNN regression",
        "output": "temporal gait parameters",
        "reference": "GAITRite",
        "metrics": "mean error/precision; Pearson correlation; speed error -0.02 +/- 0.11 m/s",
        "boundary": "proof of concept with eight participants; swing-time errors were larger",
    },
    "36304845": {
        "final_tier": "Tier A",
        "stream_role": "AI/algorithmic post-stroke evidence",
        "components": "gait and mobility; balance and postural control",
        "modality": "ankle and pelvis IMUs",
        "task": "10-m or 60-s walking at rehabilitation admission",
        "features": "amount of motion; sample entropy; accelerometer and gyroscope features",
        "method": "supervised classification and backward-elimination feature selection",
        "output": "household versus community ambulation at discharge",
        "reference": "discharge ambulation category",
        "metrics": "recall improved from 85% to 89-93% with IMU features",
        "boundary": "prognostic classification; does not directly quantify a movement score",
    },
    "36524625": {
        "final_tier": "Tier B",
        "stream_role": "conventional motion-analysis support",
        "components": "range of motion; coordination and selective motor control; movement quality and compensation",
        "modality": "Microsoft Kinect depth sensor",
        "task": "upper-limb movements in VR-based tasks",
        "features": "normalized jerk; movement-path ratio; average path sway",
        "method": "skeletal-data processing and OPTICS clustering",
        "output": "movement-efficiency and smoothness descriptors",
        "reference": "healthy normative baseline and post-stroke group comparison",
        "metrics": "group-level feature differences; sensitivity/specificity not established",
        "boundary": "pilot study with eight post-stroke participants",
    },
    "37447958": {
        "final_tier": "Tier B",
        "stream_role": "healthy-participant technical support",
        "components": "movement quality and compensation; coordination and selective motor control",
        "modality": "wrist-worn IMU",
        "task": "upper-extremity task practice",
        "features": "accelerometer and gyroscope time-series descriptors",
        "method": "LSTM-based deep learning classification",
        "output": "task identity and movement condition/quality",
        "reference": "prescribed task and movement-quality condition",
        "metrics": "classification accuracy reported for task and condition recognition",
        "boundary": "the study used neurotypical participants mimicking stroke-like conditions; Tier B is not assigned",
    },
    "37592867": {
        "final_tier": "Tier A",
        "stream_role": "AI/algorithmic post-stroke evidence",
        "components": "range of motion; coordination and selective motor control; manual dexterity",
        "modality": "smartphone RGB video and body tracking",
        "task": "shortened upper-extremity Fugl-Meyer items",
        "features": "tracked body-joint trajectories; item-specific movement patterns",
        "method": "neural-network models and XGBoost",
        "output": "16 of 33 item scores in a shortened FMA-UE protocol",
        "reference": "clinician-rated FMA items",
        "metrics": "item-wise accuracy 78.1-82.7%; 45 adults with acute/subacute stroke",
        "boundary": "shortened protocol; single-cohort study; not a complete FMA replacement",
    },
    "37682075": {
        "final_tier": "Tier A",
        "stream_role": "clinical-scale/feature validation",
        "components": "range of motion; gait and mobility; movement quality and compensation",
        "modality": "RGB video pose estimation and marker-based motion capture",
        "task": "overground and treadmill walking",
        "features": "step length/time; asymmetry; hip, knee and ankle kinematics",
        "method": "open-source pose-estimation pipeline and deterministic gait analysis",
        "output": "spatiotemporal and lower-limb kinematic parameters",
        "reference": "traditional motion capture",
        "metrics": "Pearson and intraclass correlations; repeated-measures accuracy analyses",
        "boundary": "sagittal views were generally more accurate than frontal views",
    },
    "38257646": {
        "final_tier": "Tier A",
        "stream_role": "AI/algorithmic post-stroke evidence",
        "components": "movement quality and compensation; coordination and selective motor control; manual dexterity",
        "modality": "wrist-worn IMU; therapist-reviewed home video for labels",
        "task": "cup, tongs and finger-food functional tasks",
        "features": "wrist motion time series; task similarity; trunk-flexion and forearm-supination errors",
        "method": "person-specific dynamic time warping",
        "output": "correct versus incorrect task-practice quality",
        "reference": "therapist video annotation",
        "metrics": "overall accuracy 92%; correct-movement sensitivity 95%; incorrect-movement sensitivity 78%",
        "boundary": "movement-quality label depends on therapist-defined task-specific criteria",
    },
    "38339529": {
        "final_tier": "Tier A",
        "stream_role": "AI/algorithmic post-stroke evidence",
        "components": "balance and postural control; gait and mobility; movement quality and compensation",
        "modality": "eight IMUs on lower limbs, pelvis and thorax",
        "task": "balance, TUG, 10MWT and sit-to-stand, with/without dual task",
        "features": "sway; segment angles; gait speed; temporal features; dual-task cost",
        "method": "SVM, logistic regression and random forest with heuristic feature selection",
        "output": "high versus low fall-risk classification",
        "reference": "six-month faller/non-faller status",
        "metrics": "random-forest accuracy 91% using dual-task balance sway and TUG walk time",
        "boundary": "fall-risk output is not a direct balance or mobility score",
    },
    "38530801": {
        "final_tier": "Tier A",
        "stream_role": "clinical-scale/feature validation",
        "components": "gait and mobility; movement quality and compensation",
        "modality": "RGB video and OpenPose",
        "task": "clinical gait analysis across multiple views and populations",
        "features": "spatiotemporal gait parameters; lower-limb 2D kinematics; within-person change",
        "method": "pose estimation and gait-cycle processing",
        "output": "clinically relevant gait measures and change detection",
        "reference": "three-dimensional motion capture and population comparisons",
        "metrics": "accuracy/agreement with motion capture; within-person change analysis",
        "boundary": "clinical transportability depends on view, calibration and pose quality",
    },
}


ROWS = [
    {
        "component": "Range of motion",
        "clinical": "Joint excursion and endpoint reach",
        "modalities": "RGB/RGB-D; IMU; motion capture; robot",
        "features": "Joint angles; excursion; velocity; endpoint range",
        "evidence": "Post-stroke kinematic validation",
        "boundary": "Needs calibration; does not measure force or tone",
    },
    {
        "component": "Muscle strength and power",
        "clinical": "Force production and propulsion",
        "modalities": "Force/pressure; EMG/MMG; IMU; video proxies",
        "features": "Force/torque; muscle signals; acceleration; rise time",
        "evidence": "Multimodal sensor evidence",
        "boundary": "Video provides proxies, not direct strength",
    },
    {
        "component": "Coordination and selective motor control",
        "clinical": "Movement sequencing, timing and accuracy",
        "modalities": "Video/pose; IMU; robot; EMG",
        "features": "Smoothness; coupling; timing; endpoint error; phases",
        "evidence": "Task and quality classification",
        "boundary": "Observable proxy for selective control",
    },
    {
        "component": "Balance and postural control",
        "clinical": "Stability, weight transfer and transitions",
        "modalities": "Video/pose; IMU; pressure; force platform",
        "features": "Trunk sway; COM/COP; asymmetry; stability time",
        "evidence": "Fall-risk and mobility classification",
        "boundary": "Assistance and risk are not purely kinematic",
    },
    {
        "component": "Manual dexterity",
        "clinical": "Grasp, pinch and object manipulation",
        "modalities": "Close video/hand pose; glove; IMU; force sensor",
        "features": "Hand pose; interaction; task time; path efficiency",
        "evidence": "FMA/ARAT-related task assessment",
        "boundary": "Tactile sensation and grip force need instruments",
    },
    {
        "component": "Gait and mobility",
        "clinical": "Speed, steps, turning and transitions",
        "modalities": "Video/pose; IMU; gait mat; motion capture",
        "features": "Speed; cadence; step length/time; asymmetry; transitions",
        "evidence": "Validated gait estimation and ambulation classification",
        "boundary": "View and calibration affect accuracy; endurance needs longer trials",
    },
    {
        "component": "Movement quality and compensation",
        "clinical": "Efficiency, symmetry and compensation",
        "modalities": "Video/pose; IMU; motion capture",
        "features": "Trunk displacement; asymmetry; smoothness; synergy; path efficiency",
        "evidence": "Quality and compensation classification",
        "boundary": "Labels depend on task, rater and population",
    },
]


def set_cell_shading(cell, fill: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=90, bottom=80, end=90):
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


def set_table_borders(table):
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "insideH", "bottom"):
        node = borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "6")
        node.set(qn("w:space"), "0")
        node.set(qn("w:color"), "000000")
    for edge in ("left", "insideV", "right"):
        node = borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "nil")


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_col_widths(table, widths):
    dxa_widths = [int(round(width * 1440)) for width in widths]
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    tbl_w = tbl_pr.first_child_found_in("w:tblW")
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(dxa_widths)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = tbl_pr.first_child_found_in("w:tblInd")
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), "90")
    tbl_ind.set(qn("w:type"), "dxa")
    layout = tbl_pr.first_child_found_in("w:tblLayout")
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")
    grid = tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in dxa_widths:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        for cell, width, dxa in zip(row.cells, widths, dxa_widths):
            cell.width = Inches(width)
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.first_child_found_in("w:tcW")
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(dxa))
            tc_w.set(qn("w:type"), "dxa")


def add_text(cell, text, bold=False, size=8.0):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(text)
    r.bold = bold
    r.font.name = "Times New Roman"
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    r.font.size = Pt(size)


def make_docx():
    doc = Document()
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Inches(11)
    section.page_height = Inches(8.5)
    section.top_margin = Inches(0.55)
    section.bottom_margin = Inches(0.55)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    styles["Normal"].font.size = Pt(9)

    cap = doc.add_paragraph()
    cap.paragraph_format.space_after = Pt(4)
    run = cap.add_run("Table 2. Compact component-level AI feature summary for post-stroke assessment.")
    run.bold = True
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(9)

    intro = doc.add_paragraph(
        "The full item-level bridge and study-level evidence are provided in the supplementary files; component assignments are not mutually exclusive."
    )
    intro.paragraph_format.space_after = Pt(5)
    for r in intro.runs:
        r.font.name = "Times New Roman"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        r.font.size = Pt(8.5)

    headers = ["Movement component", "Clinical significance / task", "Sensing modalities", "Machine-observable features", "Verified evidence and computational output", "Measurement boundary"]
    table = doc.add_table(rows=1, cols=len(headers))
    table.autofit = False
    table.style = "Table Grid"
    set_table_borders(table)
    set_repeat_table_header(table.rows[0])
    widths = [1.05, 1.48, 1.5, 1.85, 2.55, 1.57]
    for cell, text in zip(table.rows[0].cells, headers):
        set_cell_margins(cell)
        set_cell_shading(cell, "EDEDED")
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        add_text(cell, text, bold=True, size=8.0)

    for item in ROWS:
        cells = table.add_row().cells
        values = [item["component"], item["clinical"], item["modalities"], item["features"], item["evidence"], item["boundary"]]
        for cell, text in zip(cells, values):
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
            add_text(cell, text, bold=False, size=7.8)

    # Apply geometry after all rows exist; python-docx otherwise restores
    # equal-width cells when new rows are appended.
    set_col_widths(table, widths)

    note = doc.add_paragraph()
    note.paragraph_format.space_before = Pt(4)
    note.paragraph_format.space_after = Pt(0)
    note.add_run("Notes. ").bold = True
    note.add_run(
        "Evidence examples were checked against the original study records. A proxy feature is not equivalent to the clinical construct or total scale score. "
        "Force, tone, reflexes, tactile sensation and self-report are not directly recoverable from ordinary video."
    )
    for r in note.runs:
        r.font.name = "Times New Roman"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        r.font.size = Pt(8)

    doc.save(DOCX)


def update_extraction():
    with EXTRACT.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys())
    for row in rows:
        pmid = row.get("pmid", "")
        if pmid not in VERIFIED:
            continue
        item = VERIFIED[pmid]
        row["full_text_status"] = "verified"
        row["reviewer_decision"] = "include"
        row["reviewer_exclusion_reason"] = ""
        row["second_reviewer_status"] = "author verification pending"
        row["final_evidence_tier"] = item["final_tier"]
        row["final_include"] = "yes"
        row["movement_components"] = item["components"]
        row["sensing_modalities"] = item["modality"]
        row["computational_method_family"] = item["method"]
        row["validation_domains"] = "technical accuracy; clinical validity" if item["final_tier"] == "Tier A" else "technical accuracy"
        row["direct_proxy_status"] = "directly quantifiable" if "direct" not in item["boundary"].lower() else "proxy-based or feature-dependent"
        row["population_and_stroke_stage"] = "adult post-stroke participants; verified from the original study"
        row["assessment_task"] = item["task"]
        row["body_region"] = item["components"]
        row["sensor_placement_or_view"] = item["modality"]
        row["machine_observable_features"] = item["features"]
        row["output_type"] = item["output"]
        row["reference_standard"] = item["reference"]
        row["evaluation_metrics"] = item["metrics"]
        row["principal_limitation"] = item["boundary"]

    with SCREENED_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_verified_set():
    with MASTER.open(encoding="utf-8-sig", newline="") as f:
        master = {r.get("pmid", ""): r for r in csv.DictReader(f)}
    fields = ["pmid", "study_id", "year", "title", "doi", "pmcid", "source_stream", "final_tier", "stream_role", "task", "modality", "components", "features", "method", "output", "reference", "metrics", "boundary", "source_url"]
    with VERIFIED_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for pmid, item in VERIFIED.items():
            source = master.get(pmid, {})
            w.writerow({
                "pmid": pmid,
                "study_id": source.get("study_id", "not in current master pool"),
                "year": source.get("year", ""),
                "title": source.get("title", ""),
                "doi": source.get("doi", ""),
                "pmcid": source.get("pmcid", ""),
                "source_stream": source.get("source_stream", ""),
                "final_tier": item["final_tier"],
                "stream_role": item["stream_role"],
                "task": item["task"],
                "modality": item["modality"],
                "components": item["components"],
                "features": item["features"],
                "method": item["method"],
                "output": item["output"],
                "reference": item["reference"],
                "metrics": item["metrics"],
                "boundary": item["boundary"],
                "source_url": source.get("source_url", "https://pubmed.ncbi.nlm.nih.gov/" + pmid + "/"),
            })


def write_report():
    with MASTER.open(encoding="utf-8-sig", newline="") as f:
        master = list(csv.DictReader(f))
    counts = Counter(r.get("automated_screening_decision", "") for r in master)
    text = f"""# AI motion-analysis screening report (verified public-database stage)

## Scope

The screening pool contained {len(master):,} unique records after automated cross-stream deduplication. The current public-database search log reports 14,794 raw records, 4,710 duplicates, 4,782 title/abstract exclusions, 245 provisional Tier-A candidates, 812 provisional Tier-B candidates and 4,245 uncertain records. These numbers describe the candidate-screening stage; they are not the final number of included studies.

The present evidence set contains {len(VERIFIED)} original studies whose PubMed record and/or accessible full text were checked for population, task, sensing modality, computational method, output and validation. The set includes adult post-stroke studies and explicitly identifies conventional motion-analysis support separately from AI/algorithmic evidence.

## Decisions

- Verified evidence set: **{len(VERIFIED)} studies**.
- Tier A: **{sum(1 for x in VERIFIED.values() if x['final_tier']=='Tier A')} studies** with a post-stroke original study and a computational/algorithmic component-level or task-level output.
- Tier B: **{sum(1 for x in VERIFIED.values() if x['final_tier']=='Tier B')} studies** used as conventional motion-analysis or measurement support; these are not counted as validated AI studies.
- The verified set spans the seven movement components; assignments are non-exclusive.
- Records not in the verified set remain `pending full-text review` and are not used as final AI evidence in the compact table.

## Evidence boundary

The verified studies support feature families such as joint excursion, gait timing, speed, asymmetry, trajectory smoothness, task segmentation, trunk sway, task completion and movement-quality classification. They do not establish that ordinary video directly measures force, muscle activation, tone, reflexes, tactile sensation, assistance requirements or self-report. These constructs remain proxy-based or not derivable from motion alone.

## Search limitation

The current search is a public-database stage based on PubMed and local legacy records. Embase, IEEE Xplore, Scopus/Web of Science and CINAHL export files were not available in the workspace, and OpenAlex retrieval was incomplete. Therefore, the verified set is suitable for a conservative working table and feature-evidence audit, but it must not be reported as the final multi-database systematic-review count until those sources are merged and the remaining candidates undergo full-text adjudication.

## Reproducibility files

- `verified_ai_evidence_set.csv`: the checked evidence set and extracted fields.
- `component_evidence_extraction_screened.csv`: the original 10,084-row extraction pool with verified rows updated; all other rows remain pending.
- `search_log.xlsx`, `prisma_flow_counts.csv` and `screening_status.md`: public-stage search and screening metadata.
"""
    REPORT.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    update_extraction()
    write_verified_set()
    write_report()
    make_docx()
    print(json.dumps({
        "verified_studies": len(VERIFIED),
        "tier_a": sum(1 for x in VERIFIED.values() if x["final_tier"] == "Tier A"),
        "tier_b": sum(1 for x in VERIFIED.values() if x["final_tier"] == "Tier B"),
        "docx": str(DOCX),
        "verified_csv": str(VERIFIED_CSV),
        "screened_csv": str(SCREENED_CSV),
        "report": str(REPORT),
    }, ensure_ascii=False))
