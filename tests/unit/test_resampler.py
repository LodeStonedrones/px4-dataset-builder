import numpy as np

from px4_dataset_builder.synchronization.resampler import resample


def test_linear_resampling_does_not_bridge_large_gap() -> None:
    result = resample(
        np.array([0.0, 1.0, 10.0]),
        np.array([0.0, 1.0, 10.0]),
        np.array([0.5, 5.0, 10.0]),
        "linear",
        max_gap_s=2.0,
    )
    assert result[0] == 0.5
    assert np.isnan(result[1])
    assert result[2] == 10.0


def test_previous_resampling_is_bounded() -> None:
    result = resample(
        np.array([0.0, 1.0]),
        np.array([3.0, 4.0]),
        np.array([0.5, 2.1]),
        "previous",
        max_gap_s=1.0,
    )
    assert result[0] == 3.0
    assert np.isnan(result[1])


def test_linear_resampling_does_not_use_relative_tolerance_for_large_timestamps() -> None:
    result = resample(
        np.array([0.0, 100_000.0]),
        np.array([0.0, 1.0]),
        np.array([99_999.5]),
        "linear",
        max_gap_s=0.1,
    )

    assert np.isnan(result[0])
