"""Generate a tiny deterministic ULog for examples and integration tests.

The file contains no real vehicle identity, coordinates, or operational data. This is
not a general ULog writer; it deliberately emits only the public test topics below.
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

ULOG_MAGIC = b"\x55\x4c\x6f\x67\x01\x12\x35"


@dataclass(frozen=True, slots=True)
class Topic:
    name: str
    definition: str
    packing: str
    rows: tuple[tuple[int | float | bool, ...], ...]


def generate_synthetic_ulog(destination: Path) -> Path:
    start = 1_000_000
    fast_times = tuple(start + index * 100_000 for index in range(51))
    slow_times = tuple(start + index * 500_000 for index in range(11))
    topics = _topics(fast_times, slow_times)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as stream:
        stream.write(ULOG_MAGIC + struct.pack("<BQ", 1, start))
        _write_info(stream, "char[9] ver_sw", b"synthetic")
        for topic in topics:
            _packet(stream, "F", f"{topic.name}:{topic.definition}".encode())
        for message_id, topic in enumerate(topics, start=1):
            _packet(stream, "A", struct.pack("<BH", 0, message_id) + topic.name.encode())
        messages: list[tuple[int, bytes]] = []
        for message_id, topic in enumerate(topics, start=1):
            packer = struct.Struct("<H" + topic.packing)
            for row in topic.rows:
                messages.append((int(row[0]), _encoded_packet("D", packer.pack(message_id, *row))))
        warning_time = start + 4_200_000
        warning = struct.pack("<BQ", ord("4"), warning_time) + b"Synthetic estimator warning"
        messages.append((warning_time, _encoded_packet("L", warning)))
        for _, payload in sorted(messages, key=lambda item: item[0]):
            stream.write(payload)
    return destination


def _topics(fast: tuple[int, ...], slow: tuple[int, ...]) -> tuple[Topic, ...]:
    gps_rows = tuple(
        (
            timestamp,
            int((47.397742 + index * 0.000001) * 1e7),
            int((8.545594 + index * 0.000001) * 1e7),
            int((500 + index * 0.1) * 1e3),
            5.0,
            1.0 if index < 5 else 5.5,
            1.5 if index < 5 else 7.0,
            4 if index < 5 or index > 7 else 2,
            12 if index < 5 else 6,
        )
        for index, timestamp in enumerate(slow)
    )
    battery_rows = tuple(
        (timestamp, 16.8 - index * 0.3, 5.0 + index, 0.55 - index * 0.05, 0)
        for index, timestamp in enumerate(slow)
    )
    status_rows = tuple(
        (timestamp, 3 if index < 5 else 4, 1 if index >= 9 else 0, 2)
        for index, timestamp in enumerate(slow)
    )
    landed_rows = tuple(
        (timestamp, index < 2 or index >= 9) for index, timestamp in enumerate(slow)
    )
    local_rows = tuple(
        (
            timestamp,
            float(index),
            float(index) / 2,
            -float(index) / 5,
            2.0,
            1.0,
            -0.1,
            0.1 * index,
            1 if index >= 6 else 0,
            0,
        )
        for index, timestamp in enumerate(slow)
    )
    estimator_rows = tuple(
        (timestamp, 1 if index >= 9 else 0, 0, 0.2, 0.3, 0.4)
        for index, timestamp in enumerate(slow)
    )
    vibration_rows = tuple(
        (timestamp, 5.0 if index >= 7 else 0.2, 0.05, 0.01) for index, timestamp in enumerate(slow)
    )
    sensor_rows = tuple(
        (
            timestamp,
            0.1,
            0.2,
            -9.81,
            0.01,
            0.02,
            0.03,
        )
        for timestamp in fast
    )
    attitude_rows = tuple(
        (
            timestamp,
            math.cos(index * 0.01 / 2),
            0.0,
            0.0,
            math.sin(index * 0.01 / 2),
        )
        for index, timestamp in enumerate(fast)
    )
    actuator_rows = tuple((timestamp, 0.5, 0.5, 0.5, 0.5) for timestamp in fast)
    mission_rows = tuple((timestamp, index // 3) for index, timestamp in enumerate(slow))
    return (
        Topic(
            "vehicle_gps_position",
            "uint64_t timestamp;int32_t lat;int32_t lon;int32_t alt;"
            "float vel_m_s;float eph;float epv;uint8_t fix_type;"
            "uint8_t satellites_used;",
            "QiiifffBB",
            gps_rows,
        ),
        Topic(
            "battery_status",
            "uint64_t timestamp;float voltage_v;float current_a;float remaining;uint8_t warning;",
            "QfffB",
            battery_rows,
        ),
        Topic(
            "vehicle_status",
            "uint64_t timestamp;uint8_t nav_state;bool failsafe;uint8_t arming_state;",
            "QB?B",
            status_rows,
        ),
        Topic(
            "vehicle_land_detected",
            "uint64_t timestamp;bool landed;",
            "Q?",
            landed_rows,
        ),
        Topic(
            "vehicle_local_position",
            "uint64_t timestamp;float x;float y;float z;float vx;float vy;"
            "float vz;float heading;uint8_t xy_reset_counter;"
            "uint8_t z_reset_counter;",
            "QfffffffBB",
            local_rows,
        ),
        Topic(
            "estimator_status",
            "uint64_t timestamp;uint32_t filter_fault_flags;"
            "uint32_t innovation_check_flags;float pos_test_ratio;"
            "float vel_test_ratio;float hgt_test_ratio;",
            "QIIfff",
            estimator_rows,
        ),
        Topic(
            "vehicle_imu_status",
            "uint64_t timestamp;float accel_vibration_metric;"
            "float gyro_vibration_metric;float gyro_coning_vibration;",
            "Qfff",
            vibration_rows,
        ),
        Topic(
            "sensor_combined",
            "uint64_t timestamp;float[3] accelerometer_m_s2;float[3] gyro_rad;",
            "Qffffff",
            sensor_rows,
        ),
        Topic(
            "vehicle_attitude",
            "uint64_t timestamp;float[4] q;",
            "Qffff",
            attitude_rows,
        ),
        Topic(
            "actuator_outputs",
            "uint64_t timestamp;float[4] output;",
            "Qffff",
            actuator_rows,
        ),
        Topic(
            "mission",
            "uint64_t timestamp;uint16_t current_seq;",
            "QH",
            mission_rows,
        ),
    )


def _write_info(stream: BinaryIO, key: str, value: bytes) -> None:
    key_bytes = key.encode()
    _packet(stream, "I", struct.pack("<B", len(key_bytes)) + key_bytes + value)


def _packet(stream: BinaryIO, message_type: str, payload: bytes) -> None:
    stream.write(_encoded_packet(message_type, payload))


def _encoded_packet(message_type: str, payload: bytes) -> bytes:
    return struct.pack("<HB", len(payload), ord(message_type)) + payload
