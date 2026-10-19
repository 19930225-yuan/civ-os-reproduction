# -*- coding: utf-8 -*-
"""实测十二：近代主权中断全样本（时代分层）+ 实测十三：五条件区分度（相关矩阵/Cronbach α）"""
import csv, itertools
from scipy import stats

OUT = "/home/work/.openclaw/workspace/实测数据"

# ===== 实测十二：扩展事件史（新增近代案例，按时代分层）=====
new_cases = [
    ("波兰(二战)", 1939, 1945, 1, "欧洲"), ("挪威(二战)", 1940, 1945, 1, "欧洲"),
    ("丹麦", 1940, 1945, 1, "欧洲"), ("荷兰", 1940, 1945, 1, "欧洲"),
    ("比利时", 1940, 1945, 1, "欧洲"), ("法国", 1940, 1944, 1, "欧洲"),
    ("希腊(二战)", 1941, 1944, 1, "欧洲"), ("南斯拉夫", 1941, 1945, 1, "欧洲"),
    ("阿尔巴尼亚(二战)", 1939, 1944, 1, "欧洲"), ("菲律宾", 1942, 1946, 1, "东南亚"),
    ("缅甸(二战)", 1942, 1948, 1, "东南亚"), ("印度尼西亚", 1942, 1949, 1, "东南亚"),
    ("朝鲜", 1910, 1945, 1, "东亚"), ("埃塞俄比亚", 1936, 1941, 1, "非洲"),
    ("爱沙尼亚", 1940, 1991, 1, "欧洲"), ("拉脱维亚", 1940, 1991, 1, "欧洲"),
    ("立陶宛", 1940, 1991, 1, "欧洲"), ("白俄罗斯", 1921, 1991, 1, "欧洲"),
    ("格鲁吉亚(苏)", 1921, 1991, 1, "西亚"), ("亚美尼亚(苏)", 1920, 1991, 1, "西亚"),
    ("阿塞拜疆", 1920, 1991, 1, "西亚"), ("哈萨克", 1920, 1991, 1, "中亚"),
    ("乌兹别克", 1924, 1991, 1, "中亚"), ("吉尔吉斯", 1926, 1991, 1, "中亚"),
    ("塔吉克", 1929, 1991, 1, "中亚"), ("土库曼", 1924, 1991, 1, "中亚"),
    ("摩尔多瓦", 1940, 1991, 1, "欧洲"), ("匈牙利", 1947, 1989, 1, "欧洲"),
    ("罗马尼亚", 1947, 1989, 1, "欧洲"), ("保加利亚", 1946, 1989, 1, "欧洲"),
    ("东德/德国统一", 1949, 1989, 1, "欧洲"), ("捷克斯洛伐克(1968)", 1968, 1989, 1, "欧洲"),
    ("柬埔寨(越南占领)", 1979, 1989, 1, "东南亚"), ("东帝汶", 1975, 2002, 1, "东南亚"),
    ("科威特(伊拉克)", 1990, 1991, 1, "西亚"), ("孟加拉", 1947, 1971, 1, "南亚"),
    ("厄立特里亚", 1962, 1993, 1, "非洲"), ("纳米比亚", 1920, 1990, 1, "非洲"),
    ("塞浦路斯", 1878, 1960, 1, "西亚"), ("马耳他", 1800, 1964, 1, "欧洲"),
    ("卡塔尔", 1916, 1971, 1, "西亚"), ("科威特(英国)", 1899, 1961, 1, "西亚"),
    ("巴林", 1880, 1971, 1, "西亚"),
    ("西藏(现代)", 1951, None, 1, "东亚"), ("巴勒斯坦", 1948, None, 1, "西亚"),
    ("库尔德斯坦", 1923, None, 1, "西亚"),
    ("满洲国", 1932, None, 0, "东亚"),
]
old = []
with open(f"{OUT}/study1_失国复国事件史.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        old.append((r["政体"], int(r["丧失年"]), int(r["复国年"]) if r["复国年"] else None,
                    int(r["X_制度化合法性载体"]), r["地区"]))
