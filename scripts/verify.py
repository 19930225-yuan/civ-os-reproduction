# -*- coding: utf-8 -*-
"""
verify.py — 复现校验脚本
重算全部关键结果并与存档值比对（回归测试）。
运行: python3 verify.py    全部 PASS 即结果可复现。
"""
import csv, math, sys
import numpy as np
from scipy import stats

DATA = "data"
checks = []
def check(name, computed, expected, tol=1e-6):
    if isinstance(expected, str) and not isinstance(computed, (int, float, np.integer, np.floating)):
        ok = str(computed) == expected
    elif isinstance(expected, (int, np.integer)):
        ok = int(computed) == int(expected)
    elif isinstance(expected, str):
        ok = str(computed) == expected
    else:
        ok = abs(float(computed) - float(expected)) <= tol
    checks.append((name, computed, expected, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: 计算={computed} 存档={expected}")

def load(name):
    return list(csv.DictReader(open(f"{DATA}/{name}", encoding="utf-8-sig")))

print("== 1. 失国—复国事件史（study1/9）==")
s1 = load("study1_失国复国事件史.csv")
ev1 = sum(1 for r in s1 if r["X_制度化合法性载体"] == "1" and r["事件"] == "1")
n1 = sum(1 for r in s1 if r["X_制度化合法性载体"] == "1")
ev0 = sum(1 for r in s1 if r["X_制度化合法性载体"] == "0" and r["事件"] == "1")
n0 = sum(1 for r in s1 if r["X_制度化合法性载体"] == "0")
check("初测 N", len(s1), 44)
check("X=1 复国/总数", f"{ev1}/{n1}", "30/35", tol=0)
p = stats.fisher_exact([[ev1, n1-ev1], [ev0, n0-ev0]], alternative="greater")[1]
check("初测 Fisher p", round(p, 9), 2.82e-6, tol=5e-8)
s9 = load("study9_扩展事件史_时代分层.csv")
check("扩展 N", len(s9), 91)
a1 = sum(1 for r in s9 if r["X"] == "1" and r["复国"] == "1"); b1 = sum(1 for r in s9 if r["X"] == "1" and r["复国"] == "0")
c1 = sum(1 for r in s9 if r["X"] == "0" and r["复国"] == "1"); d1 = sum(1 for r in s9 if r["X"] == "0" and r["复国"] == "0")
p = stats.fisher_exact([[a1, b1], [c1, d1]], alternative="greater")[1]
check("扩展合并 Fisher p", f"{p:.2e}", "6.81e-09", tol=0)
check("X=0 复国数", c1, 0)

print("== 2. 散居留存（study2）==")
s2 = load("study2_母体在场vs散居留存.csv")
insitu = [float(r["代际宗教留存率(%)"]) for r in s2 if r["母体制度"] == "在场"]
dias = [float(r["代际宗教留存率(%)"]) for r in s2 if r["母体制度"] != "在场"]
check("母体在场均值", round(np.mean(insitu), 1), 96.7, tol=0.05)
check("散居均值", round(np.mean(dias), 1), 72.4, tol=0.05)
check("差距(pp)", round(np.mean(insitu) - np.mean(dias), 1), 24.3, tol=0.05)
p = stats.mannwhitneyu(insitu, dias, alternative="greater")[1]
check("Mann-Whitney p", round(p, 3), 0.018, tol=0.002)

print("== 3. 激活测试（study5）==")
s5 = load("study5_预测二_激活测试编码.csv")
rho, p = stats.spearmanr([float(r["激活项数"]) for r in s5], [float(r["重建表现"]) for r in s5])
check("激活测试 N", len(s5), 10)
check("激活测试 rho", round(rho, 2), 0.86, tol=0.01)
check("激活测试 p", round(p, 4), 0.0013, tol=0.0005)

print("== 4. 镇压—复兴（study8）==")
s8 = load("study8_镇压复兴案例库.csv")
ar = sum(1 for r in s8 if r["外部补给/传承节点"].startswith("有") and r["是否复兴"] == "1")
an = sum(1 for r in s8 if r["外部补给/传承节点"].startswith("有") and r["是否复兴"] == "0")
br = sum(1 for r in s8 if r["外部补给/传承节点"].startswith(("无", "弱")) and r["是否复兴"] == "1")
bn = sum(1 for r in s8 if r["外部补给/传承节点"].startswith(("无", "弱")) and r["是否复兴"] == "0")
check("有补给 复兴", f"{ar}/{ar+an}", "8/8", tol=0)
check("无补给 复兴", f"{br}/{br+bn}", "0/3", tol=0)
p = stats.fisher_exact([[ar, an], [br, bn]], alternative="greater")[1]
check("镇压-复兴 Fisher p", round(p, 4), 0.0061, tol=0.0005)

print("== 5. Seshat 转型配对（基线校正）==")
sT = load("seshat_transition_pairs.csv")
y = np.array([float(r["C3_post"]) - float(r["C3_pre"]) for r in sT])
X = np.column_stack((np.ones(len(y)), [float(r["C3_pre"]) for r in sT], [float(r["C5_pre"]) for r in sT]))
import statsmodels.api as sm
m = sm.OLS(y, X).fit()
check("转型配对 N", len(sT), 130)
check("C5→ΔC3 系数", round(m.params[2], 3), 0.117, tol=0.01)
check("C5→ΔC3 p", round(m.pvalues[2], 3), 0.013, tol=0.005)

print("== 6. CBDB 家族重建（study12）==")
s12 = load("study12_CBDB家族重建.csv")
tab = {}
for r in s12:
    a = int(r["activation"])
    t = tab.setdefault(a, [0, 0])
    t[0] += int(r["rebuilt"]); t[1] += 1
check("CBDB 观测 N", len(s12), 46622)
check("激活1项重建率(%)", round(tab[1][0]/tab[1][1]*100, 1), 0.1, tol=0.1)
check("激活3项重建率(%)", round(tab[3][0]/tab[3][1]*100, 1), 24.0, tol=1.0)
hi = [r for r in s12 if int(r["activation"]) >= 2]; lo = [r for r in s12 if int(r["activation"]) < 2]
t2 = [[sum(int(r["rebuilt"]) for r in hi), len(hi)-sum(int(r["rebuilt"]) for r in hi)],
      [sum(int(r["rebuilt"]) for r in lo), len(lo)-sum(int(r["rebuilt"]) for r in lo)]]
odds, p = stats.fisher_exact(t2, alternative="greater")
check("高激活 OR", round(odds, 1), 13.7, tol=0.5)
check("高激活 Fisher p", f"{p:.1e}", "1.3e-59", tol=0)

print("== 7. 词频（study11）==")
s11 = load("study11_天命道统词频.csv")
with_tianming = sum(1 for r in s11 if float(r["天命_每万字"]) > 0)
check("含'天命'的典籍数", with_tianming, 11)
pre_qin = [float(r["道統_每万字"]) for r in s11 if "先秦" in r["朝代"] or "周" in r["朝代"]]
check("先秦'道统'出现次数", sum(1 for x in pre_qin if x > 0), 0)

print("== 8. 相关存档值 ==")
check("study9 近代层 X=1 复国", sum(1 for r in s9 if r["时代"] == "近代(≥1700)" and r["X"] == "1" and r["复国"] == "1"), 64)
check("study9 前近代层 X=0 复国", sum(1 for r in s9 if r["时代"] == "前近代(<1700)" and r["X"] == "0" and r["复国"] == "1"), 0)


print("== 9. 更替年表（study14）==")
s14 = load("study14_历史更替年表.csv")
import statistics
endo = [float(r["更替年数"]) for r in s14 if r["机制"].startswith("内生")]
exo = [float(r["更替年数"]) for r in s14 if r["机制"].startswith("外生")]
check("内生中位数(年)", round(statistics.median(endo), 1), 75.0, tol=0.05)
check("外生中位数(年)", round(statistics.median(exo), 1), 275.0, tol=0.05)
p = stats.mannwhitneyu(endo, exo, alternative="less")[1]
check("内生<外生 p", round(p, 3), 0.043, tol=0.005)

print("== 10. GSS 修正趋势（study15b，编码勘误后）==")
s15 = load("study15b_GSS修正趋势.csv")
none72 = float(s15[0]["无宗教%"]); none22 = float(s15[-1]["无宗教%"])
check("1972 无宗教(%)", none72, 5.1, tol=0.05)
check("2022 无宗教(%)", none22, 28.1, tol=0.05)
check("2022 有归属(%)", float(s15[-1]["有归属%"]), 70.3, tol=0.05)
slope, i, r, p, se = stats.linregress([int(x["year"]) for x in s15], [float(x["有归属%"]) for x in s15])
check("归属斜率(/年)", round(slope, 3), -0.461, tol=0.005)
check("归属斜率 p", round(p, 4), 0.0005, tol=0.0003)
slope2, _, _, p2, _ = stats.linregress([int(x["year"]) for x in s15], [float(x["出席0-9"]) for x in s15])
check("出席斜率(/年)", round(slope2, 4), -0.0288, tol=0.0005)

print("== 11. GSS 代际传递矩阵（study16b，勘误后）==")
s16 = load("study16b_GSS代际传递矩阵_修正.csv")
m = {r["relig16"]: r for r in s16}
check("新教留存(%)", float(m["新教"]["新教"]), 79.7, tol=0.05)
check("天主教留存(%)", float(m["天主教"]["天主教"]), 67.8, tol=0.05)
check("犹太教留存(%)", float(m["犹太教"]["犹太教"]), 79.8, tol=0.05)
check("无宗教留存(%)", float(m["无宗教"]["无宗教"]), 66.3, tol=0.05)
check("无宗教→新教(%)", float(m["无宗教"]["新教"]), 23.1, tol=0.05)

print("== 12. 双层 ABM（study18/18b）==")
s18 = load("study18_ABM双层.csv")
dI = float(s18[-1]["identity"]) - float(s18[0]["identity"])
dP = float(s18[-1]["practice"]) - float(s18[0]["practice"])
check("Δ实践", round(dP, 3), -0.230, tol=0.005)
check("Δ信仰", round(dI, 3), -0.081, tol=0.005)
check("实践塌得更快", abs(dI) < abs(dP), True, tol=0)
s18b = load("study18b_机制阶梯.csv")
def traj(name):
    return [float(x["practice"]) for x in s18b if x["level_name"] == name]
u07 = traj("+耦合(≥阈值)"); u03 = traj("耦合0.3(低于阈值)"); off = traj("OFF")
check("OFF 单调衰减", (off[0] > off[2] > off[4]) if len(off) == 5 else False, True, tol=0)
check("couple=0.7 U型", u07[4] > u07[2] and u07[2] < u07[0], True, tol=0)
check("couple=0.3 非U", not (u03[4] > u03[2] and u03[2] < u03[0]), True, tol=0)

print("== 13. 更替残余普遍性（study19）==")
s19 = load("study19_更替残余普遍性.csv")
check("更替事件数", len(s19), 14)
check("完全清除(强度0)数", sum(1 for r in s19 if float(r["残余强度(0-3)"]) == 0), 0)

print("== 14. 中国信仰结构与冲击强化（study20/21）==")
s20 = load("study20_中国信仰结构.csv")
fo = [r for r in s20 if r["对象"] == "佛或菩萨"][0]
check("佛或菩萨(%)", float(fo["比例%"]), 15.6, tol=0.05)
s21 = load("study21_冲击强化事件表.csv")
check("冲击事件数", len(s21) >= 5, True, tol=0)
sup21 = sum(1 for r in s21 if "支持" in r["判定"])
check("强化判定含'支持'数", sup21 >= 4, True, tol=0)



print("== 15. GSS 信仰层趋势（study15c，GOD 定审）==")
s15c = load("study15c_GSS信仰层趋势_GOD定审.csv")
got = {int(r["year"]): r for r in s15c}
check("god 2000 信神(%)", float(got[2000]["信神%(≥5,有效)"]), 82.3, tol=0.05)
check("god 2022 信神(%)", float(got[2022]["信神%(≥5,有效)"]), 66.3, tol=0.05)
check("god 2022 确信(%)", float(got[2022]["确信%(=6,有效)"]), 50.2, tol=0.05)
sl, _, _, pg, _ = stats.linregress([2000, 2010, 2018, 2022], [float(got[y]["信神%(≥5,有效)"]) for y in [2000, 2010, 2018, 2022]])
check("信神斜率(/年)", round(sl, 3), -0.672, tol=0.005)
check("1972 god 缺失", got[1972]["god_N"], 0)



print("== 16. 四形态重编码与跨国tau（study22/23）==")
s22 = load("study22_四形态重编码与唤醒测试.csv")
check("study22 N", len(s22), 14)
check("边界/复合标记数", sum(1 for r in s22 if r["边界标记"]), 9)
wake = [(r["形态"].split("(")[0].split(":")[0], r["唤醒类型"]) for r in s22]
check("核亡仅外部", all("外部" in w for f, w in wake if f == "核亡"), True, tol=0)
check("核续无唤醒事件", all("未断" in w for f, w in wake if f.startswith("核续")), True, tol=0)
s23 = load("study23_跨国tau三角验证_Pew2024.csv")
check("study23 N", len(s23), 7)



print("== 17. 核续衰减两段律（study24）==")
s24 = load("study24_核续衰减律_分治容器面板.csv")
m = {r["序列"]: r for r in s24}
check("印度穆斯林速率(%)", float(m["印度-穆斯林占比"]["年均相对速率(%)"]), 0.61, tol=0.01)
check("孟加拉印度教速率(%)", float(m["孟加拉-印度教徒占比"]["年均相对速率(%)"]), -1.30, tol=0.01)
check("巴基斯坦平台", m["巴基斯坦-印度教徒占比"]["半衰期(年)"], "平台", tol=0)
check("孟加拉半衰期(年)", int(m["孟加拉-印度教徒占比"]["半衰期(年)"]), 53, tol=1)



print("== 18. 同化效率对称对照（study25）==")
s25 = load("study25_同化效率对称对照.csv")
check("study25 N", len(s25), 5)
check("历史方向性条目", sum(1 for r in s25 if any("支持推论A" in v for v in r.values())), 1)



print("== 19. 征服者吸收与辐射模式（study26/27）==")
s26 = load("study26_征服者吸收对照.csv")
weak = [r for r in s26 if r["锚定态"].startswith("弱")]
check("study26 N", len(s26), 12)
check("弱锚被吸收/换核", sum(1 for r in weak if "吸收" in r["判定"] or "换核" in r["判定"]), 11)
check("满锚免疫", sum(1 for r in s26 if r["锚定态"].startswith("满") and r["判定"] == "免疫"), 1)
s27 = load("study27_辐射模式对照.csv")
check("study27 N", len(s27), 5)



print("== 20. 拉德克利夫边界配对（study28/crosswalk）==")
s28 = {r["检验"]: r for r in load("study28_拉德克利夫边界配对分析.csv")}
check("配对背离均值(pp)", float(s28["贴边配对背离"]["值"]), -80.8, tol=0.1)
check("侧效应MW p", float(s28["侧效应-MW"]["值"]), 3.69e-05, tol=1e-6)
check("crosswalk N", len(load("crosswalk_radcliffe.csv")), 21)



print("== 21. 散居对照与份额核对（study29/30）==")
s29 = load("study29_东南亚华裔份额核对.csv")
check("study29 N", len(s29), 10)
mal = [r for r in s29 if "马来西亚-华裔" in r["对象"]]
check("马来西亚1957值", any("37.7" in r["份额"] for r in mal), True, tol=0)
s30 = load("study30_散居三群体对照.csv")
check("study30 N", len(s30), 19)
check("犹太分层条目", sum(1 for r in s30 if "正统" in r["群体"]), 2)


n_fail = sum(1 for *_, ok in checks if not ok)
print(f"\n{'='*40}\n总计 {len(checks)} 项 | PASS {len(checks)-n_fail} | FAIL {n_fail}")
print(">>> 全部结果可复现 ✓" if n_fail == 0 else ">>> 存在不一致 ✗（请核对数据与脚本版本）")
sys.exit(1 if n_fail else 0)
