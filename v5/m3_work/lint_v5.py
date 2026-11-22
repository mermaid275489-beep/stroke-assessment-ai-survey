import re
V = 'D:/Stroke/v5/'
s = open(V + 'Supplementary Table S2.tex', encoding='utf-8').read()
i = s.index('{S2b}')
for part, name in [(s[:i], 'S2a'), (s[i:], 'S2b')]:
    rows = [l for l in part.splitlines() if re.match(r'^\d+ & ', l)]
    print(name, len(rows), 'cells per row', set(len(re.split(r'(?<!\\)&', l)) for l in rows))
m = open(V + 'main.tex', encoding='utf-8').read()
o = open(V + 'm3_work/main_before_m3.tex', encoding='utf-8').read()
cut = lambda t: t[:t.index(r'\section{Background and Preliminaries}')]
print('abstract + introduction unchanged:', cut(m) == cut(o))
first_t1 = m.find(r'\ref{tab:representative_scales_compact}')
first_t2 = m.find(r'\ref{tab:computational_feature_families}')
print('Table 1 cited before Table 2:', first_t1 < first_t2)
