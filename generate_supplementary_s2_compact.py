from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Supplementary_Table_S2_Assessment_Tool_Library.tex"
OUTPUT = ROOT / "Supplementary_Table_S2_Assessment_Tool_Library_Compact.tex"


def split_rows(text: str) -> list[list[list[str]]]:
    groups: list[list[list[str]]] = []
    current: list[list[str]] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not re.match(r"^\d+\s*&", line):
            continue

        row = re.sub(r"\s*\\\\\s*$", "", line)
        fields = [part.strip() for part in re.split(r"(?<!\\)&", row)]
        row_id = int(fields[0])
        if row_id == 1 and current:
            groups.append(current)
            current = []
        current.append(fields)

    if current:
        groups.append(current)
    return groups


def compact_text(value: str) -> str:
    value = value.replace(r"\allowbreak", "")
    value = value.replace(r"\newline", " ")
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\s*/\s*", "/", value)
    value = re.sub(r"\s*\+\s*", "+", value)
    value = re.sub(r"(?<=\d)-(?=\d)", "--", value)
    return value


def tool_label(full_name: str, abbreviation: str) -> str:
    full_name = compact_text(full_name)
    abbreviation = compact_text(abbreviation)
    plain_name = full_name.replace(r"\&", "&").lower()
    plain_abbreviation = abbreviation.replace(r"\&", "&").lower()
    if plain_abbreviation in plain_name:
        return full_name
    return rf"{full_name} ({abbreviation})"


def coa_mode(coa: str, mode: str) -> str:
    coa = compact_text(coa)
    mode = compact_text(mode)
    replacements = {
        "Performance": "performance",
        "Clinician-rated": "clinician",
        "Observation/interview": "observation/interview",
        "Self-report (Rasch questionnaire)": "self-report",
        "Self-report": "self-report",
        "Self-report (interview)": "self-report",
        "Self-report/performance (difficulty)": "self-report/performance",
        "Self-report/observation": "self-report/observation",
        "Clinician-rated (MRC)": "clinician (MRC)",
    }
    return f"{coa}; {replacements.get(mode, mode)}"


def source_code(evidence: str, citations: str) -> str:
    evidence = compact_text(evidence)
    code = "G" if evidence == "Guideline" else "S"
    return rf"{code} {citations.strip()}"


def make_clinical_rows(identity_rows: list[list[str]], clinical_rows: list[list[str]]) -> list[str]:
    output: list[str] = []
    for identity, clinical in zip(identity_rows, clinical_rows, strict=True):
        if identity[0] != clinical[0]:
            raise ValueError(f"ID mismatch in S2a: {identity[0]} vs {clinical[0]}")

        row_id, full_name, abbreviation, coa, mode, construct = identity
        _, _, scoring, application, evidence, citations = clinical
        role = f"{compact_text(construct)}; {compact_text(application)}"
        output.append(
            " & ".join(
                [
                    row_id,
                    tool_label(full_name, abbreviation),
                    coa_mode(coa, mode),
                    role,
                    compact_text(scoring),
                    source_code(evidence, citations),
                ]
            )
            + r" \\"
        )
    return output


def make_bridge_rows(component_rows: list[list[str]], ai_rows: list[list[str]]) -> list[str]:
    output: list[str] = []
    for component, ai in zip(component_rows, ai_rows, strict=True):
        if component[0] != ai[0]:
            raise ValueError(f"ID mismatch in S2b: {component[0]} vs {ai[0]}")

        row_id, scale, scope, *marks = component
        _, ai_scale, video_code, ai_code, features = ai
        if compact_text(scale) != compact_text(ai_scale):
            raise ValueError(f"Scale mismatch for ID {row_id}: {scale} vs {ai_scale}")
        if len(marks) != 7:
            raise ValueError(f"Expected seven movement components for ID {row_id}")

        scope = compact_text(scope)
        features = compact_text(features)
        if scope != "Whole scale":
            features = rf"\textit{{{scope}:}} {features}"

        output.append(
            " & ".join(
                [row_id, compact_text(scale), *marks, compact_text(video_code), compact_text(ai_code), features]
            )
            + r" \\"
        )
    return output


