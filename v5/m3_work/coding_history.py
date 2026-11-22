"""Rebuild the availability-coding history of every mapping entry (v5, response to review item 2).

Stages
  S1 initial     first coder, 193 records (Bridge_matrix_v4_0625.xlsx, column "Can derive original score?")
  S2 second      second reviewer's independent code (records not flagged = agreement)
  S3 consensus   after consensus on the 44 disagreements (34 recoded)
  S4 round 2     coding-rule pass R1-R5 by one coder; entry set restructured to 196 (entries_r2.csv)
  S5 round 3     verification of tool versions, outputs and scoring manuals (entries_r3.csv)
  S6 final       re-examination under the revised availability rule (entries_r4.csv)
"""
import collections
import openpyxl
import pandas as pd

REV = r'D:\Stroke\revision_2026-11-15'
V5 = r'D:\Stroke\v5'
norm = lambda m: 'Full' if str(m).upper().startswith('YES') else 'Partial' if str(m).upper().startswith('PARTIAL') else 'None'

wb = openpyxl.load_workbook(REV + r'\second_coder\Bridge_matrix_v4_0625.xlsx', read_only=True, data_only=True)
rows = [r for r in list(wb['Bridge_matrix'].iter_rows(values_only=True))[1:] if r[0]]
v4 = pd.DataFrame([(str(r[0]), str(r[4]), str(r[5]), norm(r[12])) for r in rows], columns=['Tool', 'Item', 'Task', 'S1'])
assert len(v4) == 193

r1 = pd.read_csv(REV + r'\entries_r1_frozen.csv', keep_default_na=False, dtype=str)
r2 = pd.read_csv(REV + r'\entries_r2.csv', keep_default_na=False, dtype=str)
r3 = pd.read_csv(REV + r'\entries_r3.csv', keep_default_na=False, dtype=str)
r4 = pd.read_csv(REV + r'\entries_r4.csv', keep_default_na=False, dtype=str)
chk = pd.read_excel(V5 + r'\Supplementary Data 1.xlsx', 'Second_reviewer_check', keep_default_na=False)

# r2 entry IDs keyed by (tool, task); r1 rows are matched to r2 IDs through the same key
id_by_key = {(t, k): e for e, t, k in zip(r2['Entry ID'], r2['Tool'], r2['Item / task'])}
# v4 record -> entry ID with an unchanged definition (same tool and task wording; RMI matched by item number)
def entry_for(rec):
    e = id_by_key.get((rec.Tool, rec.Task))
    if e:
        return e
    if rec.Tool.startswith('Rivermead'):
        m = r2[(r2.Tool == rec.Tool) & (r2.Item == rec.Item)]
        if len(m) == 1:
            return m['Entry ID'].iloc[0]
    return None

v4['Entry ID'] = [entry_for(r) for r in v4.itertuples()]
# the second-reviewer sheet names entries by final ID; use it to fill S2/S3 for flagged records
sec = dict(zip(chk['Entry ID'], chk['Second reviewer']))
con = dict(zip(chk['Entry ID'], chk['Code after reconciliation']))
ini = dict(zip(chk['Entry ID'], chk['Initial code']))
for e in chk['Entry ID']:
    assert e in set(v4['Entry ID']), e
v4['S2'] = [sec.get(e, s1) for e, s1 in zip(v4['Entry ID'], v4['S1'])]
v4['S3'] = [con.get(e, s1) for e, s1 in zip(v4['Entry ID'], v4['S1'])]
mism = [(e, ini[e], s1) for e, s1 in zip(v4['Entry ID'], v4['S1']) if e in ini and ini[e] != s1]
print('initial-code mismatches between matrix and check sheet:', mism)

# RMI definitions changed (self-report vs observed): treat as redefined unless wording identical
redefined_rmi = v4.Tool.str.startswith('Rivermead') & v4['Entry ID'].notna()
print('stage counts on 193 records')
for s in ['S1', 'S2', 'S3']:
    print(' ', s, collections.Counter(v4[s]))

H = r4[['Entry ID', 'Tool', 'Item / task']].copy()
H = H.merge(v4[['Entry ID', 'S1', 'S2', 'S3']], on='Entry ID', how='left')
for k, d in [('S4', r2), ('S5', r3), ('S6', r4)]:
    H = H.merge(d[['Entry ID', 'Video availability']].rename(columns={'Video availability': k}), on='Entry ID', how='left')
H['Checked record'] = H['S1'].notna()
print('final entries traceable to a checked record:', H['Checked record'].sum())
for s in ['S4', 'S5', 'S6']:
    print(' ', s, collections.Counter(H[s].fillna('-')))

def nchg(a, b, sub):
    x = sub[[a, b]].dropna()
    return int((x[a] != x[b]).sum()), len(x)

T = H[H['Checked record']]
print('S1->S3 changes (checked, traceable)', nchg('S1', 'S3', T))
print('S3->S4 changes', nchg('S3', 'S4', T), ' S4->S5', nchg('S4', 'S5', H), ' S5->S6', nchg('S5', 'S6', H))
print('S3->S5 changes (checked)', nchg('S3', 'S5', T))
print('S3==S5==... carried unchanged to round 3:', int((T.S3 == T.S5).sum()))
untr = v4[v4['Entry ID'].isna()]
print('checked records without an unchanged entry:', len(untr)); print(untr[['Tool', 'Task']].to_string())
H.to_csv(V5 + r'\m3_work\coding_history.csv', index=False, encoding='utf-8-sig')
