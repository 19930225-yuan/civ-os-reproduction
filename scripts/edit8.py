# -*- coding: utf-8 -*-
"""第七轮：新增《补充材料E：稳健性检验与研究设计》+ 主文补预测检验状态指引"""
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

AUTHOR = "AI编辑"; DATE = "2026-10-17T06:55:00Z"
_c = [10000]
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

# ================= 补充材料E =================
sup = Document("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")
style_ref = sup.tables[51].style

add_tracked_para(sup, "补充材料E：稳健性检验与研究设计", "Heading 2")
add_tracked_para(sup, "功能定位：本补充材料报告四项当代预测与核心命题的初步实测结果、编码体系的稳健性检验，以及后续研究设计。"
    "全部检验的数据文件（CSV）与分析脚本可公开复现。作为单人研究，本文以三重替代方案管理编码信度：（i）规则先固定再套用的规则化重编码；"
    "（ii）误分类稳健性检验（随机与对抗性推翻编码）；（iii）外部独立数据与文献的三角验证。人际盲评（金标准）仍待补充，方案见E.12。", "Normal")

add_tracked_para(sup, "E.1 预测一（阈值效应）：失国—复国事件史", "Heading 3")
add_tracked_para(sup, "设计：以“主权丧失—复国”事件为单位，X为亡国时是否存在独立于政权、有自身权威文本与组织机构、亡国后持续运作的合法性载体"
    "（教会/僧团/教团/成文法统，即5a/5b的外部代理变量），Y为至2000年是否重建独立宏观政治组织及重建用时。初测N=44，扩展后N=91（新增近代案例47个）。", "Normal")
add_tracked_para(sup, "结果：（a）合并样本X=1复国73/81、X=0复国0/10，Fisher单侧p=6.81×10⁻⁹；（b）按时代分层：近代（亡国年≥1700）64/71对0/3（p=1.85×10⁻³），"
    "前近代9/10对0/7（p=4.11×10⁻⁴），Mantel-Haenszel共同OR=∞（X=0组两层均零事件）——X效应不是时代窗口的伪装；（c）初测样本log-rank χ²=12.19，p=4.8×10⁻⁴，"
    "恢复时间中位数108年；（d）误分类稳健性：随机推翻5个编码以内，p<0.05占比100%；对抗性改判5个X=1案例后p=2.7×10⁻³；（e）Cox模型显示时代效应显著（HR=20.0，p=0.004），"
    "X因完全分离不收敛——X=0组零事件本身是阈值律的统计形态。X=1的截尾案例（苏格兰、加泰罗尼亚、魁北克、威尔士、西藏、巴勒斯坦、库尔德斯坦）均为“认同存续、窗口未开”，"
    "与“壳碎核移”形态一致。东帝汶（1975—2002）为个案层面的教科书样本：占领期间天主教会是唯一存续身份载体，最终经公投复国。", "Normal")

add_tracked_para(sup, "E.2 预测四（散居同化/离线生存能力）", "Heading 3")
add_tracked_para(sup, "设计：同一种教在“母体制度在场”（印度，Pew 2021全印调查）与“母体制度缺席/弱”（美国散居，Pew 2025留存率）条件下的代际宗教留存率对比。"
    "结果：母体在场均值96.7%对散居均值72.4%，差距24.3个百分点，Mann-Whitney单侧p=0.018。辅助证据：（a）美国华裔56%、日裔47%无宗教信仰（Pew 2022—23），"
    "为亚裔各族最高，与“空锚点+宗族依赖型血缘缺乏离线生存能力”的点名预测一致；（b）犹太人内婚率最低（39%）而留存率不低（76%）——该反直觉点支持结构互补律"
    "（拉比网络、会堂、高频仪式补偿血缘传递的弱化），而非内婚单因素解释。", "Normal")

add_tracked_para(sup, "E.3 预测二（协同效应/激活测试）", "Heading 3")
add_tracked_para(sup, "设计：10个恢复事件按激活项数（独立物资/独立领导/共享认知框架，0—3）与重建表现（0—1）编码。结果：Spearman ρ=0.86，p=0.0013。"
    "外部独立证据（与本框架无关联的灾害社会学量化研究）同向：Aldrich（2011, Natural Hazards）神户九区人口回迁研究显示，控制损毁、密度、经济与不平等后，"
    "社会资本是恢复的最强预测项；Aldrich（2012, Building Resilience）四案例（东京1923、神户1995、泰米尔纳德2004、新奥尔良2005）一致；"
    "新奥尔良Village de l'Est越南裔社区（教会=独立领导+共享认知+物资动员）回迁率与重建速度显著高于周边；Lee-Aldrich等（2022, Scientific Reports）大槌町社区中心研究同向。", "Normal")

