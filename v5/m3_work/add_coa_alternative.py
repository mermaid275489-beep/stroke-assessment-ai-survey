"""M6: give the COA class under a task-based reading of the BEST/ISPOR definitions alongside the operational class."""
import re
import openpyxl

S2 = r'D:\Stroke\v5\Supplementary Table S2.tex'
X = r'D:\Stroke\v5\Supplementary Data 1.xlsx'
# S2a IDs whose class differs under the task-based reading: standardized tasks performed on instruction and graded
# from that performance are PerfO whoever applies the criteria.
TO_PERFO = {4: 'ARAT', 5: 'BBS', 8: 'CAHAI', 9: 'CB&M', 10: 'DGI', 11: 'EMS', 14: 'FIST', 15: 'FGA', 19: 'Mini-BESTest',
            26: 'POMA', 27: 'TCT', 28: 'TIS', 29: 'WMFT', 30: 'ABMS II', 35: 'FMA-LE', 36: 'FMA-UE', 43: 'MoAS', 48: 'STREAM'}

tex = open(S2, encoding='utf-8').read()
cut = tex.index(r'\renewcommand{\thetable}{S2b}')
a, b = tex[:cut], tex[cut:]
assert '[task-based: PerfO]' not in a

def sub(m):
    c = re.split(r'(?<!\\)&', m.group(0))
    i = int(c[0])
    if i in TO_PERFO:
        c[2] = c[2].rstrip() + ' [task-based: PerfO] '
    return '&'.join(c)

a, n = re.subn(r'^\d+ & .*\\\\$', sub, a, flags=re.M)
assert n == 57
old = r'\noindent\scriptsize\textit{Notes.} Domain,'
assert old in a
a = a.replace(old, r'\noindent\scriptsize\textit{Notes.} COA / mode gives the operational class used in the main text; '
              r'[task-based: PerfO] marks tools that would be performance outcomes under a task-based reading of the '
              r'BEST and ISPOR definitions, in which a standardized task performed on instruction and graded from that '
              r'performance is a PerfO whoever applies the criteria (34 PerfO, 16 ClinRO, six PRO and one mixed tool, the RMI). Domain,', 1)
open(S2, 'w', encoding='utf-8').write(a + b)
print('S2a rows changed:', len(TO_PERFO))

wb = openpyxl.load_workbook(X)
ws = wb['Coding_rules']
for r in range(1, ws.max_row + 1):
    if ws.cell(r, 1).value == 'COA classification':
        v = ws.cell(r, 2).value
        if 'task-based reading' not in v:
            ws.cell(r, 2).value = v.rstrip() + (' Under a task-based reading of the BEST and ISPOR definitions, in which a '
                'standardized task performed on instruction and graded from that performance is a PerfO whoever applies the '
                'criteria, 18 tools change class (ARAT, BBS, CAHAI, CB&M, DGI, EMS, FIST, FGA, Mini-BESTest, POMA, TCT, TIS, '
                'ABMS II, FMA-LE, FMA-UE, MoAS and STREAM from ClinRO to PerfO; WMFT from mixed to PerfO), giving 34 PerfO, '
                '16 ClinRO, 6 PRO and 1 mixed (RMI). Tools whose scores rest on examiner-applied force or touch, tone or '
                'reflex examination, recovery stage, global status or usual performance remain ClinRO under both readings.')
wb.save(X)
print('Coding_rules updated')
