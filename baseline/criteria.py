# -*- coding: utf-8 -*-
"""
Baseline criteria for the YQAJ Brake-Pull benchmark.

Three criteria are provided, corresponding to the progression described in the
accompanying analysis:

    C1  absolute threshold   YawMM > 1.0                        (APP criterion)
    C2  normalized ratio     YWR = YawMM / YMM > 0.30
    C3  ratio + confounder   C2 and RollMM / YMM < 0.50         (recommended)

Run:

    python3 criteria.py ../datasets/adversarial_curve_braking_38.json

The script prints the hit rate of each criterion on the supplied session and,
when a same-day baseline file is found next to it, reports the normalized
comparison (Welch's t-test on YWR).
"""
import json
import math
import os
import sys


# ---------------------------------------------------------------- primitives

def ywr(rec):
    """Yaw-to-longitudinal amplitude ratio. Returns None when not computable."""
    ymm = rec.get("YMM", 0.0)
    if ymm <= 0:
        return None
    return rec.get("YawMM", 0.0) / ymm


def roll_ratio(rec):
    """Roll-to-longitudinal amplitude ratio. Returns None when not computable."""
    ymm = rec.get("YMM", 0.0)
    if ymm <= 0:
        return None
    return rec.get("RollMM", 0.0) / ymm


# ----------------------------------------------------------------- criteria

def C1(rec):
    """Absolute threshold, as suggested by the APP: YawMM > 1 mm."""
    return rec.get("YawMM", 0.0) > 1.0


def C2(rec):
    """Normalized ratio: YWR > 0.30. Rejects the braking-intensity confounder."""
    r = ywr(rec)
    return r is not None and r > 0.30


def C3(rec):
    """Ratio + confounder exclusion: C2 and RollMM/YMM < 0.50.

    The roll channel is the discriminative one: a genuine brake pull produces
    yaw with little roll, whereas cornering couples yaw and roll strongly.
    """
    r = ywr(rec)
    q = roll_ratio(rec)
    return r is not None and r > 0.30 and q is not None and q < 0.50


CRITERIA = {"C1": C1, "C2": C2, "C3": C3}


# ------------------------------------------------------------------ helpers

def welch_t(a, b):
    """Welch's t statistic (no variance-equality assumption)."""
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    va = sum((x - ma) ** 2 for x in a) / (len(a) - 1)
    vb = sum((x - mb) ** 2 for x in b) / (len(b) - 1)
    denom = math.sqrt(va / len(a) + vb / len(b))
    if denom == 0:
        return float("nan")
    return (ma - mb) / denom


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return float("nan")
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


# --------------------------------------------------------------------- main

def load(path):
    d = json.load(open(path, encoding="utf-8"))
    return d["records"], d


def main(path):
    recs, meta = load(path)
    n = len(recs)
    print("=" * 68)
    print("Dataset : %s" % meta.get("dataset", os.path.basename(path)))
    print("Records : %d" % n)
    if "ground_truth" in meta:
        gt = meta["ground_truth"]
        print("Truth   : brake_pull=%s, cause=%s, designed=%s"
              % (gt["brake_pull"], gt["cause"], gt["designed"]))
    print("=" * 68)

    print("\n%-6s %-42s %8s %10s" % ("ID", "Definition", "Hits", "Hit rate"))
    print("-" * 68)
    for name, fn in CRITERIA.items():
        hits = sum(1 for r in recs if fn(r))
        print("%-6s %-42s %8d %9.1f%%"
              % (name, fn.__doc__.splitlines()[0].strip(), hits, 100.0 * hits / n))

    # --- normalized comparison against same-day baseline, if available ---
    base_path = os.path.join(os.path.dirname(path), "same_day_baseline.json")
    if os.path.exists(base_path):
        brecs, _ = load(base_path)
        a = [ywr(r) for r in recs if ywr(r) is not None]
        b = [ywr(r) for r in brecs if ywr(r) is not None]
        print("\n--- normalized metric YWR (session vs same-day baseline) ---")
        print("session      n=%3d  median=%.3f  mean=%.3f"
              % (len(a), median(a), sum(a) / len(a)))
        print("same-day     n=%3d  median=%.3f  mean=%.3f"
              % (len(b), median(b), sum(b) / len(b)))
        print("Welch t = %.2f"
              % welch_t(a, b))
        print("(interpret against the baseline definition reported above; see NOTE)")
        print("\nNOTE: the sign and magnitude of this t depend on how the baseline is")
        print("drawn (same-day window vs nearest-N records). Report the baseline")
        print("definition alongside the number; do not compare t across studies")
        print("that used different baselines.")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else \
        os.path.join(os.path.dirname(__file__), "..", "datasets",
                     "adversarial_curve_braking_38.json")
    main(target)
