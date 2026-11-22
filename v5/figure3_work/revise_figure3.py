"""Small text fixes to the user's Figure 3 (layout and data untouched)."""
from pptx import Presentation
from pptx.util import Pt

SRC = r'D:\Stroke\v5\figure3_work\Figure3_original.pptx'
OUT = r'D:\Stroke\v5\figure3_work\Figure3_revised.pptx'
p = Presentation(SRC)
s = p.slides[0]
S = {sh.name: sh for sh in s.shapes}

def replace_in(sh, old, new):
    for para in sh.text_frame.paragraphs:
        for r in para.runs:
            if old in r.text:
                r.text = r.text.replace(old, new)
                return True
    raise ValueError((sh.name, old))

# missing space before the count
replace_in(S['a information type 2'], 'information(n', 'information (n')

# boxes whose text is wider than the box: widen to the left, keeping the right edge
for name, extra in [('c feature family 3', 14), ('a information type 4', 12)]:
    sh = S[name]
    right = sh.left + sh.width
    sh.width = sh.width + Pt(extra)
    sh.left = right - sh.width

# panel d note matches the caption
replace_in(S['d selected tools note'], 'Selected tools shown.', 'The five tools with the most entries in each domain are shown.')

# drop the BioRender advertisement slide
lst = p.slides._sldIdLst
sid = lst[1]
p.part.drop_rel(sid.rId)
lst.remove(sid)
p.save(OUT)
print('saved', OUT)
