# -*- coding: utf-8 -*-
"""实测十四（首期）：Seshat 大样本映射——五功能件→Seshat变量，政权存续时长面板"""
import csv, math
import openpyxl
import numpy as np
from scipy import stats

BASE = "/home/work/.openclaw/workspace/实测数据/seshat"

# ---------- 1. 读取 sc_dataset（长表）→ 政权级面板 ----------
wb = openpyxl.load_workbook(f"{BASE}/sc_dataset.12.2017.xlsx", read_only=True)
ws = wb["exportdat_share"]
rows = ws.iter_rows(values_only=True)
header = next(rows)
idx = {h: i for i, h in enumerate(header)}

MAP = {
    "C1_faith":   ["Sacred Texts", "Religious literature", "Professional priesthood", "Religious levels"],
    "C3_culture": ["Script", "Written records", "History", "Fiction", "Philosophy", "Practical literature"],
    "C4_org":     ["Administrative levels", "Full-time bureaucrats", "Professional military officers",
                   "Professional soldiers", "General postal service", "Military levels"],
    "C5_shell":   ["Formal legal code", "Judges", "Courts", "Merit promotion", "Examination system"],
}
all_vars = {v for vs in MAP.values() for v in vs}
panel = {}
for r in rows:
    nga, pol, var, val = r[0], r[1], r[idx["Variable"]], r[idx["Value From"]]
    if var in all_vars and pol:
        d = panel.setdefault((nga, pol), {})
        if isinstance(val, (int, float)):
            d[var] = max(d.get(var, 0), float(val))
        elif val == "present":
            d[var] = max(d.get(var, 0), 1.0)
        elif val == "absent":
            d.setdefault(var, 0.0)

# ---------- 2. mr_dataset：时长 + MSP ----------
mr = {}
with open(f"{BASE}/mr_dataset.04.2021.csv") as f:
    for row in csv.DictReader(f):
        try:
            start, end = int(row["Start"]), int(row["End"])
        except Exception:
            continue
        mr.setdefault(row["PolID"], {"span": 0, "MSP": None, "afterlife": None})
        mr[row["PolID"]]["span"] = max(mr[row["PolID"]]["span"], end - start)
        for k, col in [("MSP", "MSP"), ("afterlife", "afterlife")]:
            try:
                v = float(row[col])
                if mr[row["PolID"]][k] is None:
                    mr[row["PolID"]][k] = v
                else:
                    mr[row["PolID"]][k] = max(mr[row["PolID"]][k], v)
            except Exception:
                pass

# ---------- 3. 合并 + 指数 ----------
def z(vals):
    a = np.array(vals, dtype=float)
    sd = a.std(ddof=1)
    return (a - a.mean()) / sd if sd > 0 else a * 0

recs = []
for (nga, pol), vals in panel.items():
    rec = {"NGA": nga, "Polity": pol}
    ok = True
    for comp, vs in MAP.items():
        got = [vals[v] for v in vs if v in vals]
        rec[comp] = np.mean(got) if got else None
        if rec[comp] is None:
            ok = False
    if not ok:
        continue
    info = mr.get(pol)
    if info:
        rec["span"] = info["span"]; rec["MSP"] = info["MSP"]; rec["afterlife"] = info["afterlife"]
    else:
        rec["span"] = None; rec["MSP"] = None; rec["afterlife"] = None
    recs.append(rec)

comps = ["C1_faith", "C3_culture", "C4_org", "C5_shell"]
for c in comps + (["MSP"] if any(r["MSP"] is not None for r in recs) else []):
    vals = [r[c] for r in recs if r[c] is not None]
    zz = z(vals)
    it = iter(zz)
    for r in recs:
        if r[c] is not None:
            r[c + "_z"] = next(it)

with open(f"{BASE}/seshat_polity_panel.csv", "w", newline="", encoding="utf-8-sig") as f:
    fields = ["NGA", "Polity", "span", "MSP", "afterlife"] + comps + [c + "_z" for c in comps]
    w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(recs)

print("== 实测十四（首期）：Seshat 政权面板 ==")
print(f"政权级观测 N = {len(recs)}（有可比变量的政权-地区单元）")
with_span = [r for r in recs if r["span"] is not None]
print(f"其中可与时长合并（mr_dataset）N = {len(with_span)}")

def spearman(x, y):
    rr = [r for r in with_span if r[x] is not None and r.get(y) is not None]
    rho, p = stats.spearmanr([r[x] for r in rr], [r[y] for r in rr])
    return rho, p, len(rr)

print("\n与政权存续时长的 Spearman 相关:")
for c in comps:
    rho, p, n = spearman(c + "_z", "span")
    print(f"  {c:<10} rho = {rho:+.2f} (p = {p:.4f}, n = {n})")
rho, p, n = spearman("MSP", "span")
print(f"  {'MSP(条件一外部)':<10} rho = {rho:+.2f} (p = {p:.4f}, n = {n})")

# 组合指数（C1+C5）与长时段存续
from statsmodels.discrete.discrete_model import Logit
import statsmodels.api as sm
rr = [r for r in with_span if all(r[c] is not None for c in comps)]
y = np.array([1 if r["span"] >= 200 else 0 for r in rr])
X = np.column_stack([[r[c + "_z"] for r in rr] for c in comps])
X = sm.add_constant(X)
try:
    m = Logit(y, X).fit(disp=0)
    print(f"\nLogit: P(存续≥200年) ~ C1+C3+C4+C5 (N={len(rr)}, 阳性率{y.mean():.0%})")
    for name, coef, p in zip(["const"] + comps, m.params, m.pvalues):
        print(f"  {name:<10} coef = {coef:+.2f}, p = {p:.3f}")
    print(f"  伪R² = {m.prsquared:.3f}")
except Exception as e:
    print("Logit 异常:", e)

# 轴心时代数据集：统治者非神（5a代理）
import collections
ax = {}
with open(f"{BASE}/axial_dataset.05.2018.csv") as f:
    for row in csv.DictReader(f):
        nga = row["NGA"]
        try:
            rng = float(row["5. Rulers not gods"]); s = float(row["sum"])
        except Exception:
            continue
        ax.setdefault(nga, []).append((rng, s))
if ax:
    xs = []; ys = []
    for nga, lst in ax.items():
        xs.append(np.mean([v[0] for v in lst])); ys.append(np.mean([v[1] for v in lst]))
    rho, p = stats.spearmanr(xs, ys)
    print(f"\n轴心数据集（NGA层 N={len(ax)}）：'统治者非神'（≈5a代理）× 社会复杂度总分 rho = {rho:+.2f} (p = {p:.3f})")
