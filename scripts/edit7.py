# -*- coding: utf-8 -*-
"""补第14处订正（伊斯兰2c）+ 全面复核 + 重出终稿"""
import copy
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

AUTHOR = "AI编辑"; DATE = "2026-10-17T06:25:00Z"
_c = [7000]
def nid():
    _c[0] += 1
    return str(_c[0])

def _set_run_text(run_el, text):
    for ch in list(run_el):
        if ch.tag in (qn('w:t'), qn('w:delText')):
            run_el.remove(ch)
    t = OxmlElement('w:t'); t.set(qn('xml:space'), 'preserve'); t.text = text
    run_el.append(t)

def replace_in_para(p, old, new):
    for run in p.runs:
        if old in run.text:
            before, after = run.text.split(old, 1)
            r = run._r
            r_old = copy.deepcopy(r); _set_run_text(r_old, old)
            for t in r_old.findall(qn('w:t')):
                t.tag = qn('w:delText')
            r_new = copy.deepcopy(r); _set_run_text(r_new, new)
            r_after = copy.deepcopy(r); _set_run_text(r_after, after)
            _set_run_text(r, before)
            parent = r.getparent(); idx = list(parent).index(r)
            d = OxmlElement('w:del')
            d.set(qn('w:id'), nid()); d.set(qn('w:author'), AUTHOR); d.set(qn('w:date'), DATE)
            d.append(r_old)
            ins = OxmlElement('w:ins')
            ins.set(qn('w:id'), nid()); ins.set(qn('w:author'), AUTHOR); ins.set(qn('w:date'), DATE)
            ins.append(r_new)
            nodes = ([r] if before else []) + [d, ins] + ([r_after] if after else [])
            for off, n in enumerate(nodes):
                parent.insert(idx + off, n)
            if not before:
                parent.remove(r)
            return True
    return False

sup = Document("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")
T = sup.tables
# ⑮ 伊斯兰2c（表A5 行3 列6）：1.0 → 0.5
cell = T[10].rows[3].cells[6]
assert cell.text.strip() == "1.0", cell.text
assert replace_in_para(cell.paragraphs[0], "1.0", "0.5")
print(" - ⑮伊斯兰2c：1.0→0.5（表A5b有伊斯兰2c=0.5专门判定理由；修正后和=2.5=总分）")
sup.save("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")

# ===== 全面复核 =====
def cell_text(cell):
    out = []
    for el in cell._tc.iter():
        if el.tag == qn('w:t'):
            out.append(el.text or '')
    return ''.join(out)
def num(s):
    s = s.strip().split("(")[0]
    return float(s) if s else None

sup = Document("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")
T = sup.tables
ok_all = True
print("\n== 全面复核（修订态最终文本）==")
for ti, name, totrow in [(7, "条件一", 6), (10, "条件二", 6)]:
    t = T[ti]
    for ci in range(1, 9):
        case = cell_text(t.rows[0].cells[ci]).strip()
        vals = [num(cell_text(t.rows[r].cells[ci])) for r in range(1, 6)]
        s = sum(vals); tot = num(cell_text(t.rows[totrow].cells[ci]))
        ok = abs(s - tot) < 1e-9; ok_all = ok_all and ok
        print(f"  {'✓' if ok else '✗'} {name} {case}: {'+'.join(str(v) for v in vals)} = {s:.1f} vs {tot}")
t = T[25]
for ri in range(1, 9):
    case = cell_text(t.rows[ri].cells[0]).strip()
    mi = [num(x) for x in cell_text(t.rows[ri].cells[1]).split("/")]
    ma = [num(x) for x in cell_text(t.rows[ri].cells[3]).split("/")]
    mtt = num(cell_text(t.rows[ri].cells[2])); mat = num(cell_text(t.rows[ri].cells[4]))
    org = num(cell_text(t.rows[ri].cells[5]))
    ok = (len(mi) == 5 and len(ma) == 5 and abs(sum(mi) - mtt) < 1e-9
          and abs(sum(ma) - mat) < 1e-9 and abs(mtt + mat - org) < 1e-9)
    ok_all = ok_all and ok
    print(f"  {'✓' if ok else '✗'} 条件四 {case}: 微{sum(mi):.1f}/{mtt} 宏{sum(ma):.1f}/{mat} 总{mtt+mat:.1f}/{org}")
import re
b1 = T[39]
vals = [float(x) for x in re.findall(r"=\s*([0-9.]+)", cell_text(b1.rows[1].cells[2]))]
score = num(cell_text(b1.rows[1].cells[1]))
ok = abs(sum(vals) - score) < 1e-9; ok_all = ok_all and ok
print(f"  {'✓' if ok else '✗'} 苏美尔信仰: 和{sum(vals):.1f} vs 公布{score}")
t = T[36]
for ri in range(1, 9):
    case = cell_text(t.rows[ri].cells[0]).strip()
    scores = [num(cell_text(t.rows[ri].cells[ci])) for ci in range(1, 6)]
    ge4 = sum(1 for v in scores if v >= 4); pub = num(cell_text(t.rows[ri].cells[6]))
    ok = ge4 == pub; ok_all = ok_all and ok
    print(f"  {'✓' if ok else '✗'} 表A14 ≥4数 {case}: {ge4} vs {pub}")
main = Document("/home/work/.openclaw/workspace/投稿69_修改稿.docx")
t6 = main.tables[5]
col = [cell_text(c).strip() for c in t6.rows[0].cells].index("≥4数")
for ri in range(1, len(t6.rows)):
    case = cell_text(t6.rows[ri].cells[0]).strip()
    scores = [num(cell_text(t6.rows[ri].cells[ci])) for ci in range(1, 6)]
    ge4 = sum(1 for v in scores if v >= 4); pub = num(cell_text(t6.rows[ri].cells[col]))
    ok = ge4 == pub; ok_all = ok_all and ok
    print(f"  {'✓' if ok else '✗'} 主文表6 ≥4数 {case}: {ge4} vs {pub}")
print(">>> 全部一致 ✓" if ok_all else ">>> 仍有不一致 ✗")

# ===== 重出终稿 =====
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
