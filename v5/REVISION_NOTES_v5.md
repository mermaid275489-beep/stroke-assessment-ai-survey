# v5 revision notes (response to the round-5 peer review)

Base: v4 Overleaf package (`overleaf_upload_v4_2026-11-16`), copied 2026-11-20.

## Decisions
- M1 (repositioning; rewrite title, abstract and introduction): skipped. Abstract and Introduction are frozen (advisor's text).
- M2: wording corrected to independent coding (see M2 section); other M2 requests not done.
- M3 (circularity of Full; observable vs computable): done in this round.

## M3: computability coding

New attribute (v), *computability of the visible score-defining criteria*, coded for all 196 entries
(`m3_work/computability_codes.py`; one rationale per entry).

Rule: each entry takes the code of its least computable visible grade boundary.
- **Direct**: every visible boundary is a time, distance, count, angle or displacement threshold, or a discrete visible event
  (completion, a step, contact, use of the hands, an aid or physical help, a fall).
- **Proxy**: at least one boundary is a rated degree of a named observable property without a stated threshold
  (steadiness or sway, path deviation, change in speed, symmetry, smoothness, a listed compensation, supervision shown by
  visible instability).
- **Judgement**: at least one boundary is an overall clinical judgement that names no single observable property (normal vs
  abnormal movement or gait pattern, comparison with the unaffected side, clumsiness, recovery stage, safety concern,
  global disability).
- Partial entries are coded on their visible part only. None entries are not applicable.

### Results (`m3_work/analyse_computability.py`)

| Availability | Direct | Proxy | Judgement | n/a | Total |
|---|---|---|---|---|---|
| Full | 61 | 57 | 16 | 0 | 134 |
| Partial (visible part) | 21 | 9 | 6 | 0 | 36 |
| None | 0 | 0 | 0 | 26 | 26 |

- Of the Full entries: 46% Direct, 43% Proxy, 12% Judgement.
- The 104 entries that are Full by construction split into 49 Direct, 44 Proxy and 11 Judgement.
- 61/196 entries (31%; 34.5% tool-weighted) are both Full and Direct. They come from 27 tools, and in 16 tools every entry is
  Full and Direct.
- The 73 Full entries coded Proxy or Judgement outnumber the 62 Partial and None entries combined.

### Files changed
- `main.tex`
  - 3.1 Coded attributes: "Four" changed to "Five"; new definition (v) added.
  - 3.1 Verification: computability added to the attributes assigned by one coder.
  - 4.1: new results paragraph ("Visibility does not imply computability..."); a pointer added after the Full-by-construction
    sentence.
  - Limitations 3 and 4: computability added.
  - Conclusion: one sentence added.
  - Data Availability: computability codes mentioned.
  - Abstract and Introduction verified unchanged.
- `Table2.tex`: one sentence added to the notes pointing to S2b.
- `Supplementary Table S2.tex`: S2b gains a "Computability D/P/J" column, a caption update and a definition in the notes.
  F/P/N counts were re-verified against the workbook.
- `Supplementary Data 1.xlsx`
  - Mapping_entries: two new columns (code and rationale).
  - Coding_rules: new "Computability" row.
  - README: updated.
- Backups of the pre-M3 files are in `m3_work/*_before_m3.*`.

### To verify
- The codes are a single-coder draft. Boundary calls worth checking first:
  - ARAT coded Proxy, not Judgement.
  - FMA-UE synergy subscale coded Proxy because of its compensation clauses.
  - DGI/FGA level-walking items coded Judgement ("normal gait pattern").
  - BBS supervision items coded Proxy.
  - NIHSS ataxia coded Judgement.
  - SIAS trunk verticality coded Direct (15-degree record-sheet threshold).
- Not compiled locally (no TeX installation); a static lint passed (braces balanced, all `\ref` resolve, 57 S2b rows of
  12 cells). S2b is now about 14.6 cm wide against a 16.5 cm text width.
- Figure 3 is not changed. The computability split is reported in text and in S2b only.

## M2: description of the availability check (wording only)
User confirmed (2026-11-20) that the two reviewers coded availability independently; the earlier text
("with the first reviewer's codes visible") was inaccurate. Changed:
- main.tex 3.1 Verification: "Two reviewers independently coded the availability of the initial 193 entries ...";
  disagreements "resolved by consensus against the scoring manuals, which recoded 34 entries".
- main.tex Limitations (third): "The availability check was not blinded" -> "Independent double coding covered only
  availability in the initial coding".
- Supplementary Data 1, README (Second_reviewer_check row): "the reviewer saw the initial codes" -> "which the two
  reviewers coded independently"; resolution "by consensus".
Not done (other M2 requests): new double coding under the final rule, PABAK/CI, old-vs-new-rule sensitivity analysis,
22 boundary entries as Full/Partial bounds, coder backgrounds.

## Section III numerical issues
1. COA counts: no change needed. The v4 package already gives 16 PerfO / 33 ClinRO / 6 PRO / 2 mixed in the text, in
   Figure 2 and in S2a (mEFAP = PerfO). The reviewer's 15/34 came from an older PDF.
2. Coding history: the v4 text ("178 checked entries that were unchanged, three recoded later") was wrong. Rebuilt with
   `m3_work/coding_history.py`:
   - Stage 1: initial codes, 193 records: F82/P82/N29.
   - Stage 2: second reviewer, independent: F125/P43/N25.
   - Stage 3: after consensus, 34 recoded: F115/P53/N25.
   - Stage 4: before the rule revision, 196 entries: F106/P62/N28. This comprises 181 checked entries (54 changed code
     since consensus in single-coder passes applying rules R1-R4, plus 3 in the round-3 check) and 15 new or redefined
     entries. 12 checked records were excluded, split or redefined.
   - Final: F134/P36/N26 (36 changed). 129 of the 181 checked entries keep their consensus code.
   - Changes: new sheet `Coding_history` in Supplementary Data 1 (per-entry codes at every stage, plus a summary);
     Verification paragraph rewritten as three stages; Limitations (third) now names the 54 single-coder changes; README
     and the `Post_check_revisions` description updated.
3. Supplementary sources: new sheet `Source_crosstab` (main reason x source) and a "Main reason not fully available"
   column in `Mapping_entries`. Limitations (fourth) explains the overlap (audio is needed for 22 entries but is the main
   reason in 8). Totals reproduce 26/22/22/16/11/6.
4. Section 5.4: "sensation, pain and patient-reported difficulty (20 entries)" changed to "patient-reported content (20
   entries), sensation and pain (examination items outside the mapped motor content)".
