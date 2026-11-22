import sys
import pandas as pd
sys.path.insert(0, r'D:\Stroke\v5\m3_work')
from computability_codes import CODES

d = pd.read_excel(r'D:\Stroke\v5\Supplementary Data 1.xlsx', 'Mapping_entries', keep_default_na=False)
assert set(CODES) == set(d['Entry ID']), set(d['Entry ID']) ^ set(CODES)
d['C'] = d['Entry ID'].map(lambda e: CODES[e][0])
d['Rationale'] = d['Entry ID'].map(lambda e: CODES[e][1])
print(pd.crosstab(d['Video availability'], d['C'], margins=True))
mis = d[(d['Video availability'] == 'None') != (d['C'] == 'NA')]
print('NA mismatches:', mis[['Entry ID', 'Video availability', 'C']].values.tolist())

for av in ['Full', 'Partial']:
    s = d[d['Video availability'] == av]
    print(f'\n{av}: entries', s.C.value_counts().to_dict(), ' tools', {c: s[s.C == c].Tool.nunique() for c in 'DPJ'})
    for c in 'DPJ':
        print(' ', c, sorted(s[s.C == c].Tool.unique()))

# tool-weighted share of Full-Direct (mean over tools of the per-tool proportion)
d['FD'] = (d['Video availability'] == 'Full') & (d.C == 'D')
print('\nFull&Direct entries', d.FD.sum(), 'tool-weighted', round(d.groupby('Tool').FD.mean().mean() * 100, 1))
# excluding RMI
x = d[~d.Tool.str.startswith('Rivermead')]
print('without RMI Full&Direct', x.FD.sum(), len(x))
# by mapping unit
print(pd.crosstab(d['Mapping unit'], [d['Video availability'], d.C]))
# info type: entries graded only by time, distance or count
print(pd.crosstab(d['Score-defining information type'], d.C).to_string())
d[['Entry ID', 'Tool', 'Item / task', 'Video availability', 'C', 'Rationale']].to_csv(
    r'D:\Stroke\v5\m3_work\computability_draft.csv', index=False, encoding='utf-8-sig')
