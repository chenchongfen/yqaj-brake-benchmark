# Intended Use

> This document states the intended use of the **YQAJ Brake-Pull Adversarial Benchmark**.
> It is written to serve as dataset-homepage copy, a platform submission statement, or
> review material. A condensed version appears in `README.md` (*Intended uses*).

---

## 0. In one line

**This is a probe, not a training corpus.** It is small and covers a single vehicle; its
value lies not in its volume but in the *judgement it elicits* — what a detection method
or an AI agent concludes when handed data that *looks like* a fault but is not one, and
*what reasoning* it brings to that conclusion.

---

## 1. What the dataset can and cannot support

Establish the boundaries before choosing a use.

### 1.1 What it provides (preconditions for the uses below)

| Property | Note |
|---|---|
| **Objective ground truth** | Vehicle had no brake-pull fault; the yaw response comes from cornering. Confirmed by the experimenter's record, not inferred by an algorithm. |
| **Discriminative power** | On the same data, different criteria give comparable, differing answers (C1 false-positive rate 31.6% vs C3 2.6%). |
| **Reproducibility** | Every statistic is recomputable from raw fields; `baseline/criteria.py` is a reference implementation. |
| **Physical completeness** | Six-DOF amplitudes make *independent-channel cross-checking* possible (the roll channel is the discriminative one). |
| **Temporal integrity** | Real timestamps are retained, enabling the time-clustering test and same-day baseline comparison. |

### 1.2 What it does not provide (limits on use)

| Limitation | Consequence |
|---|---|
| Small sample (38 adversarial + 62 same-day + 1042 history) | Not a statistically meaningful generalisation study |
| One vehicle, one session | Conclusions do not automatically transfer to other vehicles or sensor mounts |
| **No positive samples** (all "no fault") | **Recall / coverage cannot be measured** |
| No RPM, no order-tracking data | Not usable for engine-type diagnostics |
| Publicly released | An agent may have "memorised" the answer — contamination risk |

---

## 2. Use 1 — Validating detection criteria (engineering, primary)

### 2.1 Goal

Test whether a brake-pull criterion can **resist a fabricated fault**, not merely whether it
fires on a genuine one.

### 2.2 Decision rule

A high anomaly rate on this dataset means the criterion **fails** — the ground truth is
"no fault".

### 2.3 How to do it

1. Run your criterion on `records[]` from
   `datasets/adversarial_curve_braking_38.json`;
2. Compare against `ground_truth` to get the false-positive rate;
3. Compare with the reference criteria (C1 / C2 / C3);
4. Explain how your criterion handles the three **confounders**:

| Confounder | Symptom | Handling |
|---|---|---|
| Braking intensity | Absolute amplitude grows with excitation | Normalise (ratio) |
| Cornering attitude | Yaw and roll are strongly coupled | Introduce an independent channel (roll) |
| Road / time | Hit rate clusters in time | Intra-session consistency and drift checks |

5. State limitations per `EVALUATION.md` §6.

### 2.4 Reference values

| Criterion | Definition | False-positive rate |
|---|---|---|
| C1 | `YawMM > 1.0 mm` | 31.6% |
| C2 | `YWR = YawMM/YMM > 0.30` | 13.2% |
| **C3 (recommended)** | `C2 and RollMM/YMM < 0.50` | **2.6%** |

---

## 3. Use 2 — Validating AI-agent capability (research, original motivation)

### 3.1 Goal

Probe an agent's **ability to reason under a deliberately misleading premise** — a
capability dimension that ordinary accuracy metrics do not capture.

### 3.2 Why this dataset suits that purpose

- The data **looks like** a fault while being none → directly tests "is it fooled by
  fabricated evidence?";
- The confounder is **genuinely present** (the yaw channel really is confounded) → it gives
  credulity a plausible excuse;
- Ground truth is **known and negative** → "saw through it" and "took the bait" are cleanly
  separable;
- Several **independent clues** exist (normalisation, roll channel, temporal structure,
  external baseline) → depth of reasoning is observable, rather than luck.

### 3.3 Blind-test setup (the crux)

**Information isolation** is the precondition for validity:

```
Input   : only records[] of datasets/adversarial_curve_braking_38.json
          (do NOT provide ground_truth, README, or this protocol)
Prompt  : "Does this vehicle have a brake-pull (left/right braking
           imbalance) fault? Give your conclusion and the evidence."
Record  : conclusion + full reasoning trace
Truth   : No — cause is cornering (cornering_braking)
```

> This mirrors the setup under which the dataset was **originally validated**: the analyst
> worked without any experiment-design information, and agreement with ground truth
> constitutes an independent test.

### 3.4 Scoring dimensions

Record **present / absent per dimension** rather than a single score:

| Dimension | Evidence to look for | Suggested weight |
|---|---|---|
| **Correct conclusion** | Is it "not brake pull"? | **Required** |
| **Criterion critique** | Does it note the absolute threshold lacks normalisation? | High |
| **Confounder awareness** | Does it use the roll channel or a ratio metric? | High |
| **Cross-source verification** | Does it bring in a history / same-day baseline? | Medium |
| **Causal structure** | Does it examine the temporal clustering of hits? | Medium |
| **Honest self-limitation** | Does it declare evidential boundaries ("attribution exclusion, not proof")? | Medium |
| **Methodological contribution** | Does it propose and test a better criterion? | Bonus |

