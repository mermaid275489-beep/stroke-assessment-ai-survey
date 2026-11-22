from pathlib import Path
import re


ROOT = Path(r"D:\Stroke")
SOURCE = ROOT / "Supplementary_Table_S1_Guidelines_Compact.tex"
OUTPUT = ROOT / "Supplementary_Table_S1_Guidelines_Condensed.tex"


FOCI = [
    "Cross-setting rehabilitation: assessment, prognosis, intervention and community reintegration",
    "Post-stroke rehabilitation: assessment, prognosis, intervention, transitions and participation",
    "AFO/FES selection for walking, balance and mobility",
    "Intensive task-specific locomotor training in chronic stroke",
    "Acute ischaemic stroke diagnosis, reperfusion, management and early prevention",
    "aSAH diagnosis, acute treatment, complication management and recovery",
    "Secondary prevention: risk assessment, medication, lifestyle and follow-up",
    "ICH diagnosis, haemostasis, blood-pressure management, surgery and recovery",
    "Stroke services, acute care, rehabilitation and life after stroke",
    "Adult rehabilitation: assessment, goals, therapy and community care",
    "Acute stroke/TIA recognition, imaging, reperfusion and initial management",
    "Rehabilitation planning: screening, assessment, prognosis, goals and transitions",
    "Rehabilitation delivery: therapy dose, mobility, upper-limb function and cognition",
    "ADL, self-management, participation, social roles and long-term follow-up",
    "Acute management: recognition, imaging, reperfusion and stroke-unit care",
    "Acute ICH management, complications and recovery planning",
    "Secondary prevention: vascular risk, antithrombotics and lifestyle",
    "Rehabilitation assessment and intervention across settings, including participation",
    "Rehabilitation services, workforce, reintegration and quality improvement",
    "Acute-care standard: recognition, treatment, inpatient care and rehabilitation transition",
    "Post-stroke motor-rehabilitation assessment and intervention",
    "Pharmacological support for early motor rehabilitation after ischaemic stroke",
    "Stroke evaluation, treatment, rehabilitation and secondary prevention",
    "Upper- and lower-limb function, gait, balance and task practice",
    "Motor and sensory rehabilitation, upper limb, assistive technology and shoulder care",
    "Cerebrovascular rehabilitation assessment, early initiation and service coordination",
    "Acute ischaemic stroke diagnosis and treatment",
    "ICH/SAH diagnosis, treatment, complication management and risk reduction",
    "Cerebrovascular prevention and risk-factor management",
    "Integrated rehabilitation pathways, standardized assessment and community reintegration",
    "Rehabilitation service planning, capacity, continuity and participation",
    "Acute ischaemic stroke assessment, treatment and recurrence prevention",
]


def split_unescaped_ampersands(line: str) -> list[str]:
    if line.rstrip().endswith(r"\\"):
        line = line.rstrip()[:-2]
    return [part.strip() for part in re.split(r"(?<!\\)&", line)]


def compact_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


source = SOURCE.read_text(encoding="utf-8")
source_rows = [
    line
    for line in source.splitlines()
    if re.search(r"\\cite\{", line) and line.rstrip().endswith(r"\\")
]

if len(source_rows) != 32 or len(FOCI) != 32:
    raise RuntimeError(
        f"Expected 32 guideline rows and 32 focus statements; found "
        f"{len(source_rows)} and {len(FOCI)}."
    )

rows = []
for line, focus in zip(source_rows, FOCI):
    title_year, country_org, _old_scope, tools = split_unescaped_ampersands(line)
    if ";" not in country_org:
        raise RuntimeError(f"Cannot separate region and organization: {country_org}")
    region, organization = [part.strip() for part in country_org.split(";", 1)]
    if region == "Australia":
        region = "Australia/New Zealand"
    tools = tools.replace(
        "No relevant full-name scale verified", "No eligible named tool verified"
    )
    guideline = rf"{compact_spaces(title_year)}; {compact_spaces(organization)}"
    rows.append(
        " & ".join(
            [
                compact_spaces(region),
                guideline,
                compact_spaces(focus),
                compact_spaces(tools),
            ]
        )
        + r" \\"
    )

row_block = "\n".join(rows)

output = rf"""% Condensed Supplementary Table S1: complete 32-guideline set.
% Generated from Supplementary_Table_S1_Guidelines_Compact.tex.
% Required packages: booktabs, longtable, array, ragged2e, pdflscape.

\begin{{landscape}}
\clearpage
\begingroup
\renewcommand{{\tablename}}{{Supplementary Table}}
\renewcommand{{\thetable}}{{S1}}
\setlength{{\tabcolsep}}{{2pt}}
\setlength{{\LTpre}}{{0pt}}
\setlength{{\LTpost}}{{0pt}}
\renewcommand{{\arraystretch}}{{1.02}}
\scriptsize
\begin{{longtable}}{{@{{}}
>{{\RaggedRight\arraybackslash}}p{{2.25cm}}
>{{\RaggedRight\arraybackslash}}p{{8.05cm}}
>{{\RaggedRight\arraybackslash}}p{{5.30cm}}
>{{\RaggedRight\arraybackslash}}p{{8.10cm}}
@{{}}}}
\caption{{Included stroke guideline documents by region, clinical focus, and representative assessment tools.}}
\label{{tab:s1_guidelines_compact}}\\
\toprule
\textbf{{Region}} & \textbf{{Guideline, year and organization}} & \textbf{{Clinical focus}} & \textbf{{Representative tools}} \\
\midrule
\endfirsthead
\multicolumn{{4}}{{l}}{{\textit{{Supplementary Table S1 continued}}}}\\
\toprule
\textbf{{Region}} & \textbf{{Guideline, year and organization}} & \textbf{{Clinical focus}} & \textbf{{Representative tools}} \\
\midrule
\endhead
\midrule
\multicolumn{{4}}{{r}}{{\textit{{Continued on the next page}}}}\\
\endfoot
\bottomrule
\endlastfoot
{row_block}
\end{{longtable}}
\noindent\scriptsize\textit{{Notes.}} Clinical focus is a concise paraphrase of guideline scope. Representative tools are named measures relevant to stroke severity, motor impairment, balance, mobility or function; tool abbreviations are expanded in Supplementary Table S2a. ``No eligible named tool verified'' means that no eligible standardized assessment tool was confirmed in the locally available document, not that the guideline contains no assessment recommendations. ACSQHC, Australian Commission on Safety and Quality in Health Care; ADL, activities of daily living; AFO, ankle-foot orthosis; AHA/ASA, American Heart Association/American Stroke Association; ANPT/APTA, Academy of Neurologic Physical Therapy/American Physical Therapy Association; aSAH, aneurysmal subarachnoid haemorrhage; CMA, Chinese Medical Association; CSBPR, Canadian Stroke Best Practice Recommendations; EAN/EFNS, European Academy of Neurology/European Federation of Neurorehabilitation Societies; ESO, European Stroke Organisation; EVT, endovascular therapy; FES, functional electrical stimulation; ICH, intracerebral haemorrhage; JSS, Japan Stroke Society; NICE, National Institute for Health and Care Excellence; SAH, subarachnoid haemorrhage; TIA, transient ischaemic attack; VA/DoD, U.S. Department of Veterans Affairs/U.S. Department of Defense.
\endgroup
\end{{landscape}}
"""

OUTPUT.write_text(output, encoding="utf-8")
print(OUTPUT)
