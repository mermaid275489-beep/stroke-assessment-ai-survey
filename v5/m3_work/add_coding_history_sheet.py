"""Add the Coding_history sheet (per-entry availability codes at each stage) to Supplementary Data 1."""
import openpyxl
import pandas as pd
from openpyxl.styles import Font, Alignment, PatternFill

V5 = r'D:\Stroke\v5'
REV = r'D:\Stroke\revision_2026-11-15'
H = pd.read_csv(V5 + r'\m3_work\coding_history.csv', keep_default_na=False)
c2 = pd.read_csv(REV + r'\entries_r2_changes.csv', keep_default_na=False)
c2 = c2[c2.field == 'Video availability']
r2 = pd.read_csv(REV + r'\entries_r2.csv', keep_default_na=False, dtype=str)
idk = dict(zip(zip(r2.Tool, r2['Item / task']), r2['Entry ID']))
RULE = {'R1': 'R1: grades defined by observable motor events -> Full',
        'R2': 'R2: grades defined by examiner supervision, assistance, cueing or safety -> Partial',
        'R3': 'R3: examiner resistance, passive movement or palpation -> Partial or None',
        'R4': 'R4: patient-reported score -> None'}
why = {}
for t, k, rule in zip(c2.tool, c2.task, c2.rule):
    e = idk.get((t, k))
    if e:
        why[e] = RULE[rule[:2]]

p3 = pd.read_excel(V5 + r'\Supplementary Data 1.xlsx', 'Post_check_revisions', keep_default_na=False)
p3 = p3[(p3.Field == 'Video availability')]

out = []
for r in H.itertuples():
    checked = r.S1 != ''
    notes = []
    if checked and r.S3 != r.S5:
        notes.append('single-coder pass: ' + why.get(r._1, 'harmonisation of codes across tools'))
    for rnd, e in zip(p3.Round, p3['Entry ID']):
        if e == r._1:
            notes.append(rnd.split(' (')[0].lower().replace('round', 'round') )
    out.append([r._1, r.Tool, r._3,
                'yes' if checked else 'no (added or redefined after the check)',
                r.S1 or '-', r.S2 or '-', r.S3 or '-', r.S5, r.S6, '; '.join(notes)])

wb = openpyxl.load_workbook(V5 + r'\Supplementary Data 1.xlsx')
if 'Coding_history' in wb.sheetnames:
    del wb['Coding_history']
ws = wb.create_sheet('Coding_history', index=wb.sheetnames.index('Second_reviewer_check') + 1)
hdr = ['Entry ID', 'Tool', 'Item / task', 'Independently double coded',
       '1 First reviewer (initial)', '2 Second reviewer (independent)', '3 After consensus',
       '4 Before rule revision', '5 Final (revised rule)', 'Changes after consensus']
ws.append(hdr)
for row in out:
    ws.append(row)
ws.append([])

def cnt(col):
    s = [r[col] for r in out if r[col] != '-']
    return 'Full %d, Partial %d, None %d (n = %d)' % (s.count('Full'), s.count('Partial'), s.count('None'), len(s))

summary = [
    ['Summary', 'Stage 1-3 counts refer to the 193 records double coded before the entry set was finalised; '
     '181 of them map to a final entry with the same definition (listed above), 12 were excluded, split or redefined.'],
    ['1 First reviewer (initial)', 'Full 82, Partial 82, None 29 (n = 193)'],
    ['2 Second reviewer (independent)', 'Full 125, Partial 43, None 25 (n = 193); agreement 149/193 (77.2%), '
     "Cohen's kappa 0.63, linear-weighted kappa 0.68"],
    ['3 After consensus', 'Full 115, Partial 53, None 25 (n = 193); 34 records recoded'],
    ['4 Before rule revision', cnt(7) + '; 15 entries added or redefined; 54 of the 181 checked entries changed code '
     'since consensus in single-coder passes that applied written rules R1-R4 across tools and in the round-3 check '
     '(3 entries)'],
    ['5 Final (revised rule)', cnt(8) + '; 36 codes changed by one coder under the revised rule; '
     '129 of the 181 checked entries retain their consensus code'],
]
for s in summary:
    ws.append(s)

bold = Font(bold=True)
for c in ws[1]:
    c.font = bold
    c.fill = PatternFill('solid', fgColor='DDEBF7')
    c.alignment = Alignment(wrap_text=True, vertical='top')
for r in ws.iter_rows(min_row=len(out) + 3):
    r[0].font = bold
widths = [9, 34, 40, 18, 14, 14, 14, 14, 14, 60]
for i, w in enumerate(widths):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i + 1)].width = w
ws.freeze_panes = 'D2'

wm = wb['README']
last = wm.max_row
names = [wm.cell(r, 1).value for r in range(1, last + 1)]
if 'Coding_history' not in names:
    i = names.index('Second_reviewer_check') + 2
    wm.insert_rows(i)
    wm.cell(i, 1, 'Coding_history')
    wm.cell(i, 2, 'Availability code of every entry at each coding stage: first reviewer, second reviewer (independent), '
                  'after consensus, before the rule revision (after single-coder harmonisation with written rules R1-R4 '
                  'and the round-3 check) and final, with stage totals.')
    for j in (1, 2):
        s = wm.cell(i - 1, j); c = wm.cell(i, j)
        c.font = s.font.copy(); c.alignment = s.alignment.copy()
for r in range(1, wm.max_row + 1):
    if wm.cell(r, 1).value == 'Post_check_revisions':
        wm.cell(r, 2).value = wm.cell(r, 2).value.replace(
            'All changes made after the second-reviewer check:',
            'Field-level changes with sources made after the second-reviewer check (the earlier single-coder harmonisation '
            'pass is traced entry by entry in Coding_history):')
wb.save(V5 + r'\Supplementary Data 1.xlsx')
print('rows', len(out)); [print(s) for s in summary]
