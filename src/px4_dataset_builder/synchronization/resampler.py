"""Gap-aware deterministic resampling."""

from __future__ import annotations

import numpy as np
import numpy.typing as npt

from px4_dataset_builder.topics.catalog import Interpolation

FloatArray = npt.NDArray[np.float64]


def resample(
    source_time: FloatArray,
    source_values: FloatArray,
    target_time: FloatArray,
    method: Interpolation,
    max_gap_s: float,
) -> FloatArray:
    """Resample without bridging gaps larger than ``max_gap_s``.

    `previous` is intended for states/enums, `nearest` for observations that must not
    be blended, `linear` for continuous signals, and `none` only accepts an almost
    exact target/source timestamp match.
    """
    result = np.full(target_time.shape, np.nan, dtype=np.float64)
    finite = np.isfinite(source_time) & np.isfinite(source_values)
    times = source_time[finite]
    values = source_values[finite]
    if times.size == 0:
        return result
    order = np.argsort(times, kind="stable")
    times = times[order]
    values = values[order]
    unique = np.r_[times[1:] != times[:-1], True]
    times = times[unique]
    values = values[unique]

    if method == "previous":
        indices = np.searchsorted(times, target_time, side="right") - 1
        valid = indices >= 0
        clipped = np.clip(indices, 0, len(times) - 1)
        valid &= (target_time - times[clipped]) <= max_gap_s
        result[valid] = values[clipped[valid]]
        return result

    right = np.searchsorted(times, target_time, side="left")
    left = np.clip(right - 1, 0, len(times) - 1)
    right_clipped = np.clip(right, 0, len(times) - 1)

    if method == "nearest":
        choose_right = np.abs(times[right_clipped] - target_time) < np.abs(
            target_time - times[left]
        )
        nearest = np.where(choose_right, right_clipped, left)
        valid = np.abs(times[nearest] - target_time) <= max_gap_s
        result[valid] = values[nearest[valid]]
        return result

    if method == "none":
        exact = np.isclose(times[right_clipped], target_time, atol=1e-9, rtol=0)
        result[exact] = values[right_clipped[exact]]
        return result

    interpolated = np.interp(target_time, times, values)
    exact = (right < len(times)) & np.isclose(times[right_clipped], target_time, atol=1e-9, rtol=0)
    bracketed = (right > 0) & (right < len(times))
    gap = times[right_clipped] - times[left]
    valid = exact | (bracketed & (gap <= max_gap_s))
    result[valid] = interpolated[valid]
    return result
