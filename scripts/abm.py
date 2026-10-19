# -*- coding: utf-8 -*-
"""实测二十：ABM 机制仿真实验——五功能件微观规则下的阈值律与互补律涌现检验
设计原则：微观规则只包含"机制假设"（实践载体断裂按绑定度折损传递效率），
不包含"结论"（阈值与互补必须从代际复利动态中涌现，而非硬编码）。"""
import csv, math, random
import numpy as np

random.seed(20261017)
np.random.seed(20261017)
OUT = "/home/work/.openclaw/workspace/实测数据"

# ---- 微观规则 ----
# 个体：identity∈{0,1} 是否持有核心承诺；practice∈{0,1} 是否处于现行实践载体
# 文明参数（0—1）：b 信仰锚点 | k 血缘边界 | c 文化强化 | o 组织能力 | s 外壳调整
# 每代传递：P(子代持核心) = σ(base + wb·b + wk·k + wc·c·载体在场 + wo·o·宏观在场 + wp·practice)
# 冲击：政权崩溃→宏观o消失、旧载体不可用；若s高，比例s的个体完成"载体重编码"（壳碎核移）；
#       否则载体断裂使 practice=0，传递效率按绑定度(1-s)折损——折损代际复利。
# 重建：认同份额≥r 且 o·(0.5+0.5s) ≥ 0.3 → 宏观重建（复国）。
WB, WK, WC, WO, WP, BASE = 1.2, 1.0, 0.8, 0.6, 0.7, -1.6
R_RESTORE = 0.35

def sigma(x):
    return 1.0 / (1.0 + np.exp(-x))

def run_civ(b, k, c, o, s, n_agents=800, t_shock=20, t_end=60, reps=40):
    finals, restores = [], 0
    for _ in range(reps):
        share = 1.0          # 认同者份额（代际更替模型）
        carrier = 1.0        # 实践载体覆盖率
        regime = 1
        for t in range(t_end):
            if t == t_shock:
                regime = 0
                carrier = s  # 外壳调整：s 比例完成载体重编码，其余载体断裂
            p_trans = float(sigma(BASE + WB * b + WK * k + WC * c * (0.4 + 0.6 * regime)
                                  + WO * o * regime + WP * carrier))
            p_trans *= (1.0 - (1.0 - s) * 0.55 * (1 - carrier))   # 绑定折损（代际复利来源）
            p_adopt = 0.01 + 0.06 * carrier                        # 背景皈依（可忽略的涓流）
            P = share * p_trans + (1 - share) * p_adopt
            share = float(np.random.binomial(n_agents, min(max(P, 0.0), 1.0)) / n_agents)
            if regime == 0 and share >= R_RESTORE and o * (0.5 + 0.5 * s) >= 0.3:
                regime = 1
                carrier = 1.0
                restores += 1
        finals.append(share)
    return float(np.mean(finals)), restores / reps

# ---- 八案例参数（论文评分/5，外壳用5a—5e合计/5）----
CASES = {
    "犹太":   (0.9, 0.9, 0.85, 0.4, 1.0),
    "中华":   (0.5, 0.9, 0.90, 1.0, 0.9),
    "日本":   (0.3, 0.5, 0.80, 0.9, 1.0),
    "基督教": (0.9, 0.4, 0.55, 0.9, 0.7),
    "印度":   (0.8, 0.6, 0.70, 0.7, 0.7),
    "伊斯兰": (1.0, 0.5, 0.70, 0.9, 0.4),
    "拜占庭": (0.5, 0.2, 0.45, 0.5, 0.2),
    "古埃及": (0.5, 0.4, 0.35, 0.6, 0.0),
}
print("== 实测二十：ABM 机制仿真——八案例参数复现检验 ==")
print(f"{'案例':<6} {'末代认同份额':>10} {'崩溃后重建率':>10}  历史结局")
HIST = {"犹太": "壳碎核移（存续）", "中华": "壳碎核移（存续）", "日本": "存续（未完整受测）",
        "基督教": "存续（载体转移）", "印度": "存续", "伊斯兰": "存续（调整受阻）",
        "拜占庭": "壳碎核僵", "古埃及": "壳碎核眠/亡"}
results = {}
for name, (b, k, c, o, s) in CASES.items():
    f, r = run_civ(b, k, c, o, s)
    results[name] = (f, r)
    print(f"{name:<6} {f:>10.3f} {r:>10.2f}  {HIST[name]}")

# 相关：末代认同份额 × 历史存续排序
from scipy import stats
rank_hist = {"犹太": 1, "中华": 1, "日本": 1, "基督教": 1, "印度": 1, "伊斯兰": 1, "拜占庭": 0.4, "古埃及": 0}
rho, p = stats.spearmanr([results[n][0] for n in CASES], [rank_hist[n] for n in CASES])
print(f"\n模拟末代认同 × 历史结局排序: Spearman rho = {rho:+.2f}, p = {p:.4f}")

# ---- 相图：外壳s × 信仰b（其余取中位）----
print("\n== 相图：末代认同份额（行=外壳s，列=信仰b）==")
grid_s = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
grid_b = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
rows = []
print("  s\\b " + "".join(f"{b:>6.1f}" for b in grid_b))
for s in grid_s:
    line = f" {s:>4.1f}"
    for b in grid_b:
        f, _ = run_civ(b, 0.5, 0.5, 0.5, s, reps=20)
        rows.append({"s": s, "b": b, "final_identity": f})
        ch = "#" if f >= 0.7 else ("+" if f >= 0.4 else ("." if f >= 0.15 else " "))
        line += f"{f:>6.2f}"
    print(line)
with open(f"{OUT}/study10_ABM相图.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["s", "b", "final_identity"]); w.writeheader(); w.writerows(rows)

# ---- 互补检验：弱点补偿仅在外壳≥阈值时生效 ----
print("\n== 互补检验：低信仰(0.2)下的'补偿'是否依赖外壳 ==")
for s in [0.1, 0.3, 0.5, 0.7, 0.9]:
    f_low, _ = run_civ(0.2, 0.3, 0.3, 0.3, s, reps=20)   # 全弱
    f_comp, _ = run_civ(0.2, 0.9, 0.9, 0.9, s, reps=20)  # 信仰弱、其余强
    print(f"  s={s:.1f}: 全弱 {f_low:.2f} | 弱信仰+强血统/文化/组织 {f_comp:.2f} | 补偿增益 {f_comp-f_low:+.2f}")
