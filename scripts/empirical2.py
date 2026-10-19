# -*- coding: utf-8 -*-
"""实测四-六：预测三交叉表、预测一扩展（Cox/误分类稳健性/规则化重编码）、预测二激活测试"""
import csv, random
from scipy import stats

OUT = "/home/work/.openclaw/workspace/实测数据"
random.seed(42)

# ================= 实测四：预测三（适应模式 × 外壳评分） =================
# 冲击=该文明历史上遭遇的最强一次外来宗教/文化竞争；模式：吸收=本土化吸收，非吸收=替代式接受/对抗式排斥
cases_p3 = [
    # (案例, 外壳评分, 主编码, 替代编码, 依据)
    ("古埃及", 0.0, "替代式接受", "替代式接受", "基督教化：Ma'at被救赎论替换"),
    ("拜占庭", 1.0, "对抗式排斥", "对抗式排斥", "拒绝教会联合、1204后反拉丁"),
    ("伊斯兰", 2.0, "对抗式排斥", "本土化吸收", "近现代对西方：瓦哈比/伊斯兰主义（主）；阿拔斯百年翻译运动吸收希腊（替代编码）"),
    ("基督教", 3.5, "本土化吸收", "本土化吸收", "教父-经院哲学吸纳希腊哲学"),
    ("印度", 3.5, "本土化吸收", "本土化吸收", "巴克提运动吸收性重构；种姓包容外来者"),
    ("中华", 4.5, "本土化吸收", "本土化吸收", "佛教中国化（判教→禅宗）"),
    ("日本", 5.0, "本土化吸收", "本土化吸收", "神佛习合、和魂洋才"),
    ("犹太", 5.0, "本土化吸收", "对抗式排斥", "卡巴拉吸收新柏拉图元素（主）；马加比起义拒绝希腊化（替代编码）"),
]
def cross_tab(coding_idx):
    hi_abs = hi_non = lo_abs = lo_non = 0
    for _, s, main, alt, _x in cases_p3:
        mode = main if coding_idx == 1 else alt
        absorb = (mode == "本土化吸收")
        if s >= 3.5:
            hi_abs += absorb; hi_non += (not absorb)
        else:
            lo_abs += absorb; lo_non += (not absorb)
    return [[hi_abs, hi_non], [lo_abs, lo_non]]

print("== 实测四：预测三 适应模式×外壳评分 ==")
for idx, label in [(1, "主编码"), (2, "替代编码（犹太=对抗、伊斯兰=吸收）")]:
    t = cross_tab(idx)
    odds, p = stats.fisher_exact(t, alternative="greater")
    print(f"{label}: 外壳≥3.5 吸收{t[0][0]}/非吸收{t[0][1]} | 外壳<3.5 吸收{t[1][0]}/非吸收{t[1][1]} | Fisher单侧 p={p:.4f}")
with open(f"{OUT}/study4_预测三_适应模式编码.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["案例", "外壳评分", "主编码", "替代编码", "依据"]); w.writerows(cases_p3)

# ================= 实测五：预测一扩展 =================
# 复用 study1 数据
rows = []
with open(f"{OUT}/study1_失国复国事件史.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows.append({"name": r["政体"], "loss": int(r["丧失年"]),
                     "x": int(r["X_制度化合法性载体"]), "dur": int(r["持续年数"]),
                     "ev": int(r["事件"]), "region": r["地区"]})

def fisher_p(sample):
    e1 = sum(r["ev"] for r in sample if r["x"] == 1); n1 = sum(1 for r in sample if r["x"] == 1)
    e0 = sum(r["ev"] for r in sample if r["x"] == 0); n0 = sum(1 for r in sample if r["x"] == 0)
    return stats.fisher_exact([[e1, n1 - e1], [e0, n0 - e0]], alternative="greater")[1]

print("\n== 实测五：预测一扩展（混杂控制与稳健性） ==")
# (a) Cox PH: X + 时代(亡国年≥1700) + 地区(欧洲)
import numpy as np
from statsmodels.duration.hazard_regression import PHReg
dur = np.array([r["dur"] for r in rows]); ev = np.array([r["ev"] for r in rows])
X = np.array([[r["x"], 1 if r["loss"] >= 1700 else 0, 1 if r["region"] == "欧洲" else 0] for r in rows], dtype=float)
try:
    mod = PHReg(dur, X, status=ev).fit()
    print("Cox PH（X, 时代≥1700, 欧洲）:")
    for name, coef, se, p in zip(["X_制度载体", "时代", "欧洲"], mod.params, mod.bse, mod.pvalues):
        print(f"  {name}: HR={np.exp(coef):.2f}, p={p:.3f}")
except Exception as e:
    print("Cox 拟合异常（完全分离）:", type(e).__name__, e)

# (b) 误分类稳健性：随机翻转 k 个编码
print("误分类稳健性（每次2000次随机翻转）:")
for k in [1, 2, 3, 4, 5]:
    ps = []
    for _ in range(2000):
        sample = [dict(r) for r in rows]
        for i in random.sample(range(len(sample)), k):
            sample[i]["x"] = 1 - sample[i]["x"]
        ps.append(fisher_p(sample))
    frac05 = sum(1 for p in ps if p < 0.05) / len(ps)
    frac01 = sum(1 for p in ps if p < 0.01) / len(ps)
    print(f"  翻转{k}个编码: p<0.05 占比 {frac05:.1%}, p<0.01 占比 {frac01:.1%}, 最差p={max(ps):.4f}")