def render(clinical_rows: list[str], bridge_rows: list[str]) -> str:
    clinical_block = "\n".join(clinical_rows)
    bridge_block = "\n".join(bridge_rows)
    return rf"""% Compact Supplementary Table S2a--b: complete 58-tool library.
% Generated from Supplementary_Table_S2_Assessment_Tool_Library.tex.
% Required packages: booktabs, longtable, array, ragged2e, pdflscape.

\begin{{landscape}}
\clearpage
\begingroup
\renewcommand{{\tablename}}{{Supplementary Table}}
\renewcommand{{\thetable}}{{S2a}}
\setlength{{\tabcolsep}}{{3pt}}
\setlength{{\LTpre}}{{0pt}}
\setlength{{\LTpost}}{{0pt}}
\renewcommand{{\arraystretch}}{{1.06}}
\scriptsize
\begin{{longtable}}{{@{{}}
>{{\centering\arraybackslash}}p{{0.50cm}}
>{{\RaggedRight\arraybackslash}}p{{4.40cm}}
>{{\RaggedRight\arraybackslash}}p{{2.25cm}}
>{{\RaggedRight\arraybackslash}}p{{5.90cm}}
>{{\RaggedRight\arraybackslash}}p{{4.60cm}}
>{{\RaggedRight\arraybackslash}}p{{3.55cm}}
@{{}}}}
\caption{{Canonical post-stroke assessment-tool library: clinical characteristics, scoring outputs, and evidence sources.}}
\label{{tab:supplementary_tool_library_clinical}}\\
\toprule
\textbf{{ID}} & \textbf{{Tool}} & \textbf{{COA / mode}} & \textbf{{Clinical construct and application}} & \textbf{{Scoring / output}} & \textbf{{Evidence / source}} \\
\midrule
\endfirsthead
\multicolumn{{6}}{{l}}{{\textit{{Supplementary Table S2a continued}}}}\\
\toprule
\textbf{{ID}} & \textbf{{Tool}} & \textbf{{COA / mode}} & \textbf{{Clinical construct and application}} & \textbf{{Scoring / output}} & \textbf{{Evidence / source}} \\
\midrule
\endhead
\midrule
\multicolumn{{6}}{{r}}{{\textit{{Continued on the next page}}}}\\
\endfoot
\bottomrule
\endlastfoot
{clinical_block}
\end{{longtable}}
\noindent\scriptsize\textit{{Notes.}} G, guideline evidence stream; S, supplementary clinical-literature stream. COA, clinical outcome assessment; ClinRO, clinician-reported outcome; PerfO, performance outcome; PRO, patient-reported outcome. Scoring ranges refer to the listed canonical form and may differ across modified versions. Evidence/source identifies the local evidence stream and key report used for extraction.
\endgroup

\clearpage
\begingroup
\renewcommand{{\tablename}}{{Supplementary Table}}
\renewcommand{{\thetable}}{{S2b}}
\setlength{{\tabcolsep}}{{2.2pt}}
\setlength{{\LTpre}}{{0pt}}
\setlength{{\LTpost}}{{0pt}}
\renewcommand{{\arraystretch}}{{1.06}}
\scriptsize
\newcommand{{\mcmark}}{{\(\bullet\)}}
\begin{{longtable}}{{@{{}}
>{{\centering\arraybackslash}}p{{0.48cm}}
>{{\RaggedRight\arraybackslash}}p{{1.75cm}}
*{{7}}{{>{{\centering\arraybackslash}}p{{0.55cm}}}}
>{{\centering\arraybackslash}}p{{1.55cm}}
>{{\centering\arraybackslash}}p{{1.55cm}}
>{{\RaggedRight\arraybackslash}}p{{10.60cm}}
@{{}}}}
\caption{{Canonical post-stroke assessment-tool library: movement-component coverage and AI-oriented video derivability.}}
\label{{tab:supplementary_tool_library_motion}}\\
\toprule
\multirow{{2}}{{*}}{{\textbf{{ID}}}} &
\multirow{{2}}{{*}}{{\textbf{{Scale}}}} &
\multicolumn{{7}}{{c}}{{\textbf{{Movement components}}}} &
\multirow{{2}}{{*}}{{\shortstack{{\textbf{{Video}}\\\textbf{{F/P/N}}}}}} &
\multirow{{2}}{{*}}{{\shortstack{{\textbf{{AI}}\\\textbf{{D/B/N}}}}}} &
\multirow{{2}}{{*}}{{\textbf{{Mapping scope and representative machine-observable features}}}} \\
\cmidrule(lr){{3-9}}
& & \textbf{{ROM}} & \textbf{{S/P}} & \textbf{{Coord.}} & \textbf{{Bal.}} & \textbf{{Dex.}} & \textbf{{Gait}} & \textbf{{Qual.}} & & & \\
\midrule
\endfirsthead
\multicolumn{{12}}{{l}}{{\textit{{Supplementary Table S2b continued}}}}\\
\toprule
\textbf{{ID}} & \textbf{{Scale}} & \textbf{{ROM}} & \textbf{{S/P}} & \textbf{{Coord.}} & \textbf{{Bal.}} & \textbf{{Dex.}} & \textbf{{Gait}} & \textbf{{Qual.}} & \textbf{{Video F/P/N}} & \textbf{{AI D/B/N}} & \textbf{{Mapping scope and representative features}} \\
\midrule
\endhead
\midrule
\multicolumn{{12}}{{r}}{{\textit{{Continued on the next page}}}}\\
\endfoot
\bottomrule
\endlastfoot
{bridge_block}
\end{{longtable}}
\noindent\scriptsize\textit{{Notes.}} Filled circles indicate scale-level coverage of score-defining movement components. ROM, range of motion; S/P, muscle strength and power; Coord., coordination and selective motor control; Bal., balance and postural control; Dex., manual dexterity; Gait, gait and mobility; Qual., movement quality and compensation. Video F/P/N denotes Full/Partial/None availability of score-defining information from video. AI D/B/N denotes directly derivable/bridge or proxy required/not derivable. Counts refer to the 193 mapped Bridge Matrix entries. The default mapping scope is the whole scale; italic prefixes identify restricted item or domain mappings.
\endgroup
\end{{landscape}}
"""


def main() -> None:
    groups = split_rows(SOURCE.read_text(encoding="utf-8"))
    if len(groups) != 4 or any(len(group) != 58 for group in groups):
        raise ValueError(f"Expected four 58-row source tables; found {[len(group) for group in groups]}")

    identity_rows, clinical_rows, component_rows, ai_rows = groups
    output = render(
        make_clinical_rows(identity_rows, clinical_rows),
        make_bridge_rows(component_rows, ai_rows),
    )
    OUTPUT.write_text(output, encoding="utf-8", newline="\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
