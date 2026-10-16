# YQAJ Brake-Pull Benchmark

A real-world dataset for testing whether a detection method can **resist a deliberately
constructed false fault** — an *adversarial test* for automotive modal data.

[中文说明见下方](#中文说明)

---

## What this is

A fault-free vehicle was deliberately braked **while cornering**. Cornering bends the
vehicle about both its vertical axis (yaw) and its longitudinal axis (roll), so it
produces a yaw signature that closely resembles **brake pull** (left/right braking
imbalance).

The result is a dataset that *looks like* a fault but is not one. It exists to answer a
question that ordinary fault datasets cannot:

> Can a detection method tell a genuine fault from a well-faked one?

**Ground truth is known**: the vehicle had no brake-pull fault; the yaw response is caused
by cornering. This is what makes the dataset usable as a benchmark.

---

## Intended uses

This dataset is meant to be used as a **probe**, not as a training corpus. It is small and
single-vehicle, and its value lies in the *judgement* it elicits, not in its volume.

### 1. Validating detection criteria (primary engineering use)

Test whether a brake-pull criterion survives a *fabricated* fault, not merely whether it
fires on a real one. A criterion that reports a high anomaly rate here is failing, because
the ground truth is "no fault". Compare the reference criteria (C1/C2/C3) and report both
the false-positive rate and how the criterion handles the three confounders (braking
intensity, cornering attitude, road/time drift).

### 2. Validating AI-agent capability (primary research use)

This is the use the dataset was originally built around. Because the data *looks like* a
fault while being none, it is a test of **reasoning under a deliberately misleading
premise** — a capability that ordinary accuracy metrics do not capture.

It can be used to assess whether an agent:

| Capability | What the dataset probes | Observable in |
|---|---|---|
| **Resistance to fabricated evidence** | Does the agent accept a plausible-looking signal at face value, or does it question the criterion that produced it? | Whether it reports "brake pull" |
| **Confounder awareness** | Does it notice that the yaw channel is confounded by braking intensity and cornering? | Whether it uses `YMM` for normalization and `RollMM` for discrimination |
| **Cross-source verification** | Does it bring in an independent channel / external baseline before concluding? | Whether it uses the roll channel and the history baseline |
| **Causal vs. correlational reading** | Does it distinguish "machine state" (should be persistent) from "driving path" (can appear/disappear)? | Whether it examines the time structure of hits |
| **Honest self-limitation** | Does it state what it *cannot* conclude from the data, or does it overclaim? | Whether it declares its evidential boundaries |
| **Methodological contribution** | Does it go beyond "detect/not detect" to propose and test a better criterion? | Whether it produces something like C3 |

> **Benchmarking note.** A useful protocol is a *blind* run: give the agent only the
> `records` array (not `ground_truth`, not the README), ask whether the vehicle has a
> brake-pull fault, and record the answer and reasoning. This is precisely the setup under
> which the dataset was validated (see `docs/EVALUATION.md` §2). Because the correct answer
> is "no fault", and because the yaw channel is genuinely confounded, the task
> discriminates between agents that reason about causality and agents that pattern-match
> on a single channel.

### 3. Methodological comparison

Serve as a small, fully-labelled counterexample set for comparing detection or
normalization methods (absolute thresholds, ratio metrics, regression residuals,
confounder-exclusion variants). Because the ground truth is *negative*, it exposes
false-positive behaviour that positive-only test sets hide.

### 4. Education and demonstration

Illustrate, with real data, why absolute thresholds fail under uncontrolled conditions and
why normalization and independent-channel cross-checking matter — useful in teaching
signal-processing-in-the-wild or automotive diagnostics.

### What it is *not* for

- **Training a general brake-pull classifier.** Too small, one vehicle, one session.
- **Measuring recall / coverage.** There are no positive (real-fault) samples; see
  `docs/EVALUATION.md` §6.
- **Claiming a method is "production-ready".** Passing here shows robustness to one
  fabricated fault, not general fitness.

---

## Datasets

| File | Records | Role |
|---|---|---|
| `datasets/adversarial_curve_braking_38.json` | 38 | **The adversarial test set.** One session, ground truth = *not* brake pull. |
| `datasets/same_day_baseline.json` | 62 | Same vehicle, same day, outside the session window. Strictest external baseline. |
| `datasets/history_baseline_1042.json` | 1042 | Same vehicle over ~504 days, ordinary driving. Reference distribution. |

Vehicle is anonymized as `VehicleA (2010 B-class sedan)`. Sensor mounted on the
gear-lever console.

---

## Why this can be a benchmark (and what it is *not*)

**It works as a benchmark because it has three things most real-world datasets lack:**

1. **Objective ground truth.** The "not a fault" label comes from the experimenter's own
   record, not from an algorithm.
2. **Discriminative power.** Different criteria give measurably different answers on the
   *same* data (see below).
3. **A transferable skill.** It tests *resistance to a fabricated fault*, not merely
   "can you detect brake pull".

**It is *not* a general-purpose benchmark.** With 38 records from one vehicle in one
5-minute session, it does not measure coverage or accuracy across a population. Treat it
as an **adversarial / robustness test set**, in the spirit of an adversarial-examples
subset — not as a substitute for a large multi-vehicle dataset.

---

## Baseline criteria

Three criteria are implemented in `baseline/criteria.py`:

| ID | Definition | Rationale |
|---|---|---|
| **C1** | `YawMM > 1.0 mm` | The absolute threshold originally suggested by the APP. |
| **C2** | `YWR = YawMM / YMM > 0.30` | Normalizes by braking intensity. |
| **C3** | `C2 and RollMM / YMM < 0.50` | Also excludes the cornering (roll) confounder. **Recommended.** |

Measured on the 38-record adversarial set (reproducible via `python3 baseline/criteria.py`):

| Criterion | Hits | Hit rate |
|---|---|---|
| C1 | 12 / 38 | **31.6%** — fooled |
| C2 | 5 / 38 | 13.2% |
| C3 | 1 / 38 | **2.6%** — not fooled |

**Reading:** a plain absolute threshold reports a ~32% "anomaly" rate on a vehicle with
*no fault*. Adding normalization and a single independent channel (roll) suppresses almost
all of it. The lesson generalizes: **failures in threshold-based detection systems usually
live in the criterion, not the sensor.**

> ⚠️ **Note on the baseline comparison.** Whether the session's normalized metric differs
> from baseline depends on how the baseline is drawn (same-day window → smaller `n`,
> nearest-N → larger `n`). Always report the baseline definition with any t-statistic; do
> not compare t values across studies that used different baselines.

---

## Quick start

```bash
cd baseline
python3 criteria.py
```

No dependencies beyond the Python standard library.

---

## Repository layout

```
yqaj-brake-benchmark/
├── README.md
├── LICENSE                      # see Licensing & privacy below
├── datasets/
│   ├── adversarial_curve_braking_38.json
│   ├── same_day_baseline.json
│   └── history_baseline_1042.json
├── schema/
│   └── SCHEMA.md                # field definitions
├── baseline/
│   └── criteria.py              # C1 / C2 / C3 reference implementation
└── docs/
    └── EVALUATION.md            # scoring protocol & reporting rules
```

---

## Licensing & privacy

Before publishing, confirm:

- [x] **Anonymization.** Vehicle is recorded as `VehicleA`; the specific model string is
      removed.
- [x] **Timestamps retained as-is.** Real collection times are kept (no shifting), because
      the same-day baseline analysis depends on true time alignment. The datasets contain
      no GPS coordinates and no personal identifiers. Time coverage is published openly:
      adversarial set `2026-09-11 11:46–11:52`; same-day baseline `2026-09-11 11:03–21:35`;
      history baseline `2025-05-16 … 2026-10-03`.
- [x] **Publication rights confirmed.** The data holder has confirmed the records may be
      redistributed as a public dataset.
- [x] **No promotional content.** Data files contain numbers only.
- [x] **License.** Released under **CC BY 4.0** (free reuse, including commercial, with
      attribution). See `LICENSE`.

See `docs/EVALUATION.md` for the reporting protocol.

---

## Changelog

- **v1.0.0** — initial release: 38-record adversarial set + two baselines + reference
  criteria.

---

## 中文说明

本仓库是一份用于测试**检测方法能否识破"伪造故障"**的真实世界数据集。

一辆**无故障车辆**被刻意安排**在弯道中制动**。弯道制动会让车身同时产生横摆与侧倾，
其横摆响应与**偏刹**（左右制动力不平衡）高度相似，因此这份数据"看起来像故障，实际不是"。

**真值是已知的**：车辆无偏刹故障，横摆来自弯道工况。这正是它能作为基准的前提。

**它能做基准的三个要素**：①有客观真值；②对不同判据有判别力（同一数据上 C1 报 31.6%、
C3 仅 2.6%）；③测的是"抵御伪故障"这一可迁移能力。

**它不能做什么**：38 条、单一车辆、5 分钟会话——不构成通用基准，只应作为
**对抗性/鲁棒性专项测试集**，不能替代多车型大数据集。

### 用途说明

本数据集是一把**探针**，不是训练语料。它小、且只有单一车辆，价值在于"它逼出的判断"，
而不在数据量。

**① 验证检测判据（工程用途）**
测一个偏刹判据能否抵御*伪造的*故障，而不只是它能否在真实故障上报警。在这份数据上
报出高异常率的判据，恰恰是**失败**的判据（因为真值是"无故障"）。建议报告误报率，
并说明判据如何处理三个混杂因子（制动强度、转向姿态、路况/时间漂移）。

**② 验证 AI 智能体能力（研究用途，本数据集最初的建库动机）**
数据*看起来像*故障、实际不是，因此它检验的是**在刻意误导的前提下推理的能力**——
这是常规准确率指标捕捉不到的。可用于考察智能体是否具备：

| 能力 | 本数据集考察什么 | 可观察的标志 |
|---|---|---|
| **抵御伪造证据** | 是否照单全收一个貌似合理的信号，还是质疑产生它的判据？ | 是否报出"偏刹" |
| **混杂因子意识** | 是否察觉横摆通道被制动强度与转向混杂？ | 是否用 `YMM` 归一化、用 `RollMM` 判别 |
| **跨源交叉验证** | 下结论前是否引入独立通道/外部基线？ | 是否使用侧倾通道与历史基线 |
| **因果 vs. 相关** | 是否区分"机械状态"（应持续）与"行驶路径"（可忽有忽无）？ | 是否考察命中的时间结构 |
| **诚实的自我限定** | 是否说明"从数据得不出什么"，还是过度断言？ | 是否声明其证据边界 |
| **方法论贡献** | 是否超越"检出/未检出"，提出并检验更好的判据？ | 是否产出类似 C3 的东西 |

> **基准测试要点**：建议采用**盲测**——只给智能体 `records` 数组（不给 `ground_truth`、
> 不给 README），问"该车是否存在偏刹故障"，记录答案与推理过程。这正是本数据集当初被
> 验证时的设置（见 `docs/EVALUATION.md` §2）。由于正确答案是"无故障"，且横摆通道确实
> 被混杂，该任务能区分"做因果推理的智能体"与"在单通道上做模式匹配的智能体"。

**③ 方法论对比**
作为一个小规模、完全标注的**反例集**，用于对比检测或归一化方法（绝对阈值、比值指标、
回归残差、混杂排除变体）。因为真值是*负*的，它能暴露只含正样本的测试集所掩盖的
误报行为。

**④ 教学与演示**
用真实数据说明：为什么绝对阈值在非受控条件下会失效，以及归一化与独立通道交叉验证
为何重要——适用于"真实世界信号处理"或汽车诊断的教学。

**它不适合做什么**：训练通用偏刹分类器（太小、单车型、单次会话）；测量召回率/覆盖率
（无正样本）；宣称某方法"可上线"（通过此处只说明能抵御一次伪造故障，不代表通用适用性）。

发布前必须完成：车型脱敏、确认数据发布授权、删除原始导出文件中的商业推广与任务指令。