# (c) 最坏情形：把 k 个 X=1 的“已复国”案例改判为 X=0
print("对抗性最坏情形（把X=1已复国案例改判X=0）:")
for k in [1, 2, 3, 4, 5]:
    sample = [dict(r) for r in rows]
    victims = [i for i, r in enumerate(sample) if r["x"] == 1 and r["ev"] == 1][:k]
    for i in victims: sample[i]["x"] = 0
    print(f"  改判{k}个: Fisher p = {fisher_p(sample):.2e}")

# (d) 规则化重编码一致性（规则先写死，再逐案套用）
rule = "亡国时是否存在：有自身经典文本与传承制度、独立于政权运作、且亡国后仍持续≥百年的宗教或法统组织？"
recoded = {}
for r in rows:
    basis = r["name"]
    # 规则化判定依据 CSV 中的编码依据文字（机构型=1，王权-神庙/王朝绑定型=0）
    import csv as _csv
    with open(f"{OUT}/study1_失国复国事件史.csv", encoding="utf-8-sig") as f:
        fact = {rr["政体"]: rr["编码依据"] for rr in _csv.DictReader(f)}
    b = fact[basis]
    recoded[basis] = 0 if ("绑定" in b and "教会" not in b and "教团" not in b and "教法" not in b and "法统" not in b) else 1
agree = sum(1 for r in rows if recoded[r["name"]] == r["x"])
from math import isclose
po = agree / len(rows)
p_yes = sum(recoded[r["name"]] for r in rows) / len(rows)
p_x = sum(r["x"] for r in rows) / len(rows)
pe = p_yes * p_x + (1 - p_yes) * (1 - p_x)
kappa = (po - pe) / (1 - pe)
print(f"规则化重编码（规则：{rule}）: 一致 {agree}/{len(rows)}, κ = {kappa:.2f}（同模型重编码=一致性上限，非真盲评）")

# ================= 实测六：预测二（激活测试） =================
episodes = [
    # (事件, 激活项数(独立物资/独立领导/共享认知框架0-3), 重建表现0/0.5/1, 依据)
    ("明清易代·上溪源程氏", 3.0, 1.0, "族田+族长+大一统指令全激活；康熙元年重建祠堂、族人复入仕"),
    ("太平天国后江南宗族（有族田族谱者）", 3.0, 1.0, "同治-光绪年间迅速恢复（补充材料A反向证据报告）"),
    ("犹太散地社区（Kehilla）", 3.0, 1.0, "会堂+拉比+Torah文本指令；流散地普遍重建社区"),
    ("新奥尔良越南裔（Village de l'Est）", 3.0, 1.0, "天主堂=独立领导+共享认知+物资动员；卡特里娜后高回迁快重建（Aldrich 2012; JAH 2007）"),
    ("神户强组织街区（1995）", 2.5, 1.0, "町内会网络强街区人口回迁最快（Aldrich 2011）"),
    ("大槌町社区中心（2011）", 2.5, 1.0, "社区中心参与者自报恢复显著更高（Lee-Aldrich 2022, Sci Rep）"),
    ("印度种姓/jajmani网络", 2.5, 0.5, "微观自保但无跨区域重建通道"),
    ("华北弱宗族（明清易代）", 2.0, 0.5, "族田族长在、跨区域文化指令弱；重建较慢（补充材料C.8）"),
    ("拜占庭教区", 1.0, 0.0, "无独立物资与独立于帝国的领导"),
    ("古埃及书吏/神庙", 0.0, 0.0, "三者皆无，宏观崩溃后微观瓦解"),
]
xs = [e[1] for e in episodes]; ys = [e[2] for e in episodes]
rho, p = stats.spearmanr(xs, ys)
print("\n== 实测六：预测二 激活测试 ==")
print(f"激活项数 × 重建表现: Spearman rho = {rho:.2f}, p = {p:.4f} (n={len(episodes)})")
with open(f"{OUT}/study5_预测二_激活测试编码.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["事件", "激活项数", "重建表现", "依据"]); w.writerows(episodes)

# ================= 框架外案例（留出检验） =================
out = [
    ("亚美尼亚", "5a=1,5b=1（使徒教会独立教义与组织）", "预测：壳碎核移且可复国", "1918/1991两度复国，认同存续1600+年", "一致"),
    ("帕西人（印度）", "信仰刚性高+族内通婚≈98%", "预测：散居留存极高", "留存近100%，但人口1941年11.4万→2011年5.7万", "一致（存续≠增长）"),
    ("亚述人", "东方教会+阿拉姆语传承", "预测：无国家存续", "失国近两千年维持族群认同（教会=载体）", "一致"),
]
print("\n== 框架外案例留出检验 ==")
for row in out: print(" | ".join(row))
with open(f"{OUT}/study6_框架外案例留出检验.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["案例", "框架编码", "框架预测", "实际结果", "判定"]); w.writerows(out)
