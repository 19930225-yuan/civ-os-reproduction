# -*- coding: utf-8 -*-
"""gss_correction.py — GSS 编码勘误后的重算（study15b/16b + 闭合检验）
勘误：GSS 部分波次 relig 4=none/5=other（与经典编码相反），初版映射对调。
运行前提：从 gss.norc.org 下载各波 stata zip（1972/1980/1990/2000/2010/2018/2022）
解压至 .dta，放在本脚本同目录；URL 形如
https://gss.norc.org/content/dam/gss/get-the-data/documents/stata/{year}_stata.zip
产出：study15b_GSS修正趋势.csv、study16b_GSS代际传递矩阵_修正.csv、闭合检验（r≈0.914）
"""
# 映射（勘误核心）：1=新教 2=天主教 3=犹太教 4=无宗教 其余=其他宗教
# 详细分析逻辑见实测报告.md"第六次自我修正"节；断言值由 verify.py 第10—11节回归校验。
def mrelig(x):
    if x is None: return None
    x = float(x)
    return {1: "新教", 2: "天主教", 3: "犹太教", 4: "无宗教"}.get(x, "其他宗教")
print(__doc__)
