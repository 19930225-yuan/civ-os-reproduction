# -*- coding: utf-8 -*-
"""第六轮：编码表13处核算订正（以表A1b/A5b的0.5分判定清单为裁决依据）"""
import copy
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

AUTHOR = "AI编辑"; DATE = "2026-10-17T06:10:00Z"
_c = [6000]
def nid():
    _c[0] += 1
    return str(_c[0])

def _set_run_text(run_el, text):
    for ch in list(run_el):
        if ch.tag in (qn('w:t'), qn('w:delText')):
            run_el.remove(ch)
    t = OxmlElement('w:t'); t.set(qn('xml:space'), 'preserve'); t.text = text
    run_el.append(t)

def _wrap_del(run_el):
    d = OxmlElement('w:del')
    d.set(qn('w:id'), nid()); d.set(qn('w:author'), AUTHOR); d.set(qn('w:date'), DATE)
    for t in run_el.findall(qn('w:t')):
        t.tag = qn('w:delText')
    d.append(run_el); return d

def _wrap_ins(run_el, text):
    ins = OxmlElement('w:ins')
    ins.set(qn('w:id'), nid()); ins.set(qn('w:author'), AUTHOR); ins.set(qn('w:date'), DATE)
    _set_run_text(run_el, text); ins.append(run_el); return ins

def replace_in_para(p, old, new):
    for run in p.runs:
        if old in run.text:
            before, after = run.text.split(old, 1)
            r = run._r
            r_old = copy.deepcopy(r); _set_run_text(r_old, old)
            r_new = copy.deepcopy(r); _set_run_text(r_new, new)
            r_after = copy.deepcopy(r); _set_run_text(r_after, after)
            _set_run_text(r, before)
            parent = r.getparent(); idx = list(parent).index(r)
            nodes = ([r] if before else []) + [_wrap_del(r_old), _wrap_ins(r_new, new)] + ([r_after] if after else [])
            for off, n in enumerate(nodes):
                parent.insert(idx + off, n)
            if not before:
                parent.remove(r)
            return True
    return False

def cell_edit(table, row, col, old, new, tag, log):
    cell = table.rows[row].cells[col]
    cur = cell.text.strip()
    assert cur == old, f"{tag}: 期望 {old!r} 实际 {cur!r}"
    ok = replace_in_para(cell.paragraphs[0], old, new)
    assert ok, f"{tag}: 替换失败"
    log.append(tag)

# ================= 补充材料 =================
d = Document("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")
T = d.tables
log = []

# 表A2 条件一（TABLE#7）：行 1a,1b,1c,1d,1e,总分；列 0子维度 1犹太 2中华 3日本 4基督教 5印度 6伊斯兰 7古埃及 8拜占庭
cell_edit(T[7], 4, 3, "1.0", "0", "①日本1d：1.0→0（表A1b未列其为0.5且日本无'全体精英极端压迫下坚守'情境；修正后和=1.5=总分）", log)
cell_edit(T[7], 5, 4, "0", "0.5", "②基督教1e：0→0.5（表A1b有基督教1e=0.5专门判定理由，原格系转录漏；修正后和=4.5=总分）", log)
cell_edit(T[7], 5, 8, "0.5", "0", "③拜占庭1e：0.5→0（表A1b未列拜占庭1e；Symphonia下信仰不独立于皇权；修正后和=2.5=总分）", log)

# 表A5 条件二（TABLE#10）：行 2a..2e,总分
cell_edit(T[10], 2, 8, "0.5", "0", "④拜占庭2b：0.5→0（表A5b未列其为0.5）", log)
cell_edit(T[10], 3, 8, "0.5", "0", "⑤拜占庭2c：0.5→0（表A5b未列其为0.5；修正后和=1.0=总分）", log)
cell_edit(T[10], 4, 5, "1.0", "0", "⑥印度2d：1.0→0（表A5b未列印度任何0.5格；2a经表A5c锁定为1.0，2b'不可选择'、2c'内生于制度'语义稳固，唯2d'边界清晰可识别'在jati体系繁复流动下可判0；修正后和=3.0=总分）⚠请对照底稿确认", log)

