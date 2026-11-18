import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import stats

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.stats_utils import (  # noqa: E402
    bonferroni,
    cohens_d,
    compare,
    describe,
    mix_rate_decomposition,
    welch_ci,
)

rng = np.random.default_rng(42)


def test_describe_basic():
    d = describe([1, 2, 3, 4, 5])
    assert d.n == 5
    assert d.mean == 3
    assert d.median == 3
    assert d.std == pytest.approx(np.std([1, 2, 3, 4, 5], ddof=1))


def test_compare_matches_scipy_welch():
    a = rng.normal(18, 6, 500)
    b = rng.normal(16, 9, 800)
    r = compare(a, b, label="x")
    t, p = stats.ttest_ind(a, b, equal_var=False)
    assert r.t_stat == pytest.approx(t)
    assert r.p_value == pytest.approx(p)
    assert r.diff == pytest.approx(a.mean() - b.mean())


def test_detects_real_difference():
    a = rng.normal(20, 5, 2000)
    b = rng.normal(18, 5, 2000)
    r = compare(a, b)
    assert r.p_value < 0.001
    assert r.ci_low < 2 < r.ci_high  # true difference is inside the CI
    assert 0.3 < r.cohens_d < 0.5     # true d is 0.4


def test_no_difference_is_not_significant_usually():
    a = rng.normal(15, 5, 1000)
    b = rng.normal(15, 5, 1000)
    r = compare(a, b)
    assert r.ci_low < 0 < r.ci_high


def test_ci_contains_diff():
    a = rng.normal(10, 2, 100)
    b = rng.normal(9, 3, 120)
    low, high = welch_ci(a, b)
    assert low < a.mean() - b.mean() < high


def test_cohens_d_sign():
    assert cohens_d([3, 4, 5], [1, 2, 3]) > 0
    assert cohens_d([1, 2, 3], [3, 4, 5]) < 0


def test_bonferroni_multiplies_and_caps():
    a = rng.normal(0, 1, 50)
    rs = [compare(a, a + 0.01) for _ in range(3)]
    for r in rs:
        r.p_value = 0.4
    bonferroni(rs)
    assert all(r.p_adjusted == 1.0 for r in rs)  # 0.4 * 3 capped at 1
    rs[0].p_value = 0.01
    bonferroni(rs)
    assert rs[0].p_adjusted == pytest.approx(0.03)


def test_mix_rate_decomposition_pure_mix_shift():
    # Rates unchanged; more trips move to the low-tip segment -> pure mix effect.
    before = {"airport": (0.2, 15.0), "city": (0.8, 20.0)}
    after = {"airport": (0.4, 15.0), "city": (0.6, 20.0)}
    out = mix_rate_decomposition(before, after)
    assert out["change"] == pytest.approx(-1.0)
    assert out["rate_effect"] == pytest.approx(0.0)
    assert out["mix_effect"] == pytest.approx(-1.0)


def test_mix_rate_decomposition_adds_up():
    before = {"a": (0.5, 10.0), "b": (0.5, 20.0)}
    after = {"a": (0.3, 12.0), "b": (0.7, 19.0)}
    out = mix_rate_decomposition(before, after)
    assert out["mix_effect"] + out["rate_effect"] == pytest.approx(out["change"])
