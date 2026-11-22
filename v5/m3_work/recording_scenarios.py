"""M4: sensitivity of video availability to the definition of 'ordinary video'.

Base    one RGB camera framing each task as administered, no audio, adequate recording (manuscript definition).
A       RGB + audio: Partial entries whose only missing information is audible (listed source = audio only) -> Full.
B       routine single-viewpoint recording: one camera and one viewpoint per task at whole-body (or upper-body) distance,
        standard frame rate, no hand close-up, no added calibration reference, no second simultaneous view.
        A Full entry becomes Partial when its grade needs what such a recording lacks (reason codes below).
A+B     both.
Codes are a single-coder judgement from the entry's scoring criteria and recording requirements (Supplementary Data 1).
"""
import openpyxl
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment

X = r'D:\Stroke\v5\Supplementary Data 1.xlsx'
REASON = {
    'scale': 'Metric distance read against a ruler or calibration reference that is not legible at whole-body distance',
    'hand': 'Grade depends on finger or grasp detail that needs a hand close-up',
    'views': 'Grade combines lateral deviation or frontal-plane symmetry with sagittal timing or extension, needing two simultaneous views',
    'course': 'Walking course longer than one fixed field of view (distance of the final partial lap)',
}
B = {
    # distance or scale reference
    'E008': 'scale', 'E009': 'scale', 'E041': 'scale', 'E133': 'scale', 'E155': 'scale', 'E156': 'scale', 'E164': 'scale',
    # hand close-up
    'E069': 'hand', 'E078': 'hand', 'E079': 'hand', 'E081': 'hand', 'E082': 'hand', 'E083': 'hand', 'E089': 'hand',
    'E168': 'hand', 'E169': 'hand', 'E174': 'hand', 'E175': 'hand', 'E177': 'hand', 'E178': 'hand', 'E180': 'hand',
    # two simultaneous views
    'E029': 'views', 'E030': 'views', 'E031': 'views', 'E032': 'views', 'E036': 'views', 'E037': 'views', 'E075': 'views',
    # long course
    'E057': 'course', 'E150': 'course',
}

d = pd.read_excel(X, 'Mapping_entries', keep_default_na=False)
base = dict(zip(d['Entry ID'], d['Video availability']))
src = dict(zip(d['Entry ID'], d['Supplementary source']))
for e in B:
    assert base[e] == 'Full', e
audio_only = [e for e in base if base[e] == 'Partial' and src[e].strip() == 'audio recording']

rows = []
for e in d['Entry ID']:
    a = 'Full' if e in audio_only else base[e]
    b = 'Partial' if e in B else base[e]
    ab = 'Partial' if e in B else a
    why = []
    if e in audio_only:
        why.append('A: missing information is verbal only (audio resolves it)')
    if e in B:
        why.append('B: ' + REASON[B[e]])
    rows.append((e, base[e], a, b, ab, '; '.join(why)))
S = pd.DataFrame(rows, columns=['Entry ID', 'Base', 'A RGB+audio', 'B Routine single view', 'A+B', 'Reason'])
S = S.merge(d[['Entry ID', 'Tool', 'Item / task']], on='Entry ID')

def cnt(col):
    v = S[col].value_counts()
    return v.get('Full', 0), v.get('Partial', 0), v.get('None', 0)

summary = {c: cnt(c) for c in ['Base', 'A RGB+audio', 'B Routine single view', 'A+B']}
for k, v in summary.items():
    print(k, 'F%d/P%d/N%d' % v, 'Full %.0f%%' % (100 * v[0] / 196))
print('audio-only:', audio_only)
print('B by reason:', pd.Series(B).value_counts().to_dict(), 'tools', S[S['Entry ID'].isin(B)].Tool.nunique())
# tool-weighted Full share
for c in ['Base', 'A RGB+audio', 'B Routine single view', 'A+B']:
    print(c, 'tool-weighted Full %.1f' % (100 * S.assign(f=S[c] == 'Full').groupby('Tool').f.mean().mean()))
# computability of downgraded entries
import sys
sys.path.insert(0, r'D:\Stroke\v5\m3_work')
from computability_codes import CODES
print('B downgrades by computability:', pd.Series([CODES[e][0] for e in B]).value_counts().to_dict())
fd_lost = [e for e in B if CODES[e][0] == 'D']
print('Full&Direct under B:', sum(1 for e in base if base[e] == 'Full' and CODES[e][0] == 'D' and e not in B))

wb = openpyxl.load_workbook(X)
if 'Recording_scenarios' in wb.sheetnames:
    del wb['Recording_scenarios']
ws = wb.create_sheet('Recording_scenarios', index=wb.sheetnames.index('Mapping_entries') + 1)
cols = ['Entry ID', 'Tool', 'Item / task', 'Base', 'A RGB+audio', 'B Routine single view', 'A+B', 'Reason']
ws.append(cols)
for r in S[cols].itertuples(index=False):
    ws.append(list(r))
ws.append([])
ws.append(['Scenario', 'Definition', '', 'Full', 'Partial', 'None'])
DEF = {'Base': 'One RGB camera framing each task as administered, no audio, adequate recording (manuscript definition)',
       'A RGB+audio': 'Base plus an audio track; Partial entries whose only missing information is verbal become Full',
       'B Routine single view': 'One camera and one viewpoint per task at whole-body distance, standard frame rate, no hand close-up, no added calibration reference, no second simultaneous view',
       'A+B': 'Routine single-view recording with audio'}
for k, v in summary.items():
    ws.append([k, DEF[k], ''] + [int(x) for x in v])
ws.append(['Note', 'Single-coder sensitivity analysis from written criteria and the recording requirements in Mapping_entries; not tested on recordings.'])
for c in ws[1]:
    c.font = Font(bold=True); c.fill = PatternFill('solid', fgColor='DDEBF7'); c.alignment = Alignment(wrap_text=True, vertical='top')
for i, w in enumerate([9, 32, 40, 10, 12, 14, 10, 70]):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i + 1)].width = w
ws.freeze_panes = 'D2'
wr = wb['README']
names = [wr.cell(r, 1).value for r in range(1, wr.max_row + 1)]
if 'Recording_scenarios' not in names:
    i = names.index('Mapping_entries') + 2
    wr.insert_rows(i)
    wr.cell(i, 1, 'Recording_scenarios')
    wr.cell(i, 2, 'Sensitivity of video availability to the recording definition: base (RGB only), A (RGB plus audio), '
                  'B (routine single-viewpoint recording) and A+B, per entry with reasons and totals.')
wb.save(X)