5. Figure 1 vs Table 2: not changed. Figure 1 sits in the frozen Introduction and is the advisor's figure; raise with the
   advisor.
6. Figure 3d: S2a gains a Domain column (UL/TB/GM/IG, from the Figure 3d grouping; 13/13/16/15 tools); the Fig. 3
   caption points to it. FMA-LE is in Gait and mobility, so the NIHSS selection is correct; the top-5 lists match the
   final data (BI, SIAS and STREAM tie at 3 entries).
7. Table order: the two early citations of Table 2 (Background, Coded attributes) now cite Section 4 instead, so Table 1 is
   cited first.
8. Dates: biblatex option `urldate=iso` added (prints YYYY-MM-DD). The search date (May 2026) vs reference [3] and the
   July-August access dates were NOT changed; this needs the authors' facts (was there an update search?).

### Item 8 follow-up: search date (2026-11-20)
- The authors confirm that no update search was run after May 2026.
- PubMed shows the AHA/ASA 2026 acute ischaemic stroke guideline (PMID 41582814) was published online on 2026-01-26,
  i.e. before the search date; Stroke 57(8) is its later print issue.
- Access dates (July-August 2026) belong to web scoring manuals and specifications used for coding and verification.
- Tool library paragraph now says the searches were not updated, that online-first documents are cited in their print
  versions, and that web sources were accessed until August 2026.
- Cao 2026 (Bioengineering 13(10)) is cited only in the Discussion as illustration, outside the search.

## M4: definition of "ordinary video" (sensitivity analysis)
Script `m3_work/recording_scenarios.py`; new sheet `Recording_scenarios` in Supplementary Data 1 (per-entry codes, reasons
and totals). Single-coder judgement from the scoring criteria and the recording requirements, not tested on recordings.