END = 2000
rows = []
for name, loss, restore, x, region in old + new_cases:
    rows.append({"政体": name, "丧失年": loss, "复国": 1 if restore else 0,
                 "持续年": (restore or END) - loss, "X": x, "地区": region,
                 "时代": "近代(≥1700)" if loss >= 1700 else "前近代(<1700)"})
with open(f"{OUT}/study9_扩展事件史_时代分层.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

print("== 实测十二：扩展事件史（时代分层）==")
print(f"总样本 N = {len(rows)}（原44 + 新增{len(new_cases)}）")
def tab(sample):
    a = sum(1 for r in sample if r["X"] == 1 and r["复国"] == 1)
    b = sum(1 for r in sample if r["X"] == 1 and r["复国"] == 0)
    c = sum(1 for r in sample if r["X"] == 0 and r["复国"] == 1)
    d = sum(1 for r in sample if r["X"] == 0 and r["复国"] == 0)
    return [[a, b], [c, d]]
strata = {}
for era in ["近代(≥1700)", "前近代(<1700)"]:
    s = [r for r in rows if r["时代"] == era]
    t = tab(s)
    odds, p = stats.fisher_exact(t, alternative="greater")
    strata[era] = t
    print(f"  {era}: X=1 复国{t[0][0]}/{t[0][0]+t[0][1]} | X=0 复国{t[1][0]}/{t[1][0]+t[1][1]} | Fisher单侧 p={p:.2e}")
# Mantel-Haenszel 共同OR
num = den = 0.0
for era, t in strata.items():
    a, b = t[0]; c, d = t[1]; n = a + b + c + d
    if n:
        num += a * d / n; den += b * c / n
print(f"  Mantel-Haenszel 共同 OR = {"∞（X=0组两层均零事件）" if den==0 else f"{num/den:.1f}"}（分层控制时代后）")
t_all = tab(rows)
odds, p_all = stats.fisher_exact(t_all, alternative="greater")
print(f"  合并: X=1 复国{t_all[0][0]}/{sum(t_all[0])} | X=0 复国{t_all[1][0]}/{sum(t_all[1])} | Fisher p={p_all:.2e}")
# 近代截尾案例（窗口未开）
cen = [r["政体"] for r in rows if r["复国"] == 0 and r["X"] == 1]
print(f"  X=1 未复国（截尾）案例：{ '、'.join(cen) }——窗口未开/国际秩序冻结，与'壳碎核移'形态一致")

# ===== 实测十三：五条件区分度 =====
tot = {
 "犹太":[4.5,4.5,4.25,2.0,5.0], "中华":[2.5,4.5,4.5,5.0,4.5], "日本":[1.5,2.5,4.0,4.5,5.0],
 "基督教":[4.5,2.0,2.75,4.5,3.5], "印度":[4.0,3.0,3.5,3.5,3.5], "伊斯兰":[5.0,2.5,3.5,4.5,2.0],
 "拜占庭":[2.5,1.0,2.25,2.5,1.0], "古埃及":[2.5,2.0,1.75,3.0,0]}
names = ["信仰","血统","文化","组织","外壳"]
print("\n== 实测十三：五条件区分度（N=8）==")
print("  Spearman 相关矩阵:")
print("        " + "  ".join(f"{n:>6}" for n in names))
for i, n1 in enumerate(names):
    row = []
    for j, n2 in enumerate(names):
        rho, _ = stats.spearmanr([v[i] for v in tot.values()], [v[j] for v in tot.values()])
        row.append(f"{rho:>6.2f}")
    print(f"  {n1:>6} " + "  ".join(row))
# Cronbach α
import numpy as np
M = np.array(list(tot.values()))
k = M.shape[1]
item_var = M.var(axis=0, ddof=1); total_var = M.sum(axis=1).var(ddof=1)
alpha = k / (k - 1) * (1 - item_var.sum() / total_var)
print(f"  Cronbach α = {alpha:.2f}")
print("  判读:", "α适中→五条件既非冗余也非无关，'互补'结构有构念基础 ✓" if 0.5 <= alpha <= 0.85 else
      ("α过高→五条件疑似同一潜变量，'互补'论被削弱 ⚠" if alpha > 0.85 else "α偏低→五条件独立性强，更需互补律说明其协同"))
