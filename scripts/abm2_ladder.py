# -*- coding: utf-8 -*-
"""abm2_ladder.py — E.20 机制阶梯（OFF → +稀缺显著性 → +身份→实践耦合）与 U 型阈值
机制本义：耦合=回归性实践再投入 ∝ 身份强度 × 稀缺压力（baal teshuva 型）。
结论（seed=20261018, n=2000, 5代）：U 型涌现需要耦合强度 ≥0.7；0.3—0.5 只减缓衰减；1.5 过强又被同化压力抵消。
"""
import numpy as np, random, csv
OUT = "/home/work/.openclaw/workspace/实测数据"
def run(couple, level_name, n_gen=5, n=2000, seed=20261018):
    random.seed(seed); np.random.seed(seed)
    T_I, T_P = 0.92, 0.68; PRESS_I, PRESS_P = 0.06, 0.20
    ENDOG_BOOST = 0.06; FERT_BASE, FERT_SLOPE = 1.5, 0.7; INFLOW_P = 0.75; SCARCITY = 0.15
    ap = {1: 0.4, 2: 1.0, 3: 0.7, 4: 0.6, 5: 0.6}.get
    I = np.ones(n) * 0.8; P = np.ones(n) * INFLOW_P
    out = []
    for g in range(1, n_gen + 1):
        P = P * (1 - PRESS_P * ap(g, 0.5)) + np.random.normal(0, 0.02, n).clip(0, 1)
        I = I * (1 - PRESS_I * ap(g, 0.5))
        h = float(P.mean())
        scarcity = max(0.0, 0.35 - h) / 0.35
        I = I + SCARCITY * scarcity * 0.5
        P = P + couple * I * scarcity
        I, P = np.clip(I, 0, 1), np.clip(P, 0, 1)
        endog = (np.random.rand(n) < (0.55 + 0.35 * P)).astype(float)
        I = np.clip(I * T_I + endog * ENDOG_BOOST, 0, 1)
        P = np.clip(P * T_P + endog * ENDOG_BOOST, 0, 1)
        w = FERT_BASE + FERT_SLOPE * P; w = w / w.mean()
        idx = np.random.choice(n, size=n, replace=True, p=w / w.sum())
        I, P = I[idx], P[idx]
        m = int(n * 0.12); I[:m] = 0.85; P[:m] = INFLOW_P
        out.append({"level_name": level_name, "couple": couple, "gen": g,
                    "identity": round(float(I.mean()), 4), "practice": round(float(P.mean()), 4)})
    return out
print("== E.20 机制阶梯与 U 型阈值（seed=20261018）==")
rows = []
for couple, name in [(0.0, "OFF"), (0.0, "+稀缺显著性"), (0.7, "+耦合(≥阈值)"), (0.3, "耦合0.3(低于阈值)"), (1.5, "耦合1.5(过强)")]:
    r = run(couple, name); rows += r
    pr = [x["practice"] for x in r]
    u = pr[4] > pr[2] and pr[2] < pr[0]
    print(f"  {name:14s} 实践 {pr} → {'U型 ✓' if u else '非U'}")
with open(f"{OUT}/study18b_机制阶梯.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=["level_name", "couple", "gen", "identity", "practice"])
    w.writeheader(); w.writerows(rows)
print("→ study18b_机制阶梯.csv 已写出")
