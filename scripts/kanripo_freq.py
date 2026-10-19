# -*- coding: utf-8 -*-
"""实测二十一：'天命/道统'跨朝代词频时序（Kanripo 开放古籍语料，11 部典籍）"""
import json, re, csv, io, zipfile, urllib.request, time, sys

BASE = "/home/work/.openclaw/workspace/实测数据/kanripo"
import os
os.makedirs(BASE, exist_ok=True)
UA = {"User-Agent": "research"}

WORKS = [
    ("尚書",     "周（先秦）", "KR1b0001"),
    ("毛詩",     "周（先秦）", "KR1c0001"),
    ("春秋左傳", "周（先秦）", "KR1e0001"),
    ("論語",     "周（先秦）", "KR1h0004"),
    ("孟子",     "周（先秦）", "KR1h0001"),
    ("史記",     "漢",        "KR2a0001"),
    ("貞觀政要", "唐",        "KR2e0006"),
    ("昌黎集",   "唐",        "KR4c0046"),
    ("朱子語類", "宋",        "KR3a0047"),
    ("明儒學案", "清初（記明代学术）", "KR2g0046"),
    ("日知錄",   "清",        "KR3j0070"),
]
TERMS = ["天命", "道統", "天道", "佛", "禪"]
CJK = re.compile(r"[\u4e00-\u9fff]")

def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()

def repo_text_files(repo):
    d = json.loads(get(f"https://api.github.com/repos/kanripo/{repo}/contents"))
    return [x["name"] for x in d if x["name"].endswith(".txt")]

rows = []
for title, dyn, repo in WORKS:
    try:
        files = repo_text_files(repo)
    except Exception as e:
        print(f"{title}: 列目录失败 {e}", flush=True); continue
    text = []
    got = 0
    # 优先整包 zip
    try:
        zb = get(f"https://codeload.github.com/kanripo/{repo}/zip/refs/heads/master", timeout=120)
        z = zipfile.ZipFile(io.BytesIO(zb))
        for n in z.namelist():
            if n.endswith(".txt"):
                text.append(z.read(n).decode("utf-8", errors="ignore"))
        got = sum(1 for n in z.namelist() if n.endswith(".txt"))
        mode = "zip"
    except Exception:
        mode = "逐文件"
        for fn in files:
            try:
                t = get(f"https://cdn.jsdelivr.net/gh/kanripo/{repo}@master/{fn}").decode("utf-8", errors="ignore")
                text.append(t); got += 1
            except Exception:
                pass
            if got % 25 == 0 and got:
                print(f"  {title}: {got}/{len(files)}", flush=True)
    full = "\n".join(text)
    n_cjk = len(CJK.findall(full))
    rec = {"书名": title, "朝代": dyn, "仓库": repo, "文件数": got, "汉字数": n_cjk}
    for t in TERMS:
        rec[t] = full.count(t)
        rec[t + "_每万字"] = round(rec[t] / n_cjk * 10000, 2) if n_cjk else None
    rows.append(rec)
    print(f"{title}({dyn}): 文件{got}, 汉字{n_cjk}, 天命{rec['天命']}, 道統{rec['道統']} | 每万字: 天命{rec['天命_每万字']}, 道統{rec['道統_每万字']}", flush=True)

with open(f"{BASE}/study11_天命道统词频.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("已保存 study11_天命道统词频.csv")
