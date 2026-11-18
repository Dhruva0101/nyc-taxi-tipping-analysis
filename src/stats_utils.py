"""Small, tested statistics helpers for comparing two groups.

Everything here works on plain sequences or NumPy arrays, so it can be unit-tested
without BigQuery.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass
class Describe:
    n: int
    mean: float
    std: float
    median: float
    p25: float
    p75: float


@dataclass
class Comparison:
    label: str
    n_a: int
    n_b: int
    mean_a: float
    mean_b: float
    diff: float          # mean_a - mean_b
    ci_low: float        # 95% CI for diff (Welch)
    ci_high: float
    t_stat: float
    p_value: float
    cohens_d: float
    p_adjusted: float | None = None


def describe(values) -> Describe:
    x = np.asarray(values, dtype=float)
    return Describe(
        n=int(x.size),
        mean=float(x.mean()),
        std=float(x.std(ddof=1)),
        median=float(np.median(x)),
        p25=float(np.percentile(x, 25)),
        p75=float(np.percentile(x, 75)),
    )


def cohens_d(a, b) -> float:
    """Standardized mean difference using the pooled standard deviation."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    na, nb = a.size, b.size
    pooled_var = ((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2)
    return float((a.mean() - b.mean()) / np.sqrt(pooled_var))


def welch_ci(a, b, confidence: float = 0.95) -> tuple[float, float]:
    """Confidence interval for mean(a) - mean(b) without assuming equal variances."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    va, vb = a.var(ddof=1) / a.size, b.var(ddof=1) / b.size
    se = np.sqrt(va + vb)
    # Welch-Satterthwaite degrees of freedom
    dof = (va + vb) ** 2 / (va**2 / (a.size - 1) + vb**2 / (b.size - 1))
    t_crit = stats.t.ppf((1 + confidence) / 2, dof)
    diff = a.mean() - b.mean()
    return float(diff - t_crit * se), float(diff + t_crit * se)


def compare(a, b, label: str = "") -> Comparison:
    """Welch's t-test plus effect size and CI for two independent groups."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    t_stat, p_value = stats.ttest_ind(a, b, equal_var=False)
    low, high = welch_ci(a, b)
    return Comparison(
        label=label,
        n_a=int(a.size),
        n_b=int(b.size),
        mean_a=float(a.mean()),
        mean_b=float(b.mean()),
        diff=float(a.mean() - b.mean()),
        ci_low=low,
        ci_high=high,
        t_stat=float(t_stat),
        p_value=float(p_value),
        cohens_d=cohens_d(a, b),
    )


def bonferroni(comparisons: list[Comparison]) -> list[Comparison]:
    """Adjust p-values for running several tests at once (capped at 1.0)."""
    m = len(comparisons)
    for c in comparisons:
        c.p_adjusted = min(1.0, c.p_value * m)
    return comparisons


def mix_rate_decomposition(seg_before: dict, seg_after: dict) -> dict:
    """Split the change in an overall average into mix and rate effects.

    Each argument maps segment -> (share_of_trips, mean_tip_pct).
    overall = sum(share * rate). Change = mix effect + rate effect, where
      mix effect  = sum((share_after - share_before) * rate_before)
      rate effect = sum(share_after * (rate_after - rate_before))
    """
    segments = set(seg_before) | set(seg_after)
    mix = rate = 0.0
    for s in segments:
        sh0, r0 = seg_before.get(s, (0.0, 0.0))
        sh1, r1 = seg_after.get(s, (0.0, 0.0))
        mix += (sh1 - sh0) * r0
        rate += sh1 * (r1 - r0)
    before = sum(sh * r for sh, r in seg_before.values())
    after = sum(sh * r for sh, r in seg_after.values())
    return {"before": before, "after": after, "change": after - before,
            "mix_effect": mix, "rate_effect": rate}
