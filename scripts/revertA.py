# -*- coding: utf-8 -*-
"""按作者裁决（方案A：总分为BARS整体锚定判定）：撤回14处格子改动、补方法说明、重出终稿"""
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

AUTHOR = "AI编辑"; DATE = "2026-10-17T06:40:00Z"
_c = [8000]
def nid():
    _c[0] += 1
    return str(_c[0])

def cell_text(cell):
    return ''.join(el.text or '' for el in cell._tc.iter() if el.tag == qn('w:t'))

def revert_cell(cell, expected, tag, log):
    """撤销该格的修订：删除插入内容、恢复删除内容"""
    for p in cell.paragraphs:
        for ins in list(p._p.findall(qn('w:ins'))):
            parent = ins.getparent()
            if parent.tag == qn('w:rPr'):
                parent.remove(ins); continue
            parent.remove(ins)
        for dl in list(p._p.findall(qn('w:del'))):
            parent = dl.getparent(); idx = list(parent).index(dl)
            for r in list(dl):
                for dt in r.findall(qn('w:delText')):
                    dt.tag = qn('w:t')
                parent.insert(idx, r); idx += 1
            parent.remove(dl)
    cur = cell_text(cell).strip()
    assert cur == expected, f"{tag}: 恢复后 {cur!r} ≠ 原值 {expected!r}"
    log.append(tag)

# ============ 补充材料 ============
sup = Document("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")
T = sup.tables
log = []
revert_cell(T[7].rows[4].cells[3],  "1.0", "撤①日本1d→1.0", log)
revert_cell(T[7].rows[5].cells[4],  "0",   "撤②基督教1e→0", log)
revert_cell(T[7].rows[5].cells[8],  "0.5", "撤③拜占庭1e→0.5", log)
revert_cell(T[10].rows[2].cells[8], "0.5", "撤④拜占庭2b→0.5", log)
revert_cell(T[10].rows[3].cells[8], "0.5", "撤⑤拜占庭2c→0.5", log)
revert_cell(T[10].rows[4].cells[5], "1.0", "撤⑥印度2d→1.0", log)
revert_cell(T[10].rows[3].cells[6], "1.0", "撤⑮伊斯兰2c→1.0", log)
revert_cell(T[25].rows[2].cells[3], "0.5/0.5/0.5/0.5/0", "撤⑦中华宏观", log)
revert_cell(T[25].rows[3].cells[3], "0.5/0.5/0.5/0/0",   "撤⑧日本宏观", log)
revert_cell(T[25].rows[6].cells[3], "0.5/0.5/0.5/0/0",   "撤⑨伊斯兰宏观", log)
revert_cell(T[25].rows[5].cells[3], "0/0/0/0/0/0",       "撤⑩印度宏观", log)
revert_cell(T[25].rows[8].cells[1], "0/0/0/0/0/0",       "撤⑪拜占庭微观", log)
revert_cell(T[25].rows[7].cells[1], "0/0/0/0/0/0",       "撤⑫古埃及微观", log)
revert_cell(T[36].rows[4].cells[6], "3",                 "撤⑬表A14≥4数→3", log)
revert_cell(T[39].rows[1].cells[2], "1a=0, 1b=0.5, 1c=0.5, 1d=0.5, 1e=0.5", "撤⑭苏美尔1e→0.5", log)

# A.0.2 补方法说明（修订模式插入）
ref = None
for p in sup.paragraphs:
    if p.text.startswith("关于条件四（组织能力）的说明"):
        ref = p; break
assert ref is not None
new_p = sup.add_paragraph(style="Normal")
r = new_p.add_run(
    "关于条件总分与子维度分的关系：各条件总分为行为锚定等级量表（BARS）整体锚定判定的结果，"
    "子维度分是判定理由的结构化呈现，二者不构成算术加总关系（唯一例外：条件三按∑（各项原始分×0.5）计算）。"
    "因此，复核或审稿时不应以子维度分的算术加总校验条件总分。")._r
parent = r.getparent(); idx = list(parent).index(r)
parent.remove(r)
ins = OxmlElement('w:ins')
ins.set(qn('w:id'), nid()); ins.set(qn('w:author'), AUTHOR); ins.set(qn('w:date'), DATE)
ins.append(r); parent.insert(idx, ins)
pPr = new_p._p.get_or_add_pPr()
rPr = pPr.find(qn('w:rPr'))
if rPr is None:
    rPr = OxmlElement('w:rPr')
    st = pPr.find(qn('w:pStyle'))
    (st.addnext(rPr) if st is not None else pPr.insert(0, rPr))
m = OxmlElement('w:ins')
m.set(qn('w:id'), nid()); m.set(qn('w:author'), AUTHOR); m.set(qn('w:date'), DATE)
rPr.append(m)
ref._p.addnext(new_p._p)
log.append("补A.0.2方法说明（总分为整体锚定判定，非子维度加总）")
sup.save("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")

# ============ 主文 ============
main = Document("/home/work/.openclaw/workspace/投稿69_修改稿.docx")
t6 = main.tables[5]
hdr = [cell_text(c).strip() for c in t6.rows[0].cells]
col = hdr.index("≥4数")
ri = [i for i, r in enumerate(t6.rows) if cell_text(r.cells[0]).strip().startswith("基督教")][0]
revert_cell(t6.rows[ri].cells[col], "3", "撤⑬主文表6≥4数→3", log)
main.save("/home/work/.openclaw/workspace/投稿69_修改稿.docx")

for x in log: print(" -", x)

# ============ 重出终稿 ============
def accept_all(src, dst):
    dd = Document(src)
    body = dd.element.body
    for ins in list(body.findall('.//' + qn('w:ins'))):
        parent = ins.getparent(); idx = list(parent).index(ins)
        if parent.tag == qn('w:rPr'):
            parent.remove(ins); continue
        for ch in list(ins):
            parent.insert(idx, ch); idx += 1
        parent.remove(ins)
    for dl in list(body.findall('.//' + qn('w:del'))):
        parent = dl.getparent()
        if parent.tag == qn('w:rPr'):
            p = parent.getparent().getparent()
            has_text = any(t.text for t in p.findall('.//' + qn('w:t')))
            if not has_text:
                p.getparent().remove(p)
            else:
                parent.remove(dl)
            continue
        parent.remove(dl)
    dd.save(dst)
accept_all("/home/work/.openclaw/workspace/投稿69_修改稿.docx", "/home/work/.openclaw/workspace/投稿69_终稿.docx")
accept_all("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx", "/home/work/.openclaw/workspace/网络补充材料_终稿.docx")
print("终稿已更新")
