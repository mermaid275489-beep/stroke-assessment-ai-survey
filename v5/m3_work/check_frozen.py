import re

def parts(path):
    t = open(path, encoding='utf-8').read()
    a = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', t, re.S)
    i = t.index(r'\section{Introduction}')
    j = t.index(r'\section{Background and Preliminaries}')
    return (a.group(1) if a else None), t[i:j]

v5 = parts(r'D:\Stroke\v5\main.tex')
for name, p in [('v4 package', r'D:\Stroke\overleaf_upload_v4_2026-11-16\main.tex'),
                ('menuscripts_v4', r'D:\Stroke\menuscripts_v4.tex'),
                ('menuscripts_v1 (advisor)', r'D:\Stroke\menuscripts_v1.tex')]:
    o = parts(p)
    print(f'{name}: abstract identical = {v5[0] == o[0]}, introduction identical = {v5[1] == o[1]}')
print('abstract found in v5:', v5[0] is not None, '| intro length', len(v5[1]))
