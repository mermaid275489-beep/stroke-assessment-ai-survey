"""Compare the Codex readability rewrite with the current v5 main.tex: frozen parts, citations, refs, numbers."""
import re
from collections import Counter

A = open(r'D:\Stroke\v5\main.tex', encoding='utf-8').read()
B = open(r'C:\Users\15751\Documents\Codex\2026-11-19\referenced-chatgpt-conversation-this-is-an\outputs\main_readability_revised.tex', encoding='utf-8').read()

def sect(t, a, b):
    return t[t.index(a):t.index(b)]

print('preamble identical:', A[:A.index(r'\begin{document}')] == B[:B.index(r'\begin{document}')])
print('abstract identical:', sect(A, r'\begin{abstract}', r'\end{abstract}') == sect(B, r'\begin{abstract}', r'\end{abstract}'))
ia = sect(A, r'\section{Introduction}', r'\section{Background')
ib = sect(B, r'\section{Introduction}', r'\section{Background')
print('introduction identical:', ia == ib)

cites = lambda t: Counter(k.strip() for g in re.findall(r'\\cite\w*\{([^}]*)\}', t) for k in g.split(','))
ca, cb = cites(A), cites(B)
print('citation keys only in v5:', sorted(set(ca) - set(cb)))
print('citation keys only in rewrite:', sorted(set(cb) - set(ca)))
refs = lambda t: Counter(re.findall(r'\\ref\{([^}]+)\}', t))
print('refs only in v5:', sorted(set(refs(A)) - set(refs(B))), '| only in rewrite:', sorted(set(refs(B)) - set(refs(A))))
print('labels equal:', sorted(re.findall(r'\\label\{([^}]+)\}', A)) == sorted(re.findall(r'\\label\{([^}]+)\}', B)))
print('inputs equal:', re.findall(r'\\input\{([^}]+)\}', A) == re.findall(r'\\input\{([^}]+)\}', B))

body = lambda t: t[t.index(r'\section{Background'):t.index(r'\printbibliography')]
num = lambda t: Counter(re.findall(r'(?<![\w.])\d+(?:\.\d+)?(?:--\d+(?:\.\d+)?)?', re.sub(r'\\(cite|ref|label)\w*\{[^}]*\}', '', t)))
na, nb = num(body(A)), num(body(B))
print('numbers in v5 body missing from rewrite:', sorted((na - nb).items()))
print('numbers in rewrite body not in v5:', sorted((nb - na).items()))
wa = len(re.sub(r'\\\w+|[{}]', ' ', body(A)).split()); wb = len(re.sub(r'\\\w+|[{}]', ' ', body(B)).split())
print('body words v5 %d, rewrite %d' % (wa, wb))
fa = sect(A, r'\includegraphics[width=\linewidth]{figure3.pdf}', r'\label{fig:video_availability}')
fb = sect(B, r'\includegraphics[width=\linewidth]{figure3.pdf}', r'\label{fig:video_availability}')
print('fig3 caption has priority rule in rewrite:', 'first that applies' in fb)
