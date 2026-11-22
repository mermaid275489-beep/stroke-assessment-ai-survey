"""Add the Figure 3d domain of each tool to Supplementary Table S2a (review item 6)."""
import re
import sys
sys.path.insert(0, r'D:\Stroke\revision_2026-11-15')
import make_figure3 as F3  # GROUPS: the domain assignment used for Figure 3d

S2 = r'D:\Stroke\v5\Supplementary Table S2.tex'
tex = open(S2, encoding='utf-8').read()
assert 'Domain' not in tex[:tex.index('{S2b}')]
cut = tex.index(r'\renewcommand{\thetable}{S2b}')
a, b = tex[:cut], tex[cut:]

abbr = {}
for m in re.finditer(r'^(\d+) & (.+?) & [IST] &', b, flags=re.M):
    abbr[int(m.group(1))] = re.sub(r'\\textsuperscript\{a\}', '', m.group(2)).strip()
assert len(abbr) == 57
SHORT = {'Upper limb': 'UL', 'Trunk and balance': 'TB', 'Gait and mobility': 'GM', 'Impairment and global': 'IG'}
dom = {t: SHORT[g] for g, _, ts in F3.GROUPS for t in ts}
assert set(abbr.values()) == set(dom), set(abbr.values()) ^ set(dom)

a = a.replace('>{\\RaggedRight\\arraybackslash}p{2.25cm}\n>{\\RaggedRight\\arraybackslash}p{5.90cm}',
              '>{\\RaggedRight\\arraybackslash}p{2.25cm}\n>{\\centering\\arraybackslash}p{0.85cm}\n>{\\RaggedRight\\arraybackslash}p{5.05cm}', 1)
hdr_old = r'\textbf{ID} & \textbf{Tool} & \textbf{COA / mode} & \textbf{Clinical construct and application}'
hdr_new = r'\textbf{ID} & \textbf{Tool} & \textbf{COA / mode} & \textbf{Domain} & \textbf{Clinical construct and application}'
assert a.count(hdr_old) == 2
a = a.replace(hdr_old, hdr_new)
a = a.replace(r'\multicolumn{6}{', r'\multicolumn{7}{')

def add(m):
    cells = re.split(r'(?<!\\)&', m.group(0))
    i = int(cells[0].strip())
    cells.insert(3, ' ' + dom[abbr[i]] + ' ')
    return '&'.join(cells)

a, n = re.subn(r'^\d+ & .*\\\\$', add, a, flags=re.M)
assert n == 57, n
note_old = r'\noindent\scriptsize\textit{Notes.} G, guideline evidence stream;'
assert note_old in a
a = a.replace(note_old, r'\noindent\scriptsize\textit{Notes.} Domain, the grouping used in Fig.~\ref{fig:video_availability}d: '
              r'UL, upper limb; TB, trunk and balance; GM, gait and mobility; IG, impairment and global. '
              r'G, guideline evidence stream;', 1)
open(S2, 'w', encoding='utf-8').write(a + b)
from collections import Counter
print(Counter(dom[abbr[i]] for i in abbr))
