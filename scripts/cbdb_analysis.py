# -*- coding: utf-8 -*-
"""实测二十二：CBDB 家族跨易代重建检验（预测二·激活测试的中国历史量化）"""
import sqlite3, csv
from collections import defaultdict
import numpy as np
from scipy import stats

BASE = "/home/work/.openclaw/workspace/实测数据/cbdb"
con = sqlite3.connect(f"{BASE}/cbdb_20261010.sqlite3")

# ---------- 1. 并查集：家族连通分量 ----------
parent = {}
def find(x):
    while parent.setdefault(x, x) != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[ra] = rb
n_edges = 0
for pid, kid in con.execute("select c_personid, c_kin_id from KIN_DATA where c_kin_id is not null"):
    union(pid, kid); n_edges += 1
comp_size = defaultdict(int)
for x in list(parent):
    comp_size[find(x)] += 1
print(f"亲属边 {n_edges}，节点 {len(parent)}，连通分量（家族） {len(comp_size)}")

# ---------- 2. 精英标记（功名/入仕）+ 年份 ----------
JINSHI = {47, 90, 136, 115}   # 進士/業進士/鄉貢進士/舉人
elite_year = {}               # personid -> 最早精英年份
is_jinshi = set()
for pid, code, y1, y2 in con.execute("select c_personid, c_status_code, c_firstyear, c_lastyear from STATUS_DATA"):
    if code in JINSHI:
        is_jinshi.add(pid)
        for y in (y1, y2):
            if y and y > 0:
                elite_year[pid] = min(elite_year.get(pid, 10**9), y)
exam_codes = {r[0] for r in con.execute("select c_entry_code from ENTRY_CODES where c_entry_desc like 'examination%'")}
exam_fam = set()
for pid, code, y in con.execute("select c_personid, c_entry_code, c_year from ENTRY_DATA"):
    if code in exam_codes:
        exam_fam.add(pid)
        if y and y > 0:
            elite_year[pid] = min(elite_year.get(pid, 10**9), y)
# 补充年份：index_year
for pid, y in con.execute("select c_personid, c_index_year from BIOG_MAIN where c_index_year is not null"):
    if pid not in elite_year and y and y > 0:
        elite_year[pid] = y
print(f"精英标记（功名∪科举入仕）人数: {len(set(elite_year) & (is_jinshi | exam_fam))}")

# ---------- 3. 跨易代重建 ----------
TRANSITIONS = [("宋→元", 1279), ("元→明", 1368), ("明→清", 1644)]
elite_ids = {pid for pid in elite_year if pid in is_jinshi or pid in exam_fam}
fam_rows = []
for tname, T in TRANSITIONS:
    pre = defaultdict(list)   # root -> [personids]
    post = defaultdict(list)
    for pid in elite_ids:
        y = elite_year.get(pid)
        if not y: continue
        r = find(pid)
        if T - 150 <= y <= T - 1: pre[r].append(pid)
        elif T <= y <= T + 150: post[r].append(pid)
    print(f"\n== {tname}（T={T}）: 前代精英家族 {len(pre)} | 后代精英家族 {len(post)}")
    for r, mem in pre.items():
        size = comp_size.get(r, 1)
        act = 0
        act += (size >= 5)                          # (a) 家族组织规模（独立资源）
        act += (any(p in is_jinshi for p in mem))   # (b) 进士/举人（独立领导）
        act += (any(p in exam_fam for p in mem))    # (c) 科举传统（共享认知框架）
        rebuilt = 1 if r in post else 0
        fam_rows.append({"transition": tname, "root": r, "size": size, "n_pre": len(mem),
                         "activation": act, "rebuilt": rebuilt})
    tab = defaultdict(lambda: [0, 0])
    for row in [x for x in fam_rows if x["transition"] == tname]:
        tab[row["activation"]][0] += row["rebuilt"]
        tab[row["activation"]][1] += 1
    for a in sorted(tab):
        rb, n = tab[a]
        print(f"   激活项 {a}: 重建 {rb}/{n} = {rb/n:.1%}")
    xs = [x["activation"] for x in fam_rows if x["transition"] == tname]
    ys = [x["rebuilt"] for x in fam_rows if x["transition"] == tname]
    rho, p = stats.spearmanr(xs, ys)
    print(f"   Spearman(激活项, 重建) rho = {rho:+.2f}, p = {p:.4f}")

print("\n== 合并三朝 ==")
tab = defaultdict(lambda: [0, 0])
for row in fam_rows:
    tab[row["activation"]][0] += row["rebuilt"]; tab[row["activation"]][1] += 1
for a in sorted(tab):
    rb, n = tab[a]
    print(f"   激活项 {a}: 重建 {rb}/{n} = {rb/n:.1%}")
xs = [x["activation"] for x in fam_rows]; ys = [x["rebuilt"] for x in fam_rows]
rho, p = stats.spearmanr(xs, ys)
print(f"   合并 Spearman rho = {rho:+.2f}, p = {p:.4f} (N = {len(fam_rows)})")
lo = [x for x in fam_rows if x["activation"] <= 1]; hi = [x for x in fam_rows if x["activation"] >= 2]
t = [[sum(x["rebuilt"] for x in hi), len(hi) - sum(x["rebuilt"] for x in hi)],
     [sum(x["rebuilt"] for x in lo), len(lo) - sum(x["rebuilt"] for x in lo)]]
odds, pf = stats.fisher_exact(t, alternative="greater")
print(f"   高激活(≥2) {t[0][0]}/{sum(t[0])} vs 低激活(≤1) {t[1][0]}/{sum(t[1])} | Fisher 单侧 p = {pf:.2e}, OR = {odds:.2f}")
with open(f"{BASE}/study12_CBDB家族重建.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(fam_rows[0].keys())); w.writeheader(); w.writerows(fam_rows)
print("已保存 study12_CBDB家族重建.csv")