add_tracked_para(sup, "E.4 预测三（适应模式）：探索性，降调处理", "Heading 3")
add_tracked_para(sup, "结果随编码方案翻转：主编码（犹太=吸收、伊斯兰=对抗）Fisher p=0.018；替代编码（犹太=对抗、伊斯兰=吸收）p=0.286。"
    "结论：预测三是四个预测中最弱的一个，本文将其降为“探索性推论”。后续应以“外来核心承诺在该文明核心区的最终形态”为操作化定义（而非精英行为），"
    "预先注册编码规则后重测。", "Normal")

add_tracked_para(sup, "E.5 F4限定（外部补给/传承节点）：镇压—复兴案例库", "Heading 3")
add_tracked_para(sup, "设计：11个“功能件被国家力量否定”的案例，按是否存在外部载体补给或跨代际传承节点分组。结果：有补给组8/8复兴（蒙古、苏联中亚、阿尔巴尼亚、"
    "柬埔寨、中国佛教、古巴、墨西哥、俄罗斯/波兰），无或弱补给组0/3复兴（朝鲜、东德、捷克），Fisher单侧p=0.0061。关键对照：蒙古（镇压约60年，"
    "有活佛转世节点）复兴至53%（2010普查）对朝鲜（镇压77年，封闭无补给）至今宗教人口极低。命题一的限定形式由此获得直接验证。", "Normal")

add_tracked_para(sup, "E.6 无神论化自然实验：组织载体的调节作用", "Heading 3")
add_tracked_para(sup, "共产主义实验中各国同受信仰否定，但教会组织存续度不同：波兰（教会=抵抗组织）2021年普查71.3%仍为天主教徒；俄罗斯正教认同由1990年代约37%"
    "回升至2017年71%；东德（组织被削弱）今约2/3“从未信过上帝”；捷克（剥夺最彻底）无信仰72—78%。组织载体（条件四）对信仰锚点存废的调节作用，"
    "构成结构互补律的量化证据。", "Normal")

add_tracked_para(sup, "E.7 沉积与文本保真检验", "Heading 3")
add_tracked_para(sup, "（a）古埃及“壳碎核眠”维持原判：科普特语→埃及阿拉伯语借词百余至数百（Bishai 1964核定109个，后有增补）且口语保留科普特句法构造（Ishak 1976）；"
    "古基因组比较显示现代埃及人与古埃及样本主体遗传连续（Schuenemann et al. 2017, Nature Communications）；科普特教会与科普特语礼拜存续至今——"
    "“地层覆盖未粉碎+沉积残留+后裔社群承接”三要件齐备。（b）犹太“核心承诺文本完整迁移”成立：死海古卷圣经抄本与马所拉文本高度接近（以色列文物局评价其"
    "早于已知抄本千年以上而“remarkable”）；同时应注意第二圣殿期存在文本多样性（proto-MT、前撒马利亚、七十士译本对齐三类并存），"
    "其收敛本身是5b制度化释法通道（拉比标准化）运作的结果——文本稳定性是外壳调整在奠基期即已运作的证据。", "Normal")

add_tracked_para(sup, "E.8 五条件区分度", "Heading 3")
add_tracked_para(sup, "八案例五条件Spearman相关矩阵与Cronbach α=0.71：五条件既非冗余也非无关，互补结构有构念基础。两个关键读数：（a）信仰锚点与其余四条件"
    "近乎零相关（|r|≤0.16）——信仰是独立维度，只能被补偿、不能被替代，与命题二一致；（b）血统—文化—外壳构成高共线簇（r=0.72—0.90），"
    "这符合理论预期（条件二/三正是外壳所承载与更新的对象），且核心结论不依赖三者独立：阈值律只使用外壳维度，互补律的判别对照（犹太组织2.0/外壳5.0"
    "对古埃及组织3.0/外壳0）在簇内仍可区分。", "Normal")

add_tracked_para(sup, "E.9 敏感性与阈值识别", "Heading 3")
add_tracked_para(sup, "（a）全表蒙特卡洛敏感性（40个评分随机±0.5，10000次）：F1状态与阈值律对应关系保持率100%，§2.2关键对比保持率88.7%；"
    "“≥4条件数”列对边界值敏感（不变概率仅6.9%），故该列仅作描述性辅助，不承担论证功能。（b）阈值识别：外壳评分分布中（1.0,2.0）与（2.0,3.5）区间无案例，"
    "2.0门槛应理解为“存在制度化调整接口”定性二分的数值化表述（区间阈值），其精确取值待新增案例校准（见表11第F3条）。"
    "（c）编码体系说明：各条件总分为BARS整体锚定判定，非子维度加总（见A.0.2）。", "Normal")