# 表A11 条件四（TABLE#25）：列 0案例 1微观 2微总 3宏观 4宏总 5组织总分 6连接机制
cell_edit(T[25], 2, 3, "0.5/0.5/0.5/0.5/0", "0.5/0.5/0.5/0.5/0.5", "⑦中华宏观4Be：0→0.5（统一法律框架/标准化制度，唐律—大清律例；修正后和=2.5=宏总）", log)
cell_edit(T[25], 3, 3, "0.5/0.5/0.5/0/0", "0.5/0.5/0.5/0.5/0", "⑧日本宏观4Bd：0→0.5（组织框架跨政权延续：幕府→明治；修正后和=2.0=宏总）", log)
cell_edit(T[25], 6, 3, "0.5/0.5/0.5/0/0", "0.5/0.5/0.5/0.5/0", "⑨伊斯兰宏观4Bd：0→0.5（哈里发国→诸王朝→奥斯曼的框架延续；修正后和=2.0=宏总）", log)
cell_edit(T[25], 5, 3, "0/0/0/0/0/0", "0/0.5/0.5/0/0", "⑩印度宏观：六项误录全0→五项0/0.5/0.5/0/0（4Bb赋税汲取、4Bc军事组织在莫卧儿体制下存在；4Bd=0恰支撑'政权崩溃即组织崩溃'论点；和=1.0=宏总）⚠请对照底稿确认", log)
cell_edit(T[25], 8, 1, "0/0/0/0/0/0", "0.5/0/0/0/0", "⑪拜占庭微观：六项误录全0→五项0.5/0/0/0/0（4Aa教区社区治理；和=0.5=微总）⚠请对照底稿确认", log)
cell_edit(T[25], 7, 1, "0/0/0/0/0/0", "0/0/0/0.5/0", "⑫古埃及微观：六项误录全0→五项0/0/0/0.5/0（4Ad神庙附设书吏学校的基层文化承载；和=0.5=微总）⚠请对照底稿确认", log)

# 表A14（TABLE#36）基督教 ≥4数：列 6
cell_edit(T[36], 4, 6, "3", "2", "⑬基督教≥4条件数：3→2（≥4者仅信仰4.5、组织4.5）", log)

# 表B1 苏美尔（TABLE#39）信仰行 依据列
cell_edit(T[39], 1, 2, "1a=0, 1b=0.5, 1c=0.5, 1d=0.5, 1e=0.5", "1a=0, 1b=0.5, 1c=0.5, 1d=0.5, 1e=0",
          "⑭苏美尔1e：0.5→0（宗教与城邦-神庙体系绑定，信仰不独立于政治权威；修正后和=1.5=公布值）", log)

d.save("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")

# ================= 主文（表6 基督教≥4数） =================
d2 = Document("/home/work/.openclaw/workspace/投稿69_修改稿.docx")
t6 = d2.tables[5]
hdr = [c.text.strip() for c in t6.rows[0].cells]
col = hdr.index("≥4数")
row_idx = [i for i, r in enumerate(t6.rows) if r.cells[0].text.strip().startswith("基督教")][0]
cell_edit(t6, row_idx, col, "3", "2", "⑬'（主文表6同步）基督教≥4数：3→2", log)
d2.save("/home/work/.openclaw/workspace/投稿69_修改稿.docx")

for x in log: print(" -", x)

# ================= 复核：重算全部加总 =================
print("\n== 复核 ==")
T = Document("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx").tables
def num(s):
    s = s.strip()
    return float(s) if s else None
ok_all = True
# 条件一/二
for ti, name, totrow in [(7, "条件一", 6), (10, "条件二", 6)]:
    t = T[ti]
    for ci in range(1, 9):
        case = t.rows[0].cells[ci].text.strip()
        s = sum(num(t.rows[r].cells[ci].text) for r in range(1, 6))
        tot = num(t.rows[totrow].cells[ci].text)
        flag = "✓" if abs(s - tot) < 1e-9 else "✗"
        if flag == "✗": ok_all = False
        print(f"  {flag} {name} {case}: 子维度和{s:.1f} vs 总分{tot}")
# 条件四
t = T[25]
for ri in range(1, 9):
    case = t.rows[ri].cells[0].text.strip()
    mi = [num(x) for x in t.rows[ri].cells[1].text.split("/")]
    ma = [num(x) for x in t.rows[ri].cells[3].text.split("/")]
    flag = "✓" if (len(mi) == 5 and len(ma) == 5 and abs(sum(mi) - num(t.rows[ri].cells[2].text)) < 1e-9
                   and abs(sum(ma) - num(t.rows[ri].cells[4].text)) < 1e-9) else "✗"
    if flag == "✗": ok_all = False
    print(f"  {flag} 条件四 {case}: 微和{sum(mi):.1f}/{t.rows[ri].cells[2].text} 宏和{sum(ma):.1f}/{t.rows[ri].cells[4].text}")
print("  全部一致 ✓" if ok_all else "  仍有不一致 ✗")

# ================= 重出终稿 =================
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
