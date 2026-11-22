"""M3: add the computability code to Supplementary Table S2b and Supplementary Data 1 (v5)."""
import re
import sys
import shutil
import openpyxl
from openpyxl.styles import Alignment
from copy import copy
import pandas as pd

sys.path.insert(0, r'D:\Stroke\v5\m3_work')
from computability_codes import CODES

V5 = r'D:\Stroke\v5'
XLSX = V5 + r'\Supplementary Data 1.xlsx'
S2 = V5 + r'\Supplementary Table S2.tex'

ORDER = ['10-Metre Walk Test', '2-Minute Walk Test (2MWT)', '6-Minute Walk Test', 'Action Research Arm Test (ARAT)',
         'Berg Balance Scale (BBS)', 'Box and Block Test (BBT)', 'Brunel Balance Assessment (BBA)',
         'Chedoke Arm and Hand Activity Inventory (CAHAI)', 'Community Balance & Mobility Scale (CB&M)',
         'Dynamic Gait Index', 'Elderly Mobility Scale (EMS)', 'Five Times Sit-to-Stand', 'Frenchay Arm Test (FAT)',
         'Function In Sitting Test (FIST)', 'Functional Gait Assessment', 'Functional Reach Test (FRT)',
         'Jebsen-Taylor Hand Function Test (JTHFT)', 'Manual Function Test (MFT)', 'Mini-BESTest',
         'Modified Emory Functional Ambulation Profile', 'Nine-Hole Peg Test (9HPT)',
         'Short Physical Performance Battery (SPPB)', 'Six-Spot Step Test (SSST)',
         'Stroke Upper Limb Capacity Scale (SULCS)', 'Timed Up and Go', 'Tinetti / POMA', 'Trunk Control Test (TCT)',
         'Trunk Impairment Scale (TIS, Verheyden)', 'Wolf Motor Function Test (WMFT)',
         'Ability for Basic Movement Scale II (ABMS II)', 'Barthel Index', 'Brunnstrom Recovery Stages',
         'Chedoke-McMaster Stroke Assessment', 'Composite Spasticity Index (CSI)', 'Fugl-Meyer LE (FMA-LE)',
         'Fugl-Meyer UE (FMA-UE)', 'Functional Ambulation Category (FAC)', 'Functional Independence Measure (FIM)',
         'Medical Research Council (MRC) muscle scale', 'Modified Ashworth Scale', 'modified Rankin Scale (mRS)',
         'Modified Tardieu Scale', 'Motor Assessment Scale (MAS)', 'Motricity Index', 'NIH Stroke Scale (NIHSS)',
         'Scale for Contraversive Pushing (SCP)', 'Shoulder Abduction Finger Extension (SAFE) score', 'STREAM',
         'Stroke Impairment Assessment Set (SIAS)', 'ABILHAND', 'Activities-specific Balance Confidence (ABC)',
         'Activity Measure for Post-Acute Care (AM-PAC)', 'Falls Efficacy Scale (FES)',
         'Falls Efficacy Scale-International (FES-I)', 'Motor Activity Log (MAL)', 'Stroke Impact Scale (SIS)',
         'Rivermead Mobility Index (RMI)']
LABEL = {'D': 'Direct', 'P': 'Proxy', 'J': 'Judgement', 'NA': 'Not applicable'}

d = pd.read_excel(XLSX, 'Mapping_entries', keep_default_na=False)
assert len(ORDER) == 57 and set(ORDER) == set(d.Tool)
d['C'] = d['Entry ID'].map(lambda e: CODES[e][0])

# ---------- S2b ----------
tex = open(S2, encoding='utf-8').read()
start = tex.index(r'\renewcommand{\thetable}{S2b}')
head, body = tex[:start], tex[start:]
assert 'Computability' not in body, 'already applied'

body = body.replace('*{7}{>{\\centering\\arraybackslash}p{0.75cm}}\n>{\\centering\\arraybackslash}p{1.9cm}\n@{}}',
                    '*{7}{>{\\centering\\arraybackslash}p{0.75cm}}\n>{\\centering\\arraybackslash}p{1.9cm}\n>{\\centering\\arraybackslash}p{1.9cm}\n@{}}', 1)
body = body.replace(r'\multirow{2}{*}{\shortstack{\textbf{Video}\\\textbf{F/P/N}}} \\',
                    r'\multirow{2}{*}{\shortstack{\textbf{Video}\\\textbf{F/P/N}}} &' + '\n' +
                    r'\multirow{2}{*}{\shortstack{\textbf{Computability}\\\textbf{D/P/J}}} \\', 1)
body = body.replace(r'& \textbf{Q/C} & \\', r'& \textbf{Q/C} & & \\', 1)
body = body.replace(r'\textbf{Q/C} & \textbf{Video} \\', r'\textbf{Q/C} & \textbf{Video} & \textbf{Comp.} \\', 1)
body = body.replace(r'\multicolumn{11}{', r'\multicolumn{12}{')
body = body.replace(r'\caption{Movement-component coverage and video availability of score-defining information for the 57 canonical post-stroke assessment tools.}',
                    r'\caption{Movement-component coverage, video availability and computability of score-defining information for the 57 canonical post-stroke assessment tools.}', 1)

