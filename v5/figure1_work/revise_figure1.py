"""Revise Figure 1 in place (text, alignment and one added label); illustrations are not touched."""
import copy
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

SRC = r'D:\Stroke\v5\figure1_work\Figure1_original.pptx'
OUT = r'D:\Stroke\v5\figure1_work\Figure1_revised.pptx'
p = Presentation(SRC)
s = p.slides[0]
S = {sh.name: sh for sh in s.shapes}

def set_lines(sh, lines):
    """Replace text paragraph by paragraph, keeping each paragraph's run formatting."""
    paras = sh.text_frame.paragraphs
    assert len(paras) == len(lines), (sh.name, len(paras))
    for para, txt in zip(paras, lines):
        runs = para.runs
        runs[0].text = txt
        for r in runs[1:]:
            r.text = ''

# 1. feature-family names as in Table 2 (two lines: family name, example variables)
FAM = {
    'temporal family label': ('Temporal & Event', '(Duration, Counts)'),
    'spatial family label': ('Spatial & Trajectory', '(Path, Distance)'),
    'kinematics family label': ('Joint & Segment', 'Kinematics (Angles)'),
    'symmetry family label': ('Inter-segment & Relational', '(Symmetry, Coupling)'),
    'trajectory-quality family label': ('Trajectory-derived Quality', '(Smoothness, Jerk)'),
}
field = S['Pale blue field for the five feature families']
cx = field.left + field.width // 2
for name, lines in FAM.items():
    sh = S[name]
    set_lines(sh, lines)
    sh.width = Pt(166)
    sh.left = cx - sh.width // 2
    sh.text_frame.word_wrap = True

# 2. column-4 heading aligned with the other three headings
h4, h1 = S['Intended uses and validation heading'], S['Clinical observations heading']
h4.top = h1.top
h4.height = h1.height
for para in h4.text_frame.paragraphs:
    for r in para.runs:
        r.font.size = Pt(12.51)
        r.font.color.rgb = RGBColor(0x17, 0x1B, 0x22)

# 3. intended-use labels share one style (bold, 10.44 pt)
for r in S['Criterion scoring label'].text_frame.paragraphs[0].runs:
    r.font.bold = True
    r.font.size = Pt(10.44)

# 4. follow-up time labels left as in the original (8 pt made them collide)

# 5. observability boundary (Table 2, last row): what motion features do not capture
ref = S['Patient label']
box = s.shapes.add_textbox(Pt(18), Pt(431), Pt(180), Pt(33))
box.name = 'Not captured by motion features'
tf = box.text_frame
tf.word_wrap = True
tf.margin_left = tf.margin_right = Pt(2)
tf.margin_top = tf.margin_bottom = 0
tf.vertical_anchor = MSO_ANCHOR.TOP
lines = [('Not captured by motion features:', True),
         ('amount of assistance, verbal cues,', False),
         ('applied force, tone and self-report', False)]
for i, (txt, bold) in enumerate(lines):
    para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    para.alignment = PP_ALIGN.CENTER
    r = para.add_run()
    r.text = txt
    r.font.name = 'Arial'
    r.font.size = Pt(8.5)
    r.font.bold = bold
    r.font.italic = not bold
    r.font.color.rgb = RGBColor(0x4B, 0x52, 0x60)

# 5b. move the trajectory start label left of the start dot so it clears the family name
st = S['Trajectory start']
st.left, st.top = Pt(236), Pt(160)

# 6. drop the BioRender advertisement slide (not part of the figure)
sldIdLst = p.slides._sldIdLst
sid = sldIdLst[1]
p.part.drop_rel(sid.rId)
sldIdLst.remove(sid)
p.save(OUT)
print('saved', OUT)
