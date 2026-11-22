"""Cross-tabulate the main reason an entry is not fully available against the supplementary sources it needs."""
import openpyxl
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment

X = r'D:\Stroke\v5\Supplementary Data 1.xlsx'
d = pd.read_excel(X, 'Mapping_entries', keep_default_na=False)
d = d[d['Video availability'] != 'Full'].copy()
assert len(d) == 62

AMOUNT = {'E001', 'E012', 'E090', 'E166', 'E191', 'E192', 'E193', 'E194', 'E195'}
VERBAL = {'E005', 'E011', 'E028', 'E033', 'E064', 'E066', 'E099', 'E160'}
USUAL = {'E104', 'E110', 'E111', 'E112', 'E113', 'E189'}
SUPERV = {'E161', 'E162'}

def reason(r):
    t = r['Score-defining information type']
    if 'self-report' in t:
        return '6 Patient report'
    if 'force' in t or 'tone' in t:
        return '5 Examiner-applied force, tone or reflex'
    e = r['Entry ID']
    for s, lab in [(AMOUNT, '1 Amount of assistance'), (VERBAL, '2 Verbal cue or response'),
                   (USUAL, '3 Usual performance outside the recording'), (SUPERV, '4 Supervision decision without a visible trace')]:
        if e in s:
            return lab
    raise ValueError(e)

d['Main reason'] = d.apply(reason, axis=1)
SRC = [('patient report', 'Patient interview or questionnaire'), ('audio', 'Audio recording'),
       ("examiner's record", "Examiner's record of the clinical decision"),
       ('manual examination', 'Manual examination'), ('daily-life records', 'Clinical or daily-life records'),
       ('force measurement', 'Force measurement')]
for k, lab in SRC:
    d[lab] = d['Supplementary source'].str.contains(k, regex=False).astype(int)
cols = [lab for _, lab in SRC]
tab = d.groupby('Main reason').agg(**{'Entries': ('Entry ID', 'size'), 'Partial': ('Video availability', lambda s: (s == 'Partial').sum()),
                                     'None': ('Video availability', lambda s: (s == 'None').sum())}, **{c: (c, 'sum') for c in cols})
tab.loc['Total'] = tab.sum()
print(tab.to_string())

wb = openpyxl.load_workbook(X)
if 'Source_crosstab' in wb.sheetnames:
    del wb['Source_crosstab']
ws = wb.create_sheet('Source_crosstab', index=wb.sheetnames.index('Mapping_entries') + 1)
ws.append(['Main reason the entry is not fully available'] + list(tab.columns))
for idx, row in tab.iterrows():
    ws.append([idx.split(' ', 1)[1] if idx[0].isdigit() else idx] + [int(v) for v in row])
ws.append([])
ws.append(['Notes', 'Rows: the 62 Partial or None entries, each assigned one main reason (the information type that decides '
           'its code; rows 1-4 split the 25 Partial entries graded partly by assistance, supervision, safety or verbal '
           'information). Columns: the supplementary sources listed for the entry in Mapping_entries; an entry can need '
           'several, so source totals exceed 62 and differ from the main-reason counts. For example, audio is needed '
           'for the 8 entries whose main reason is a verbal cue or response but also for entries whose grades rest '
           'mainly on the amount of help, usual performance or interview content and include verbal help or cues as a '
           'secondary criterion.'])
for c in ws[1]:
    c.font = Font(bold=True); c.fill = PatternFill('solid', fgColor='DDEBF7'); c.alignment = Alignment(wrap_text=True, vertical='top')
ws.cell(ws.max_row - 2, 1).font = Font(bold=True)
ws.cell(ws.max_row, 1).font = Font(bold=True)
ws.column_dimensions['A'].width = 44
for i in range(2, 2 + len(tab.columns)):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = 16

# main-reason label per entry in Mapping_entries
wm = wb['Mapping_entries']
hdr = [c.value for c in wm[1]]
if 'Main reason not fully available' not in hdr:
    col = len(hdr) + 1
    wm.cell(1, col, 'Main reason not fully available').font = wm.cell(1, col - 1).font.copy()
    lab = dict(zip(d['Entry ID'], d['Main reason'].str.split(' ', n=1).str[1]))
    idc = hdr.index('Entry ID') + 1
    for r in range(2, wm.max_row + 1):
        wm.cell(r, col, lab.get(wm.cell(r, idc).value, ''))
    wm.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 30

wr = wb['README']
names = [wr.cell(r, 1).value for r in range(1, wr.max_row + 1)]
if 'Source_crosstab' not in names:
    i = names.index('Mapping_entries') + 2
    wr.insert_rows(i)
    wr.cell(i, 1, 'Source_crosstab')
    wr.cell(i, 2, 'Cross-tabulation of the main reason each of the 62 Partial or None entries is not fully available '
                  'against the supplementary sources it needs (sources overlap).')
wb.save(X)