def row_sub(m):
    i = int(m.group(1))
    tool = ORDER[i - 1]
    s = d[d.Tool == tool]
    fpn = 'F%d/P%d/N%d' % ((s['Video availability'] == 'Full').sum(), (s['Video availability'] == 'Partial').sum(),
                           (s['Video availability'] == 'None').sum())
    assert fpn == m.group(3), (i, tool, fpn, m.group(3))
    vis = s[s.C != 'NA']
    comp = '--' if vis.empty else 'D%d/P%d/J%d' % ((vis.C == 'D').sum(), (vis.C == 'P').sum(), (vis.C == 'J').sum())
    return m.group(0)[:-len(' \\\\')] + ' & ' + comp + ' \\\\'

body, n = re.subn(r'^(\d+) & (.+?) & (F\d+/P\d+/N\d+) \\\\$', row_sub, body, flags=re.M)
assert n == 57, n

note_old = 'Counts refer to 196 mapping entries;'
note_new = ('Computability D/P/J classifies the visible score-defining criteria of each Full or Partial entry by the least computable '
            'grade boundary: D (direct), every visible boundary is a time, distance, count, angle or displacement threshold or a '
            'discrete visible event such as completion, a step, contact, hand or aid use, physical help or a fall; P (proxy), at '
            'least one boundary is a rated degree of a named observable property, such as steadiness, sway, path deviation, '
            'symmetry, smoothness or a listed compensation, so a feature can target the property but its grade thresholds must be '
            'validated against rater scores; J (judgement), at least one boundary is an overall clinical judgement that names no '
            'single observable property, such as a normal versus abnormal movement or gait pattern, recovery stage, clumsiness or '
            'global disability. For Partial entries the code applies only to the visible part; -- marks tools whose entries are '
            'all None. Counts refer to 196 mapping entries;')
assert note_old in body
body = body.replace(note_old, note_new, 1)
open(S2, 'w', encoding='utf-8').write(head + body)
print('S2b updated')

# ---------- Supplementary Data 1 ----------
wb = openpyxl.load_workbook(XLSX)
ws = wb['Mapping_entries']
hdr = [c.value for c in ws[1]]
assert 'Computability' not in hdr
ncol = ws.max_column
src_hdr = ws.cell(1, ncol)
for j, name in enumerate(['Computability of visible criteria', 'Computability rationale'], start=1):
    c = ws.cell(1, ncol + j, name)
    c.font = copy(src_hdr.font); c.fill = copy(src_hdr.fill); c.border = copy(src_hdr.border)
    c.alignment = copy(src_hdr.alignment)
    ws.column_dimensions[openpyxl.utils.get_column_letter(ncol + j)].width = 18 if j == 1 else 60
idcol = hdr.index('Entry ID') + 1
for r in range(2, ws.max_row + 1):
    e = ws.cell(r, idcol).value
    code, why = CODES[e]
    for j, v in enumerate([LABEL[code], why], start=1):
        c = ws.cell(r, ncol + j, v)
        s = ws.cell(r, ncol)
        c.font = copy(s.font); c.border = copy(s.border); c.alignment = copy(s.alignment)

wr = wb['Coding_rules']
last = wr.max_row
rule = ('Computability of the visible score-defining criteria (added in revision; coded by one coder). Each Full or Partial '
        'entry is classified by the least computable of its visible grade boundaries. Direct: every visible boundary is set by '
        'a time, distance, count, angle or displacement threshold, or by a discrete visible event (task completion or failure, '
        'number of attempts or steps, contact with a target or obstacle, foot placement, use of the hands, an aid, a rail or '
        'physical help, a fall). Proxy: at least one boundary is a rated degree of a named observable property without a '
        'stated threshold (steadiness or sway, path deviation, change in speed, symmetry, smoothness, control of descent, '
        'hesitancy, a listed compensation strategy, need for supervision shown by visible instability); a feature can target '
        'the property, but its grade thresholds must be learned from or validated against rater scores. Judgement: at least '
        'one boundary is an overall clinical judgement that names no single observable property (normal versus abnormal '
        'movement or gait pattern, comparison with the unaffected side, clumsiness, synergy dependence, recovery stage, '
        'safety concern, global disability). For Partial entries the code applies only to the visible part; None entries are '
        'not applicable. Availability and computability are independent: Full means the information is visible, Direct means '
        'a computed quantity reproduces the grade boundary.')
wr.cell(last + 1, 1, 'Computability')
wr.cell(last + 1, 2, rule)
for j in (1, 2):
    s = wr.cell(last, j); c = wr.cell(last + 1, j)
    c.font = copy(s.font); c.border = copy(s.border); c.alignment = copy(s.alignment)

wm = wb['README']
for r in range(1, wm.max_row + 1):
    if wm.cell(r, 1).value == 'Mapping_entries':
        v = wm.cell(r, 2).value
        if 'computability' not in v:
            wm.cell(r, 2).value = v.rstrip('.') + (', and the computability of the visible criteria (Direct, Proxy or '
                                                   'Judgement) with its rationale.')
wb.save(XLSX)
print('Supplementary Data 1 updated')
