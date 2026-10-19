# -*- coding: utf-8 -*-
"""第八轮：补充材料E新增 E.14 因果级证据（分裂对照设计 + 外部准实验文献对标）"""
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

AUTHOR = "AI编辑"; DATE = "2026-10-17T07:05:00Z"
_c = [11000]
def nid():
    _c[0] += 1
    return str(_c[0])

def add_tracked_para(doc, text, style):
    p = doc.add_paragraph(style=style)
    r = p.add_run(text)._r
    parent = r.getparent(); idx = list(parent).index(r)
    parent.remove(r)
    ins = OxmlElement('w:ins')
    ins.set(qn('w:id'), nid()); ins.set(qn('w:author'), AUTHOR); ins.set(qn('w:date'), DATE)
    ins.append(r); parent.insert(idx, ins)
    pPr = p._p.get_or_add_pPr()
    rPr = pPr.find(qn('w:rPr'))
    if rPr is None:
        rPr = OxmlElement('w:rPr')
        st = pPr.find(qn('w:pStyle'))
        (st.addnext(rPr) if st is not None else pPr.insert(0, rPr))
    m = OxmlElement('w:ins')
    m.set(qn('w:id'), nid()); m.set(qn('w:author'), AUTHOR); m.set(qn('w:date'), DATE)
    rPr.append(m)
    return p

def add_tracked_table(doc, rows, style_ref):
    t = doc.add_table(rows=1, cols=len(rows[0]))
    try:
        t.style = style_ref
    except Exception:
        t.style = 'Table Grid'
    for i, v in enumerate(rows[0]):
        t.rows[0].cells[i].text = v
    for row in rows[1:]:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = v
    for row in t.rows:
        for cell in row.cells:
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
    return t


def full_text(p):
    out = []
    for el in p._p.iter():
        if el.tag == qn('w:t'):
            parent = el.getparent().getparent()
            if parent is not None and parent.tag == qn('w:del'):
                continue
            out.append(el.text or '')
    return ''.join(out)

sup = Document("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")
style_ref = sup.tables[51].style
ref = None
for p in sup.paragraphs:
    if full_text(p).startswith("注：上述检验均为初步实测"):
        ref = p
assert ref is not None

blocks = [
 ("E.14 因果级证据：分裂对照设计与外部准实验文献", "Heading 3"),
 ("宏观历史命题无法随机化处理，本文不声称平均处理效应（ATE）。可追求的最强证据是两级："
  "一级为“同源人群分裂对照”（split-sample natural experiment）——同一民族被外生政治事件分裂进不同文明容器，处理前同质、处理后制度环境分化，"
  "结果分化方向可与预测比对；二级为已发表的准实验文献（断点回归/工具变量）中与五功能件子机制对应的因果证据。", "Normal"),
 ("（一）四组分裂对照", "Normal"),
 ("德国（1949—1990）：分裂前同民族、同语言、同宗教文化；处理为东德国家无神论+教会国家化（条件四被削弱），西德为对照。"
  "结果：1989年东德教会成员仅约30%（西德约84%）；统一35年后差距未收敛——今约2/3东德人“从未信过上帝”（西德约10%），"
  "统一后东德还出现退教潮。若效应仅是“压制期间不敢信”，1990年后的自由交流应使差距收敛；差距的持续（滞后效应）指向组织载体被破坏的不可逆部分——条件四的因果作用。", "Normal"),
 ("朝鲜半岛（1945—今）：分裂前同一文化-宗教传统（佛教、儒教、基督教）；处理为朝鲜对宗教的系统清除+封闭国境（无外部补给），韩国为对照。"
  "结果：韩国约29%基督徒+23%佛教徒（约52%宗教人口，Pew），朝鲜基督徒约1.7%、佛教徒约2%，以无信仰为主。该组对照直接检验F4限定："
  "封闭容器+无传承节点=解体不可逆，与蒙古（有转世节点而复兴）互为镜像。", "Normal"),
 ("印巴/孟加拉（1947—今）：分治前同源人口（旁遮普、孟加拉两地的印度教徒/穆斯林/锡克教徒）；处理为进入不同文明容器。"
  "结果：孟加拉印度教徒22%（1951）→8.5%（2022），巴基斯坦印度教徒约15%（1947）→1.6%（1951）至今，印度穆斯林9.8%→14.2%（2011）——"
  "各容器向本教主体同质化。识别局限：1947年约1400万人的交换迁徙削弱“处理前同质”假设，且孟加拉案例的下降主因含生育率与迁移（见E.10）。", "Normal"),
 ("两岸（1949—今）：处理为大陆的宗教清除（1966—76）后伴随再开放与外部补给（港台佛教/基督教网络），台湾为连续对照。"
  "结果：大陆宗教活动在1980年代后大规模恢复（寺庙重建、信众回升），与F4“有补给则可逆”一致；台湾宗教生态延续未断。", "Normal"),
 ("四组对照的共同逻辑：分裂事件本身由战争与大国政治决定，近似外生；结果分化方向与框架预测一致（组织载体存续度、补给有无决定恢复轨迹）。"
  "这不是随机实验，但已属宏观史可得的最强因果证据形态。", "Normal"),
 ("（二）外部准实验文献的机制对标", "Normal"),
]
for text, style in blocks:
    add_tracked_para(sup, text, style)