| Scenario | Full | Partial | None | Full % (entry / tool-weighted) |
|---|---|---|---|---|
| Base (RGB, no audio) | 134 | 36 | 26 | 68 / 53 |
| A: RGB + audio | 139 | 31 | 26 | 71 / 54 |
| B: routine single viewpoint per task | 104 | 66 | 26 | 53 / 34 |
| A + B | 109 | 61 | 26 | 56 / 35 |

- A: only the 5 Partial entries whose sole missing source is audio become Full (E005, E011, E028, E033, E160). The other 17
  entries that need audio also need the examiner's record, interview or daily-life records.
- B: 30 Full entries from 17 tools are lowered to Partial.
  - 14 need a hand close-up (ARAT grasp/grip/pinch, 9HPT, JTHFT, MFT grasp/pinch/peg-board, MoAS hand items, FAT, SULCS,
    SIAS motor, STREAM upper limb).
  - 7 need a legible ruler or calibration (BBS reach and retrieve, TIS 10-cm displacement, FRT, BBA sitting and standing
    reach, EMS reach).
  - 7 need two simultaneous views (FGA items with lane-deviation thresholds; MoAS sit-to-stand).
  - 2 have a course longer than one field of view (2MWT, 6MWT).
  - By computability: 15 Direct, 9 Proxy, 6 Judgement. Full-and-Direct entries fall from 61 to 46.
- Text changes:
  - 3.1 (iii): a sentence introducing the sensitivity analysis.
  - 4.1: a new results paragraph.
  - Limitations (fourth): the scenario result and the need for a calibration study (BBS, TIS) added; the closing sentence
    now reads "RGB video without audio".
- Not done: the pilot on real recordings, which needs data and ethics approval; it is named as future work in the
  Limitations.

## M5: tool-library construction (text only)
Checked against the source files: `candidate_supplementary_tools*.csv`, `Guideline Summary.xlsx` (presence matrix) and the
`Guideline_fulltext_log`.
- 3.1 Tool library:
  - Extraction rule stated: full-name presence, confirmed by reading the passage; named tools were included even when not
    formally recommended, and recommendation strength was not graded. Source: `Guideline_x_Tool_matrix`, "verified
    presence matrix".
  - Supplementary stream: 22 retained after checking 58 source reports, by relevance (FULL / PARTIAL / UPPER LIMB
    grades) and a verifiable scoring specification. Reasons for the 162 non-retained leads were never recorded (no log
    exists); this is now said openly.
  - MTS described as an exception to the language rule.
- Limitations (first):
  - Regional distribution of the 28 guidelines (US 8, Canada 6, UK 3, AU/NZ 3, Europe 2, Korea 2, HK 2, Singapore 1,
    mainland China 1); none from Latin America, Africa or South Asia.
  - Asymmetry: Japanese and Chinese guidelines without English texts were excluded, while the Japanese tools SIAS, MFT and
    ABMS II entered through the supplementary stream.
  - Missing tools:
    - PASS: in the 184 supported candidates ("Postural Assessment Scale for Stroke patients", multicentre) but not
      retained; no reason recorded.
    - RMA: never identified.
    - FMA balance: identified ("Fugl-Meyer balance scale") but outside the FMA motor scores mapped.
- Not done:
  - Per-reason counts for the 162 leads; they would have to be classified retrospectively.
  - OSF retrospective registration (an author action).
  - PRISMA-ScR checklist; the paper is positioned as a methods survey and M1 was skipped.
  - Adding PASS to the library.

## M6: COA classification under two readings
- The operational split is kept: 16 PerfO / 33 ClinRO / 6 PRO / 2 mixed.
- A task-based reading of the same BEST/ISPOR definitions is added: a standardized task performed on instruction and
  graded from that performance counts as PerfO whoever scores it. Result: 34 PerfO / 16 ClinRO / 6 PRO / 1 mixed (RMI).
  - Change class: ARAT, BBS, CAHAI, CB&M, DGI, EMS, FIST, FGA, Mini-BESTest, POMA, TCT, TIS, ABMS II, FMA-LE, FMA-UE,
    MoAS and STREAM move from ClinRO to PerfO; WMFT moves from mixed to PerfO.
  - Stay ClinRO under both readings: examiner force/touch, tone/reflex, stage, global status or usual performance (BI,
    BRS, CMSA, CSI, FAC, FIM, MRC, MAS, mRS, MTS, MI, NIHSS, SCP, SAFE, SIAS, AM-PAC).
