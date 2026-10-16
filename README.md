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

发布前必须完成：车型脱敏、确认数据发布授权、删除原始导出文件中的商业推广与任务指令。
