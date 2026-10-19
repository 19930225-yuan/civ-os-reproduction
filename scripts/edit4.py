# -*- coding: utf-8 -*-
"""第四轮：印度案例补"空间不均衡+进程中断"（区域伊斯兰化/英国干预/印巴分治）"""
import copy
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

AUTHOR = "AI编辑"; DATE = "2026-10-17T05:30:00Z"
_c = [4000]
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

def flatten_para(p):
    for ins in list(p._p.findall(qn('w:ins'))):
        parent = ins.getparent(); idx = list(parent).index(ins)
        if parent.tag == qn('w:rPr'):
            parent.remove(ins); continue
        for ch in list(ins):
            parent.insert(idx, ch); idx += 1
        parent.remove(ins)
    for dl in list(p._p.findall(qn('w:del'))):
        parent = dl.getparent()
        parent.remove(dl)

def full_text(p):
    out = []
    for el in p._p:
        tag = el.tag.split('}')[1]
        if tag == 'r':
            out.append(''.join(t.text or '' for t in el.findall(qn('w:t'))))
        elif tag == 'ins':
            for r in el.findall(qn('w:r')):
                out.append(''.join(t.text or '' for t in r.findall(qn('w:t'))))
    return ''.join(out)

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

# ---------- 正文 §8.5 ----------
d = Document("/home/work/.openclaw/workspace/投稿69_修改稿.docx")
p = [x for x in d.paragraphs if full_text(x).startswith("印度（外壳=3.5）")]
assert len(p) == 1
flatten_para(p[0])
old = "上述判定与证据的逐条论证详见补充材料C第C.16.1节。"
new = ("还需作空间限定：伊斯兰化在南亚次大陆并非整体失败——今巴基斯坦、孟加拉与克什米尔谷地等地区确实完成了深度伊斯兰化，"
       "当地原有的佛教、印度教认同被替代；未被替代的是印度文明核心区（恒河平原大部、德干与南印度）的文明承诺。"
       "18世纪中叶起英国殖民统治逐步取代莫卧儿政权，伊斯兰化的政治动力被第三方力量中断，1947年印巴分治又以宗教分界"
       "将两种文明的空间边界政治性地固定下来。上述判定与证据的逐条论证详见补充材料C第C.16.1节。")
assert replace_in_para(p[0], old, new)
print("R3 正文§8.5补空间限定与进程中断")

# ---------- 补充材料 C.16.1 新增 (e) ----------
d2 = Document("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")
ref = [x for x in d2.paragraphs if full_text(x).startswith("（d）压力下的宗教创新")]
assert len(ref) == 1
insert_para_tracked(d2, ref[0],
    "（e）空间不均衡与进程中断：区域伊斯兰化与英国殖民干预。南亚的伊斯兰化并非整体性失败，而是空间上不均衡、"
    "时间上被中断的过程：西北印度（犍陀罗、旁遮普西部）的佛教社群在11—13世纪的入侵与伊斯兰化进程中消亡；"
    "孟加拉在德里苏丹国至孟加拉苏丹国时期（13—16世纪）完成大规模伊斯兰化；克什米尔谷地于14—15世纪伊斯兰化。"
    "在这些地区，伊斯兰统治建立了替代性核心认同（判定指标（b）成立），原有文明认同随之更替；"
    "印度文明核心区（恒河平原大部、德干与南印度）则维持了核心承诺。18世纪中叶起，英国殖民统治逐步取代莫卧儿与地方政权，"
    "伊斯兰化的政治动力被第三方力量中断；1947年印巴分治以宗教分界固定了两种文明的空间边界——巴基斯坦以“两个民族理论”立国，"
    "可视为伊斯兰文明在南亚完成“核心承诺+政治载体”重建的案例。对本文框架的意义有三：（i）印度的“未穿透”必须作空间限定，"
    "指印度文明核心区；（ii）外部冲击可以被第三方力量中断——冲击的“终止”属于压力测试参数的一部分，而非被测者结构强度的一部分，"
    "这与正文第七节将冲击策略定位为“力度参数”的处理一致；（iii）若将分析单位下沉到区域层面，"
    "“伊斯兰化成功的地区对应基层组织网络（种姓/宗族）较弱、核心承诺锚定较弱的地区”是一个可独立检验的推论，留待后续研究。",
    "Normal", after=True)
print("R4 补充材料C.16.1新增(e)条")
d.save("/home/work/.openclaw/workspace/投稿69_修改稿.docx")
d2.save("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")

# ---------- 重出终稿 ----------
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