- Files:
  - S2a: "[task-based: PerfO]" added to the COA cell of the 18 tools, plus a note.
  - main.tex 3.1 COA paragraph: three sentences added, including the reason for keeping the operational split.
  - Table 1: notes updated.
  - Supplementary Data 1: `Coding_rules` COA row extended.
- No new references; the existing BEST and Walton/ISPOR citations are used. Borderline calls to check: FMA (motor items
  are tasks on instruction, a few graded against resistance) and FAC (kept ClinRO as a clinician category).

## Figure 1 (user's revised BioRender figure, 2026-11-21)
Source: `Downloads/Figure1_intended_uses_revised.pptx`, copied to `figure1_work/Figure1_original.pptx`. Edited copy:
`figure1_work/Figure1_revised.pptx`, made by `revise_figure1.py`. The illustrations are untouched.
- Changes:
  - The five family labels now use the Table 2 names: Temporal & Event; Spatial & Trajectory; Joint & Segment Kinematics;
    Inter-segment & Relational; Trajectory-derived Quality. This answers review item 5.
  - New label under the patient: "Not captured by motion features: amount of assistance, verbal cues, applied force,
    tone and self-report". This mirrors the last row of Table 2.
  - The column-4 heading is aligned with the other three headings; "Criterion Scoring" is bold like the other use labels.
  - The "S" trajectory marker was moved off the family label.
  - The BioRender advertisement slide was removed.
- `figure1_work/figure1.pdf`: cropped to 1.636:1 so that the frozen `\includegraphics[width=0.9\linewidth,
  height=0.55\linewidth]` does not stretch it (the full slide is 1.43:1). Upload it to Overleaf as figure1.pdf. It is
  not in the v5 zip; neither the v4 nor the v5 package contained figure1.pdf.
- BioRender artwork needs a publication licence from the BioRender account holder before journal submission.
- Figure 1 caption rewritten at the user's request (2026-11-21). This is the one exception to the frozen Introduction:
  the caption now describes the four columns, the five families (pointing to Section 4), direct vs indicator features,
  the information motion features do not capture, the validation levels and the illustrative elements. "Component-level"
  is kept so the caption matches the frozen introduction text. The BioRender credit line ("Created in BioRender. ...
  https://BioRender.com/...") still has to be added from the licence.

## Figure 3 (user's repaired curved-flow version, 2026-11-21)
Source: `Downloads/Figure3_repaired_curved_flows.pptx`, copied to `figure3_work/Figure3_original.pptx`.
- Data check against the final entries:
  - a: 104/55/17/20 -> Full 134, Partial 36, None 26; the 55-entry group splits 30 Full / 25 Partial.
  - b: entry-weighted 68/18/13; tool-weighted 53/29/18.
  - c: 153/42, 81/24, 52/21, 46/19, 6/6.
  - d: every tool's F/P/N squares and totals match S2b.
  - All correct.
- Fixes (`revise_figure3.py`; layout and data untouched):
  - Missing space added in "information (n = 55)".
  - Two labels that were wider than their boxes now have wider boxes.
  - The panel-d note now reads "The five tools with the most entries in each domain are shown."
  - The BioRender advertisement slide was removed.
- `v5/figure3.pdf` replaced by the cropped export of `Figure3_revised.pptx`; the previous file is kept as
  `figure3_work/figure3_v5_before.pdf`.
- Caption, panel a: the order in which an entry with several information types is assigned to one group is now stated
  (review minor comment 6).

## Readability rewrite merged (2026-11-21)
`main.tex` was replaced by the Codex readability rewrite (`main_readability_revised.tex`). The previous file is kept as
`m3_work/main_before_readability_merge.tex`.
- Checked identical: preamble, abstract, introduction (including the new Figure 1 caption), citation keys, `\ref`,
  `\label`, `\input`, and every number in the body.
- Body: 6057 -> 5538 words.
- The user chose to keep the rewrite's Figure 3 caption, so the panel-a priority sentence added earlier today is not in
  the caption for now.
