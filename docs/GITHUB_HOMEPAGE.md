# GitHub 仓库主页文案（Repository Homepage Copy）

> 供在 GitHub 建仓时直接粘贴使用。含 Short description、Topics、About 与 Release 文案。

---

## 1. Short description（仓库简介栏）

GitHub 的 *Description* 字段**上限 350 字符**。以下三版任选，均在此限内。

### 版 A — 学术中性（推荐）

```
A fault-free curved-braking dataset for testing whether a detection method — or an AI agent — can resist a deliberately fabricated fault. Ground truth known. Adversarial/robustness probe for automotive modal data. CC BY 4.0.
```
（约 230 字符）

### 版 B — 强调智能体评测

```
Benchmark for validating AI agents and detection criteria against fabricated faults: a fault-free vehicle braked while cornering, producing a brake-pull-like yaw signature. Tests causal reasoning, not pattern-matching. CC BY 4.0.
```
（约 228 字符）

### 版 C — 极简

```
Adversarial benchmark for automotive brake-pull detection: fault-free curved-braking data that looks like a fault. Probe for detection criteria and AI-agent reasoning. CC BY 4.0.
```
（约 178 字符）

---

## 2. Topics（仓库标签）

GitHub Topics 用小写、连字符分隔。建议**全选 20 个**（上限即 20）：

```
benchmark
adversarial-testing
automotive
fault-detection
modal-analysis
brake-pull
signal-processing
anomaly-detection
machine-learning-benchmark
ai-agent
ai-evaluation
robustness-testing
out-of-distribution
confounding-factors
sensor-data
vibration-analysis
real-world-data
dataset
cc-by-4
vehicle-diagnostics
```

**分组说明**（便于你按需增删）：

| 类别 | Topics |
|---|---|
| 基准/评测 | `benchmark` `ai-evaluation` `machine-learning-benchmark` |
| 对抗/鲁棒 | `adversarial-testing` `robustness-testing` `out-of-distribution` |
| 领域 | `automotive` `vehicle-diagnostics` `brake-pull` `modal-analysis` `vibration-analysis` |
| 方法 | `fault-detection` `anomaly-detection` `signal-processing` `confounding-factors` |
| 智能体 | `ai-agent` |
| 数据属性 | `real-world-data` `sensor-data` `dataset` |
| 许可 | `cc-by-4` |

---

## 3. About 区块（仓库右上角）

GitHub 的 *About* = Description + Website + Topics。建议：

| 字段 | 内容 |
|---|---|
| **Description** | 用上面版 A（学术中性） |
| **Website** | 留空，或填随附论文的链接（发布后补） |
| **Topics** | 用上面 20 个 |
| **Include in the home page** | 勾选 **Releases**、**Packages**（如不用可取消）、**Used by**（自动） |

---

## 4. Release 文案（v1.0.0）

在 GitHub 建 Tag/Release 时使用：

**Tag**: `v1.0.0`
**Release title**: `v1.0.0 — Initial release`

**Release notes**:

```markdown
## YQAJ Brake-Pull Adversarial Benchmark v1.0.1

A fault-free, curved-braking dataset for testing whether a detection method — or an
AI agent — can resist a *deliberately fabricated* fault.

### What's inside

| File | Records | Role |
|---|---|---|
| `datasets/adversarial_curve_braking_38.json` | 38 | Adversarial test set; ground truth = **not** brake pull |
| `paper/paper.zh.md` / `.html` | — | The full falsification-oriented analysis of this test |
| `paper/fig1-adversarial-test.png` | — | Figure 1: the adversarial test schematic |

### Highlights

- **Known ground truth** — the vehicle had no brake-pull fault; the yaw signature is caused
  by cornering.
- **Discriminative power** — on the same data, C1 (absolute threshold) reports a 31.6%
  false-positive rate, while C3 (ratio + confounder exclusion) reports 2.6%.
- **Reproducible** — `baseline/criteria.py` implements C1/C2/C3 with the Python standard
  library only.
- **Agent-validation ready** — see `docs/INTENDED_USE.md` for a blind-test protocol and
  scoring rubric.
- **Paper included** — the full analysis is in `paper/`, including an erratum (Appendix F)
  documenting a corrected, previously non-reproducible baseline statistic.

### What it is NOT

Small (38 records), single vehicle, single session, **no positive samples**. It is a
*specialised adversarial/robustness probe*, not a general-purpose benchmark. See
`docs/EVALUATION.md` §6 for limitations.

### License

CC BY 4.0. See `LICENSE` for the attribution format.

### Note on scope

This release ships **only** the adversarial set. The two same-vehicle ordinary-driving
baselines used during the original analysis (n=62 same-day, n=1042 history) are not
included: they do not serve the adversarial task and would offer solvers a distributional
shortcut. Baseline statistics are therefore cited from `paper/` rather than reproducible
from this repository alone.
```

---

## 5. 建仓步骤（配合上文）

```bash
cd yqaj-brake-benchmark
git remote add origin https://github.com/<account>/yqaj-brake-benchmark.git
git branch -M main
git push -u origin main

# 打 tag 并推送（发布 Release 用）
git tag -a v1.0.0 -m "Initial release: YQAJ Brake-Pull Adversarial Benchmark v1.0.0"
git push origin v1.0.0
```

推送后在 GitHub 网页：
1. 右上 **About** → 齿轮 → 填 Description、加 Topics（见 §1、§2）；
2. **Releases** → *Draft a new release* → 选 tag `v1.0.0` → 粘贴 §4 的 notes → 发布。

---

## 6. 账号可替换占位符

文案中的 `<account>` 请替换为你的 GitHub 用户名/组织名。若最终仓库名不同，也请同步替换
`yqaj-brake-benchmark`。
