"""Deterministic anonymization with no external service calls."""

from __future__ import annotations

from math import cos, radians

import numpy as np
import pandas as pd

from px4_dataset_builder.config.models import AnonymizationConfig
from px4_dataset_builder.models import FlightEvent, FlightMetadata
from px4_dataset_builder.utils.hashing import private_alias

EARTH_RADIUS_M = 6_378_137.0


class Anonymizer:
    def apply(
        self,
        data: pd.DataFrame,
        metadata: FlightMetadata,
        events: list[FlightEvent],
        config: AnonymizationConfig,
    ) -> tuple[pd.DataFrame, FlightMetadata, list[FlightEvent]]:
        if not config.enabled:
            return data, metadata, events
        result = data.copy()
        result = result.drop(columns=["timestamp_us"], errors="ignore")
        if config.gps_mode == "remove":
            result = result.drop(
                columns=["gps.latitude_deg", "gps.longitude_deg", "gps.altitude_m"],
                errors="ignore",
            )
        elif config.gps_mode == "relative":
            self._relative_gps(result, relative_altitude=config.relative_altitude)

        update: dict[str, object] = {
            "start_timestamp": None,
            "end_timestamp": None,
            "start_timestamp_us": 0,
            "end_timestamp_us": round(metadata.duration_seconds * 1_000_000),
            "drone_id": None,
            "source_info": {
                key: value
                for key, value in metadata.source_info.items()
                if key not in config.remove_metadata
            },
            "signals_available": sorted(
                str(column) for column in result.columns if column not in {"time_s", "timestamp_us"}
            ),
            "gps_available": any(str(column).startswith("gps.") for column in result),
        }
        if config.hash_source_filenames:
            update["source_file"] = f"{private_alias(metadata.source_sha256)}.ulg"
            update["flight_id"] = private_alias(metadata.source_sha256)
        anonymized_metadata = metadata.model_copy(update=update)
        anonymized_events = [
            event.model_copy(
                update={
                    "flight_id": anonymized_metadata.flight_id,
                    "description": (
                        "PX4 warning/error text removed by anonymization."
                        if event.name == "px4_log_message"
                        else event.description
                    ),
                    "observed_value": None
                    if event.name == "px4_log_message"
                    else event.observed_value,
                }
            )
            for event in events
        ]
        return result, anonymized_metadata, anonymized_events

    @staticmethod
    def _relative_gps(frame: pd.DataFrame, relative_altitude: bool) -> None:
        latitude_name = "gps.latitude_deg"
        longitude_name = "gps.longitude_deg"
        if latitude_name in frame and longitude_name in frame:
            latitude = frame[latitude_name].to_numpy(dtype=np.float64)
            longitude = frame[longitude_name].to_numpy(dtype=np.float64)
            valid = np.isfinite(latitude) & np.isfinite(longitude)
            if valid.any():
                origin_index = int(np.flatnonzero(valid)[0])
                lat0 = latitude[origin_index]
                lon0 = longitude[origin_index]
                frame["gps.north_m"] = np.radians(latitude - lat0) * EARTH_RADIUS_M
                frame["gps.east_m"] = (
                    np.radians(longitude - lon0) * EARTH_RADIUS_M * cos(radians(lat0))
                )
            frame.drop(columns=[latitude_name, longitude_name], inplace=True)
        if relative_altitude and "gps.altitude_m" in frame:
            altitude = frame["gps.altitude_m"].to_numpy(dtype=np.float64)
            finite = altitude[np.isfinite(altitude)]
            if finite.size:
                frame["gps.altitude_relative_m"] = altitude - finite[0]
            frame.drop(columns=["gps.altitude_m"], inplace=True)
