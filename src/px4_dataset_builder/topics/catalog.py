"""Canonical public signal names mapped to reviewed PX4 uORB fields.

Candidates are ordered from newer to legacy representations. A missing candidate is
reported as unavailable; values are never synthesized from a field with different
semantics. The catalog is data, making PX4-version changes reviewable and testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Interpolation = Literal["linear", "previous", "nearest", "none"]


@dataclass(frozen=True, slots=True)
class SignalSpec:
    candidates: tuple[str, ...]
    unit: str
    interpolation: Interpolation
    scale: float = 1.0
    offset: float = 0.0
    valid_range: tuple[float, float] | None = None
    sensitive: bool = False


def _signal(
    *candidates: str,
    unit: str,
    interpolation: Interpolation = "linear",
    scale: float = 1.0,
    valid_range: tuple[float, float] | None = None,
    sensitive: bool = False,
) -> SignalSpec:
    return SignalSpec(candidates, unit, interpolation, scale, 0.0, valid_range, sensitive)


SIGNAL_CATALOG: dict[str, SignalSpec] = {
    "gps.latitude_deg": _signal(
        "vehicle_gps_position.lat",
        unit="deg",
        scale=1e-7,
        valid_range=(-90, 90),
        sensitive=True,
    ),
    "gps.longitude_deg": _signal(
        "vehicle_gps_position.lon",
        unit="deg",
        scale=1e-7,
        valid_range=(-180, 180),
        sensitive=True,
    ),
    "gps.altitude_m": _signal(
        "vehicle_gps_position.alt",
        unit="m",
        scale=1e-3,
        valid_range=(-1_000, 100_000),
        sensitive=True,
    ),
    "gps.velocity_m_s": _signal("vehicle_gps_position.vel_m_s", unit="m/s", valid_range=(0, 500)),
    "gps.velocity_n_m_s": _signal(
        "vehicle_gps_position.vel_n_m_s", unit="m/s", valid_range=(-500, 500)
    ),
    "gps.velocity_e_m_s": _signal(
        "vehicle_gps_position.vel_e_m_s", unit="m/s", valid_range=(-500, 500)
    ),
    "gps.velocity_d_m_s": _signal(
        "vehicle_gps_position.vel_d_m_s", unit="m/s", valid_range=(-500, 500)
    ),
    "gps.heading_rad": _signal(
        "vehicle_gps_position.heading",
        unit="rad",
        interpolation="nearest",
        valid_range=(-6.4, 6.4),
    ),
    "gps.eph_m": _signal("vehicle_gps_position.eph", unit="m", valid_range=(0, 10_000)),
    "gps.epv_m": _signal("vehicle_gps_position.epv", unit="m", valid_range=(0, 10_000)),
    "gps.fix_type": _signal(
        "vehicle_gps_position.fix_type", unit="enum", interpolation="previous", valid_range=(0, 8)
    ),
    "gps.satellites_used": _signal(
        "vehicle_gps_position.satellites_used",
        unit="count",
        interpolation="previous",
        valid_range=(0, 100),
    ),
    "position.x_m": _signal("vehicle_local_position.x", unit="m"),
    "position.y_m": _signal("vehicle_local_position.y", unit="m"),
    "position.z_m": _signal("vehicle_local_position.z", unit="m"),
    "position.velocity_x_m_s": _signal("vehicle_local_position.vx", unit="m/s"),
    "position.velocity_y_m_s": _signal("vehicle_local_position.vy", unit="m/s"),
    "position.velocity_z_m_s": _signal("vehicle_local_position.vz", unit="m/s"),
    "position.heading_rad": _signal(
        "vehicle_local_position.heading",
        "vehicle_local_position.yaw",
        unit="rad",
        interpolation="nearest",
    ),
    "attitude.q_w": _signal("vehicle_attitude.q[0]", unit="ratio", interpolation="nearest"),
    "attitude.q_x": _signal("vehicle_attitude.q[1]", unit="ratio", interpolation="nearest"),
    "attitude.q_y": _signal("vehicle_attitude.q[2]", unit="ratio", interpolation="nearest"),
    "attitude.q_z": _signal("vehicle_attitude.q[3]", unit="ratio", interpolation="nearest"),
    "imu.accel_x_m_s2": _signal(
        "sensor_combined.accelerometer_m_s2[0]", "sensor_accel.x", unit="m/s^2"
    ),
    "imu.accel_y_m_s2": _signal(
        "sensor_combined.accelerometer_m_s2[1]", "sensor_accel.y", unit="m/s^2"
    ),
    "imu.accel_z_m_s2": _signal(
        "sensor_combined.accelerometer_m_s2[2]", "sensor_accel.z", unit="m/s^2"
    ),
    "imu.gyro_x_rad_s": _signal("sensor_combined.gyro_rad[0]", "sensor_gyro.x", unit="rad/s"),
    "imu.gyro_y_rad_s": _signal("sensor_combined.gyro_rad[1]", "sensor_gyro.y", unit="rad/s"),
    "imu.gyro_z_rad_s": _signal("sensor_combined.gyro_rad[2]", "sensor_gyro.z", unit="rad/s"),
    "magnetic.x_ga": _signal(
        "vehicle_magnetometer.magnetometer_ga[0]",
        "sensor_combined.magnetometer_ga[0]",
        "sensor_mag.x",
        unit="gauss",
    ),
    "magnetic.y_ga": _signal(
        "vehicle_magnetometer.magnetometer_ga[1]",
        "sensor_combined.magnetometer_ga[1]",
        "sensor_mag.y",
        unit="gauss",
    ),
    "magnetic.z_ga": _signal(
        "vehicle_magnetometer.magnetometer_ga[2]",
        "sensor_combined.magnetometer_ga[2]",
        "sensor_mag.z",
        unit="gauss",
    ),
    "barometer.altitude_m": _signal(
        "vehicle_air_data.baro_alt_meter", "sensor_combined.baro_alt_meter", unit="m"
    ),
    "barometer.pressure_pa": _signal(
        "vehicle_air_data.baro_pressure_pa", "sensor_baro.pressure", unit="Pa"
    ),
    "battery.voltage_v": _signal("battery_status.voltage_v", unit="V", valid_range=(0, 100)),
    "battery.current_a": _signal("battery_status.current_a", unit="A", valid_range=(-500, 1_000)),
    "battery.remaining": _signal(
        "battery_status.remaining", unit="ratio", interpolation="previous", valid_range=(-0.1, 1.1)
    ),
    "battery.discharged_mah": _signal("battery_status.discharged_mah", unit="mAh"),
    "battery.warning": _signal("battery_status.warning", unit="enum", interpolation="previous"),
    "flight.mode": _signal(
        "vehicle_status.nav_state",
        unit="enum",
        interpolation="previous",
    ),
    "flight.arming_state": _signal(
        "vehicle_status.arming_state", unit="enum", interpolation="previous"
    ),
    "flight.failsafe": _signal("vehicle_status.failsafe", unit="bool", interpolation="previous"),
    "land.landed": _signal("vehicle_land_detected.landed", unit="bool", interpolation="previous"),
    "mission.current_sequence": _signal(
        "mission.current_seq", unit="index", interpolation="previous"
    ),
    "estimator.filter_fault_flags": _signal(
        "estimator_status.filter_fault_flags", unit="bitmask", interpolation="previous"
    ),
    "estimator.innovation_check_flags": _signal(
        "estimator_status.innovation_check_flags", unit="bitmask", interpolation="previous"
    ),
    "estimator.position_test_ratio": _signal("estimator_status.pos_test_ratio", unit="ratio"),
    "estimator.velocity_test_ratio": _signal("estimator_status.vel_test_ratio", unit="ratio"),
    "estimator.height_test_ratio": _signal("estimator_status.hgt_test_ratio", unit="ratio"),
    "estimator.gps_hpos_innovation_x": _signal(
        "estimator_innovations.gps_hpos[0]", "ekf2_innovations.vel_pos_innov[3]", unit="m"
    ),
    "estimator.gps_hpos_innovation_y": _signal(
        "estimator_innovations.gps_hpos[1]", "ekf2_innovations.vel_pos_innov[4]", unit="m"
    ),
    "estimator.xy_reset_counter": _signal(
        "vehicle_local_position.xy_reset_counter", unit="count", interpolation="previous"
    ),
    "estimator.z_reset_counter": _signal(
        "vehicle_local_position.z_reset_counter", unit="count", interpolation="previous"
    ),
    "vibration.accel": _signal("vehicle_imu_status.accel_vibration_metric", unit="m/s^2"),
    "vibration.gyro": _signal("vehicle_imu_status.gyro_vibration_metric", unit="rad/s"),
    **{
        f"actuator.output_{index}": _signal(
            f"actuator_outputs.output[{index}]", unit="normalized_or_pwm", interpolation="previous"
        )
        for index in range(16)
    },
}


def required_topics(signal_names: list[str]) -> set[str]:
    selected = (
        SIGNAL_CATALOG
        if signal_names == ["*"]
        else {name: SIGNAL_CATALOG[name] for name in signal_names if name in SIGNAL_CATALOG}
    )
    return {
        candidate.split(".", 1)[0] for spec in selected.values() for candidate in spec.candidates
    }