add_tracked_table(sup, [
    ["文献", "设计", "因果发现", "对标功能件"],
    ["Dell (2010), Econometrica 78(6)", "断点回归：殖民强制劳役（Mita）边界", "制度/产权形式沿边界持续300年以上", "条件四/五：组织与外壳的路径持续性"],
    ["Becker & Woessmann (2009), QJE 124(2)", "工具变量：至维滕贝格距离→新教传教", "传教→识字率→长期人力资本", "条件三：文本-教育引擎的因果效力"],
    ["Nunn (2008), QJE 123(3)", "工具变量：至海岸距离→奴隶输出强度", "奴隶贸易→族群碎片化与不信任长期存续", "条件二/四：边界与组织被破坏的长期效应"],
    ["Nunn & Wantchekon (2011), AER 101(7)", "工具变量：至海岸距离→奴隶劫掠暴露", "历史劫掠→当代人际不信任", "条件二/四：同上（个体层验证）"],
], style_ref)
add_tracked_para(sup, "读法：五功能件的子机制（制度惯性、文本教育的传递效力、组织/边界破坏的长期疤痕）在经济学准实验文献中已各有因果级证据；"
  "本文的增量是把这些子机制装配为系统级命题，并以分裂对照与事件史做系统级检验。系统级命题本身无法达到子机制级的识别强度——"
  "这是宏观比较研究的方法论上限，应明示而非掩饰。", "Normal")
add_tracked_para(sup, "（三）识别边界声明：（a）文明存续不可随机化，N=1世界不存在重复实验；（b）分裂对照的识别假设（分裂外生、处理前同质）"
  "在德国、朝鲜组最强，印巴组因人口交换减弱；（c）朝鲜数据为估计值，精度有限；（d）本文的因果声称限于机制级与准实验级，"
  "不声称平均处理效应，亦不声称五条件的边际贡献可分离。", "表注")

# 顺序插入到 E.13 汇总表与表注之后：改为将块插到 ref（E.13表注）之后
# 当前 add_* 是追加到文末；把它们移到 ref 之后
body = sup.element.body
new_nodes = []
capture = False
for child in list(body):
    tag = child.tag.split('}')[1]
    if tag == 'p':
        from docx.text.paragraph import Paragraph
        if full_text(Paragraph(child, sup)).startswith("E.14 因果级证据"):
            capture = True
    if capture:
        new_nodes.append(child)
anchor = ref._p
for node in new_nodes:
    body.remove(node)
    anchor.addnext(node)
    anchor = node
sup.save("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")
print("E.14 已写入并归位")

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
            pp = parent.getparent().getparent()
            has_text = any(t.text for t in pp.findall('.//' + qn('w:t')))
            if not has_text:
                pp.getparent().remove(pp)
            else:
                parent.remove(dl)
            continue
        parent.remove(dl)
    dd.save(dst)
accept_all("/home/work/.openclaw/workspace/投稿69_修改稿.docx", "/home/work/.openclaw/workspace/投稿69_终稿.docx")
accept_all("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx", "/home/work/.openclaw/workspace/网络补充材料_终稿.docx")
print("终稿已更新")