add_tracked_para(sup, "E.10 边界机制：分治容器面板", "Heading 3")
add_tracked_para(sup, "1947年印巴分治后各容器向本教主体同质化：孟加拉印度教徒占比22%（1951）→8.5%（2022），巴基斯坦印度教徒约15%（1947）→1.6%（1951）至今，"
    "印度穆斯林9.8%（1951）→14.2%（2011）。需注意孟加拉案例的下降主因是生育率差异与国际迁移（Journal of Religion and Demography, 2024队列研究），"
    "故该面板支持“容器同质化”，同化机制的分解留待后续。", "Normal")

add_tracked_para(sup, "E.11 留出案例（框架外检验）", "Heading 3")
add_tracked_para(sup, "亚美尼亚（5a=1,5b=1，1918/1991两度复国、认同存续1600+年）、亚述人（东方教会+阿拉姆语，失国近两千年维持族群认同）、"
    "帕西人（族内通婚约98%，留存近100%，但人口1941年11.4万→2011年5.7万，说明存续≠增长）——3/3与预测一致。", "Normal")

add_tracked_para(sup, "E.12 后续研究设计", "Heading 3")
add_tracked_para(sup, "（一）人际盲评：3名历史学/社会学研究者以补充材料A为编码手册，对8案例×5条件独立盲评，报告Krippendorff α（目标≥0.80），"
    "重点复核5a/5b/5e。（二）聚合效度：将五功能件映射至Seshat全球历史数据库变量（行政层级、文字系统、仪式频率）与历史识字率估计，"
    "检验评分与外部独立指标的相关。（三）扩充样本QCA：新增回鹘、西辽、西夏、吐蕃、高棉、祖鲁、桑海等案例，填充外壳1.5—2.5区间后重估阈值。"
    "（四）预测二深化：以家谱数据库与中国历代人物传记资料库（CBDB）做华南/华北宗族重建对照。（五）空锚点文本检验：以中国哲学书电子化计划（ctext）语料"
    "测“天命/道统”词频的跨朝代稳定性。（六）预注册公开：公开编码手册、逐案判定理由与分析脚本，邀请外部复现。", "Normal")

add_tracked_para(sup, "E.13 预测检验状态汇总", "Heading 3")
add_tracked_table(sup, [
    ["命题/预测", "主要检验", "结果", "状态"],
    ["预测一（阈值效应）", "失国—复国事件史N=91（分层+MH）", "p=6.81×10⁻⁹；两层方向一致", "强支持"],
    ["预测二（协同效应）", "恢复事件编码ρ=0.86；Aldrich系列独立证据", "p=0.0013；外部证据同向", "支持"],
    ["预测三（适应模式）", "编码交叉表（双方案）", "p=0.018 / p=0.286", "探索性（降调）"],
    ["预测四（散居同化）", "母体在场vs散居留存（Pew）", "差距24.3pp，p=0.018", "支持"],
    ["命题一限定（F4）", "镇压—复兴案例库", "8/8对0/3，p=0.0061", "直接验证"],
    ["阈值律稳健性", "蒙特卡洛±0.5", "保持率100%", "稳健"],
    ["五条件区分度", "相关矩阵+α", "α=0.71；信仰独立", "构念成立"],
], style_ref)
add_tracked_para(sup, "注：上述检验均为初步实测，样本与编码的局限见E.0与正文8.7；人际盲评（E.12第一项）完成后，相关结果方可视为对编码信度的完整确认。", "表注")
sup.save("/home/work/.openclaw/workspace/网络补充材料_修改稿.docx")
print("补充材料E 已写入")

# ================= 主文指引 =================
main = Document("/home/work/.openclaw/workspace/投稿69_修改稿.docx")
ref = None
for p in main.paragraphs:
    if p.text.startswith("四个预测相互独立"):
        ref = p; break
assert ref is not None
p = main.add_paragraph(style="Normal")
r = p.add_run("四项预测已获初步实测检验（详见补充材料E）：预测一在91个“失国—复国”事件的分层分析中获得强支持（合并Fisher p=6.81×10⁻⁹，"
    "控制时代窗口后方向不变）；预测二获恢复事件编码检验（ρ=0.86）与灾害社会学独立量化证据的支持；预测四获跨国宗教留存数据支持"
    "（母体在场效应24.3个百分点）；预测三对编码方案敏感，暂列为探索性推论。命题一的限定形式（外部补给/传承节点）亦获镇压—复兴案例库的直接验证"
    "（8/8对0/3）。这些结果是初步的：其可信度最终取决于补充材料E第E.12项人际盲评的完成。")._r
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
ref._p.addnext(p._p)
print("主文§9.4 已补检验状态指引")
main.save("/home/work/.openclaw/workspace/投稿69_修改稿.docx")

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
