# -*- coding: utf-8 -*-
"""第五轮：命题一限定、阈值识别说明、表11新增F3/F4、玛雅判定注"""
import copy
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

AUTHOR = "AI编辑"; DATE = "2026-10-17T05:50:00Z"
_c = [5000]
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

def insert_para_tracked(doc, ref_p, text, style_name, after=True):
    new_p = doc.add_paragraph(style=style_name)
    r = new_p.add_run(text)._r
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
    (ref_p._p.addnext(new_p._p) if after else ref_p._p.addprevious(new_p._p))
    return new_p

def find_para(doc, needle):
    hits = [p for p in doc.paragraphs if needle in p.text]
    assert len(hits) == 1, f"{needle!r} -> {len(hits)}"
    return hits[0]

def add_tracked_row(table, values):
    row = table.add_row()
    for cell, val in zip(row.cells, values):
        cell.text = val
        # 单元格文字标记为插入
        for p in cell.paragraphs:
            for run in list(p.runs):
                r = run._r; parent = r.getparent(); idx = list(parent).index(r)
                parent.remove(r)
                ins = OxmlElement('w:ins')
                ins.set(qn('w:id'), nid()); ins.set(qn('w:author'), AUTHOR); ins.set(qn('w:date'), DATE)
                ins.append(r); parent.insert(idx, ins)
    trPr = row._tr.get_or_add_trPr()
    mark = OxmlElement('w:ins')
    mark.set(qn('w:id'), nid()); mark.set(qn('w:author'), AUTHOR); mark.set(qn('w:date'), DATE)
    trPr.append(mark)
    return row

# ================= 正文 =================
d = Document("/home/work/.openclaw/workspace/投稿69_修改稿.docx")
log = []

p = find_para(d, "命题一：文明存续面临五个客观功能性问题")
assert replace_in_para(p, "任何一个若被永久性地否定回答，系统将在有限代际内解体。",
    "任何一个若被永久性地否定回答——且这种否定不存在外部载体补给或跨代际传承节点（如境外教团网络、活佛转世制度）的对冲——系统将在有限代际内解体。")
log.append("E1 命题一加限定（外部补给/传承节点）")

p = find_para(d, "功能分析前提：设文明为一跨越代际的行动系统")
assert replace_in_para(p, "且任何一个若被永久性地否定回答，则S将在有限代际内解体",
    "且任何一个若被永久性地否定回答（且不存在外部载体补给或跨代际传承节点的对冲），则S将在有限代际内解体")
log.append("E2 §2.1功能前提同步加限定")

p = find_para(d, "关于“加总”与“互补”的关系澄清")
assert replace_in_para(p, "功能激活阈值（外壳≥2.0是“弱点补偿”生效的前提）。",
    "功能激活阈值（外壳≥2.0是“弱点补偿”生效的前提）。需说明的是，2.0在当前样本中只能识别为区间阈值（1.0,2.0]——"
    "样本中无外壳评分介于1.5—2.5之间的案例，故该门槛应理解为“存在制度化调整接口”这一定性二分的数值化表述，"
    "其精确取值有待新增案例校准（见表11第F3条）。")
log.append("E3 §2.2补阈值识别说明")

ref = find_para(d, "声称范围。框架只声称")
insert_para_tracked(d, ref,
    "蒙古案例与命题一的限定。蒙古僧团在1930年代被系统性消灭（700余座寺院、约1.7万名喇嘛被杀），国家无神论政策延续约70年，"
    "但1990年后佛教迅速复兴——2010年普查中53%的人口自称佛教徒。这一案例表明：功能件被“永久否定”后仍可复兴，"
    "条件是存在外部载体补给（藏传佛教网络、达赖喇嘛体系）与跨代际传承节点（活佛转世制度）。据此，命题一的准确表述是："
    "当功能件被否定且不存在外部载体补给或跨代际传承节点时，系统在有限代际内解体。该限定自带可检验预测："
    "有外部补给的剥夺案例可逆，无补给者不可逆——东德、捷克的持久世俗化与波兰、俄罗斯的认同回弹构成初步对照。",
    "Normal", after=False)
log.append("E4 §8.5补蒙古边界案例与限定")

t11 = d.tables[10]
assert t11.rows[-1].cells[0].text.strip() == "F2"
add_tracked_row(t11, ["F3", "出现外壳评分介于1.5—2.5之间、且危机后结局与阈值预测不符的案例",
                      "待检验（现样本该区间无案例，2.0系约定取值）"])
add_tracked_row(t11, ["F4", "出现功能件被否定、且无外部载体补给或跨代际传承节点，却仍然复兴的案例",
                      "未触发（蒙古因存在外部补给与转世节点，不构成反例）"])
log.append("E5 表11新增F3（阈值识别）、F4（命题一限定）")
d.save("/home/work/.openclaw/workspace/投稿69_修改稿.docx")

# ================= 补充材料 =================
d2 = Document("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")
ref = find_para(d2, "B.2 六个候选扩展案例的预测")
insert_para_tracked(d2, ref,
    "玛雅判定的说明。“消亡”在本文中指古典城邦体系与象形文字传统的终结（1697年最后一个城邦陷落），而非文化认同的终结——"
    "当代玛雅人口约600万，30余种玛雅语以及宇宙观、仪式传统持续至今并有复兴运动。因此玛雅更准确的归类是“壳碎核移/核眠”谱系，"
    "而非“壳碎核亡”；表B5的模式比较相应应理解为“政治架构未恢复”，而非“文化清除”。",
    "Normal", after=False)
log.append("E6 补充材料补玛雅判定说明")
d2.save("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")

for x in log: print(" -", x)

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
