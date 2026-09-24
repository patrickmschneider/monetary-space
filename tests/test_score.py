import pytest

from monetary_space import score
from monetary_space.score import DOWN, EASE, HAWKISH, LOOSE, NEUTRAL, ON_TRACK, TIGHT, UP


def test_zscore_sign_makes_positive_inflationary():
    # Unemployment above u* is disinflationary: sign −1 turns it negative.
    z = score.zscore(x=5.0, b=4.5, sigma=0.5, sign=-1)
    assert z.z == pytest.approx(-1.0)
    assert not z.clipped


def test_zscore_clips_and_keeps_raw():
    z = score.zscore(x=10.0, b=2.0, sigma=1.0, sign=1, clip=3.0)
    assert z.z == 3.0 and z.raw == 8.0 and z.clipped


@pytest.mark.parametrize("bad", [0.0, -1.0])
def test_zscore_rejects_nonpositive_sigma(bad):
    with pytest.raises(ValueError):
        score.zscore(1.0, 0.0, bad, 1)


@pytest.mark.parametrize("z,expected", [(0.51, UP), (0.5, NEUTRAL), (-0.5, NEUTRAL), (-0.51, DOWN)])
def test_direction_thresholds_are_strict(z, expected):
    assert score.direction(z, 0.5) == expected


def test_block_score_and_diffusion():
    zs = [1.0, 0.2, -0.9]
    assert score.block_score(zs) == pytest.approx(0.1)
    assert score.diffusion(zs) == {UP: 1, NEUTRAL: 1, DOWN: 1}


def test_pressure_uses_config_weights_and_requires_all_blocks():
    w = {"B": 0.5, "A": 0.3, "C": 0.2}
    assert score.pressure({"A": 1.0, "B": 1.0, "C": -1.0}, w) == pytest.approx(0.6)
    assert score.pressure({"A": 1.0, "B": 1.0, "C": -1.0}, {"A": 1 / 3, "B": 1 / 3, "C": 1 / 3}) == pytest.approx(1 / 3)
    with pytest.raises(ValueError):
        score.pressure({"A": 1.0, "B": 1.0}, w)


def test_rstar_band_widens_to_minimum_half_width():
    assert score.rstar_band(0.5, 0.7, 0.5) == pytest.approx((0.1, 1.1))
    assert score.rstar_band(0.0, 2.0, 0.5) == pytest.approx((0.0, 2.0))


@pytest.mark.parametrize("r,expected", [(1.6, TIGHT), (1.5, NEUTRAL), (0.5, NEUTRAL), (0.4, LOOSE)])
def test_stance_against_band(r, expected):
    assert score.stance(r, (0.5, 1.5)) == expected


# Golden test: the verdict grid in spec Section 2, all nine cells.
GRID = {
    (UP, LOOSE): HAWKISH, (UP, NEUTRAL): HAWKISH, (UP, TIGHT): ON_TRACK,
    (NEUTRAL, LOOSE): HAWKISH, (NEUTRAL, NEUTRAL): ON_TRACK, (NEUTRAL, TIGHT): EASE,
    (DOWN, LOOSE): ON_TRACK, (DOWN, NEUTRAL): EASE, (DOWN, TIGHT): EASE,
}


@pytest.mark.parametrize("cell,expected", GRID.items())
def test_verdict_grid(cell, expected):
    assert score.verdict(*cell) == expected


def test_driver_is_largest_weighted_contribution():
    w = {"B": 0.5, "A": 0.3, "C": 0.2}
    assert score.driver({"A": 2.0, "B": 1.0, "C": 0.0}, w) == "A"   # 0.6 > 0.5
    assert score.driver({"A": -0.5, "B": 0.4, "C": -2.0}, w) == "C"  # |−0.4| is largest
