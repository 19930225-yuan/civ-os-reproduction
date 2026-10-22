# 复现包（投稿69·Civ-OS 实测部分）

一键校验：`cd 复现包 && python3 scripts/verify.py`
→ 期望输出：**80 项 PASS、0 FAIL**（重算全部关键数字并与存档值逐项比对）。

![verify](https://github.com/19930225-yuan/civ-os-reproduction/actions/workflows/verify.yml/badge.svg)

## 目录结构

```
复现包/
├── scripts/          分析脚本（按执行顺序）
│   ├── verify.py             ★核心：回归校验（重算关键结果）
│   ├── empirical.py          实测1-3：事件史/散居/分治面板
│   ├── empirical2.py         实测4-6：预测三/激活/留出案例
│   ├── empirical3.py         实测7-8：编码审计/蒙特卡洛
│   ├── empirical4.py         实测12-13：时代分层/区分度
│   ├── seshat1.py            实测14：Seshat 政权面板（首期）
│   ├── abm.py                实测20：ABM 机制仿真（seed=20261017）
│   ├── kanripo_freq.py       实测21：天命/道统词频
│   ├── cbdb_analysis.py      实测22：CBDB 家族重建
│   ├── abm2_ladder.py        E.20 机制阶梯（U 型阈值：耦合 ≥0.7，seed=20261018）
│   └── gss_correction.py     GSS 编码勘误说明（study15b/16b 的映射规则）
│   └── edit*.py / revertA.py / verify6.py   论文修订脚本（跟踪修订）
├── data/             结果数据（study1-31 共 38 个 CSV：含勘误后 15b/16b/18b、study22-30 对照系列、study31 判定层重编码审计表）
│   ├── study15b_GSS修正趋势.csv / study16b_GSS代际传递矩阵_修正.csv   ★GSS 编码勘误后版本
│   └── study18b_机制阶梯.csv                                          ★E.20 机制阶梯（U 型阈值）
└── results/          （verify.py 输出即结果快照）
```

## 原始数据来源与校验

| 数据 | 来源 | 获取方式 | 校验 |
|---|---|---|---|
| Seshat 三数据集 | github.com/datasets/seshat（CC BY-NC-SA） | jsdelivr CDN 下载 | 文件见 data/（axial、mr 为原始件） |
| D-PLACE/EA | github.com/d-place/dplace-data/datasets/EA | jsdelivr 下载 variables/societies/codes/data.csv | — |
| Kanripo 古籍 | github.com/kanripo/KR*（各书仓库） | jsdelivr 下载 .txt 分卷 | 书目与仓库号见 kanripo_freq.py |
| CBDB 2026-10 | huggingface.co/datasets/cbdb/cbdb-sqlite（经 hf-mirror） | ZIP 139,431,708 字节 | SQLite SHA256=b43de31b298546ad8605ab52cd78d2a70d7b946abc01bf0d4efd18dd7853782d（与官方一致） |
| Pew 等统计 | 见实测报告"数据来源"节（引文式，手工录入 CSV） | — | 手工核对 |


## ⚠ 重要勘误（2026-10-19）

GSS 编码映射错位（部分波次 4=none/5=other，与经典编码相反）已修正：
- 旧 study15/16 **作废**，以 **study15b/16b** 为准（"归属率恒96%"系假象；修正后有归属 94.5%→70.3%、无宗教 5.1%→28.1%，与公认趋势吻合）；
- E.20 机制阶梯旧数字（一次性运行、无存档）作废，以 **abm2_ladder.py + study18b** 为准（U 型涌现需耦合强度 ≥0.7）；
- verify.py 第 10—12 节即勘误后回归断言。

## 随机性与环境

- 所有随机过程固定种子：ABM=20261017、双层ABM/机制阶梯=20261018、蒙特卡洛=7、study 分析=42；
- 环境：Python 3，scipy、statsmodels、numpy、openpyxl；
- 结果是确定性的：同数据同脚本重跑数值一致（verify.py 即证明）。

## 网络获取注意

raw.githubusercontent.com、huggingface.co、wikimedia、ctext 在部分网络不可达或禁爬：
- GitHub 文件 → 用 cdn.jsdelivr.net/gh/<owner>/<repo>@master/<file>
- HuggingFace → 用 hf-mirror.com 镜像
- ctext.org 有反爬条款（要求机构订阅），本研究未爬取，改用 Kanripo 开放语料

## verify.py 保证什么、不保证什么

**保证**：脚本→结果的计算链一致（80 项关键数字全部可重算复现）；
**不保证**：数据→事实的正确性（案例编码、事实卡仍含研究者判断）——这正是论文 §8.1/E.12 承认并以人际盲评补强的部分。

---

## 发布状态与三步（GitHub + Zenodo）

**已发布**：GitHub 仓库 github.com/19930225-yuan/civ-os-reproduction（CI 自动重跑）＋ Zenodo 双 DOI（10.5281/zenodo.23466926 复现包、10.5281/zenodo.23520081 补充材料，CC BY 4.0）。以下步骤供重传/复核时使用。

**约定：GitHub 仓库根 = 本目录（复现包/）的内容。**

### ① GitHub（自动重跑证明，10 分钟）
1. github.com 新建仓库（如 `civ-os-replication`），Public；
2. 把本目录全部内容上传（网页拖拽即可），确保 `.github/workflows/verify.yml` 在仓库根；
3. 推送后 Actions 自动运行 verify.py → 通过则显示绿勾 ✅；
4. README 顶部加徽章：`![verify](https://github.com/<用户名>/<仓库名>/actions/workflows/verify.yml/badge.svg)`

### ② Zenodo（DOI 存证）——已存证，如需新版本：上传新 zip 后发布 New Version，DOI 不变
1. osf.io 注册（可用 ORCID）→ Create Project；
2. 上传 `复现包.zip`（或分文件夹）；
3. **必须做**：Create → Registration（冻结快照）→ 得到 DOI；
4. 论文数据可用性声明写：*"All data, code, and verification materials are archived at OSF (DOI: 10.17605/OSF.IO/XXXXX); the verification suite is continuously re-run in CI (GitHub Actions, green badge)."*

### ③ 论文里怎么写（模板）
> **数据与代码可用性声明**：本研究全部数据（含原始数据获取脚本与校验和）、分析脚本及一键复现校验套件（verify.py，80 项断言）已存档于 Zenodo（复现包 DOI: 10.5281/zenodo.23466926；补充材料 DOI: 10.5281/zenodo.23520081）。校验套件在持续集成环境中自动重跑（GitHub Actions，仓库 github.com/19930225-yuan/civ-os-reproduction，状态徽章见 README 顶部）。Seshat、D-PLACE、Kanripo、CBDB 数据的使用遵循各自许可协议（CBDB 数据经官方 SHA256 校验）。

### 审稿人会怎么验
1. 下载复现包（GitHub 或 Zenodo 10.5281/zenodo.23466926）→ `python3 scripts/verify.py` → 80 项 PASS（约 2 分钟）；
2. 看 GitHub 徽章 → 绿勾（代码没有"只在作者机器上能跑"问题）；
3. 想深挖 → scripts/ 里每个实测有独立脚本，data/ 有中间数据。