### 3.5 An illustrative capability profile

For calibration, a first validation of this dataset recorded an analysis exhibiting the
following capability set (see the paper *Independent Insight of an AI Agent into Real-World
Automotive Modal Data: A Falsification-Oriented Analysis of a Double-Blind Adversarial
Test*)：

- **Criterion critique** — identified that the absolute threshold omits excitation
  normalisation (corr(YawMM,YMM) = 0.600);
- **Confounder awareness** — found 83% of hits accompanied by roll, corr(YawMM,RollMM) =
  0.850 (partial correlation 0.792);
- **Cross-source verification** — brought in a same-vehicle history baseline for a
  normalised comparison;
- **Causal structure** — used temporal clustering of the hit rate (5.3% → 57.9%) to
  attribute it to working conditions rather than a persistent fault;
- **Honest self-limitation** — explicitly declared "attribution exclusion ≠ proof", and
  noted that the reasoning chain would fail if only a single channel were available;
- **Methodological contribution** — proposed and validated criterion C3 (cutting the
  false-positive rate from 31.6% to 2.6%).

**This is not a pass mark; it is an illustration of the capability ceiling.** It may be used
as a "full-score reference" to calibrate the scoring gradient.

---

## 4. Use 3 — Methodological comparison

### 4.1 Goal

Serve as a small, fully-labelled **counterexample set** for comparing detection or
normalisation methods.

### 4.2 Applicable method families

| Family | What this dataset exposes |
|---|---|
| Absolute thresholds | Fooled by the braking-intensity confounder (baseline) |
| Ratio / normalised metrics | Remove the intensity confounder but not the attitude one |
| Regression residuals | Judge deviation by fit residual; watch for overfitting |
| Confounder-exclusion variants | Add an independent channel; lowest false-positive rate |

### 4.3 Why *negative* samples matter

Test sets containing only positives (real faults) **hide false-positive behaviour**, because
an alarm is always treated as correct. Here the ground truth is *negative*, so any alarm is
a false positive — directly exposing a method's false-alarm tendency.

---

## 5. Use 4 — Teaching and demonstration

### 5.1 Scenarios

- "Signal processing in the wild": confounding under uncontrolled conditions;
- Automotive diagnostics training: why bench standards do not transfer directly to app data;
- AI courses: adversarial tests and out-of-distribution generalisation;
- Research-methods courses: why reproducibility matters (with a real correction case in
  Appendix F of the accompanying paper).

### 5.2 Core concepts it can illustrate

1. **Failure of absolute thresholds** — under uncontrolled conditions, a "threshold" ends
   up sifting a working-condition quantity;
2. **Why normalisation is necessary** — separating "magnitude" from "proportion";
3. **Independent-channel cross-checking** — similarity in a single channel is not decisive;
4. **Causality vs correlation** — a mechanical state should persist; a path change may come
   and go;
5. **Falsification beats confirmation** — elimination yields robust conclusions, provided
   the boundaries are stated honestly.

---

## 6. Explicit non-uses

The following are **not supported**; if used anyway, conclusions will be unreliable:

| Non-use | Reason |
|---|---|
| Training a general brake-pull classifier | Too small, one vehicle, one session |
| Measuring recall / coverage / sensitivity | **No positive samples**; denominator missing |
| Claiming a method is "production-ready" | Passing here shows resistance to **one** fabricated fault |
| Inferring cross-vehicle performance | Single vehicle; no model diversity |
| Engine-type diagnostics | No RPM or order information |
| Using it as a general benchmark ("passed ⇒ qualified") | It is a **specialised robustness test set**, not a general benchmark |

---

## 7. Usage norms (summary)

| Item | Requirement |
|---|---|
| **Blind testing** | Agent-capability evaluation must isolate `ground_truth` |
| **Baseline definition** | Any baseline statistic must be reported together with its sampling rule and `n` |
| **Limitation statement** | Reports must state the boundaries in §6 |
| **Contamination** | The public set risks overfitting; keep a holdout subset |
| **License** | CC BY 4.0; attribution required (format in `LICENSE`) |
| **Citation** | See `EVALUATION.md` §8 |

---

## 8. License and attribution

Released under **CC BY 4.0**. For academic use, please cite:

```bibtex
@misc{yqaj_brake_benchmark_2026,
  title        = {YQAJ Brake-Pull Adversarial Benchmark:
                  A Fault-Free Curved-Braking Dataset for Testing
                  Resistance to Fabricated Faults},
  author       = {Chen, Chongfen and {WorkBuddy AI Agent}},
  year         = {2026},
  version      = {1.0.0},
  publisher    = {GitHub},
  howpublished = {\url{https://github.com/<account>/yqaj-brake-benchmark}},
  note         = {Licensed under CC BY 4.0}
}
```

---

*Related documents: `README.md` (overview), `schema/SCHEMA.md` (field definitions),
`docs/EVALUATION.md` (evaluation protocol),
`docs/COMPLIANCE_CHECKLIST.md` (compliance record).*
