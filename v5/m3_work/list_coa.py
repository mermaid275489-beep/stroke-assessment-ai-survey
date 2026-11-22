import re
s = open('D:/Stroke/v5/Supplementary Table S2.tex', encoding='utf-8').read()
a = s[:s.index('{S2b}')]
for l in a.splitlines():
    if re.match(r'^\d+ & ', l):
        c = re.split(r'(?<!\\)&', l)
        print(c[0].strip(), '|', c[1].strip()[:45], '|', c[2].strip(), '|', c[5].strip()[:80])
