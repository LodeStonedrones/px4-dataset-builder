"""Aggregate metadata and event distributions without loading flight tables."""

from __future__ import annotations

from collections import Counter
from statistics import fmean, median
from typing import Any

from px4_dataset_builder.models import ProcessedFlight, QualityCode


def aggregate_statistics(
    flights: list[ProcessedFlight], failed_logs: list[dict[str, str]]
) -> dict[str, Any]:
    durations = [flight.metadata.duration_seconds for flight in flights]
    event_counts = Counter(event.name for flight in flights for event in flight.events)
    versions = Counter(flight.metadata.px4_version or "unknown" for flight in flights)
    issue_codes = Counter(issue.code.value for flight in flights for issue in flight.quality.issues)
    gps_degraded = sum(
        any(
            event.name in {"gps_lost", "gps_degraded", "high_eph", "high_epv"}
            for event in flight.events
        )
        for flight in flights
    )
    failsafe = sum(any(event.name == "failsafe" for event in flight.events) for flight in flights)
    battery_minima = [
        stats["minimum"]
        for flight in flights
        if (stats := flight.quality.signal_statistics.get("battery.remaining"))
        and stats["minimum"] is not None
    ]
    total = len(flights)
    return {
        "flight_count": total,
        "total_duration_seconds": sum(durations),
        "total_flight_hours": sum(durations) / 3_600,
        "duration_seconds": {
            "minimum": min(durations, default=0),
            "maximum": max(durations, default=0),
            "mean": fmean(durations) if durations else 0,
            "median": median(durations) if durations else 0,
        },
        "event_distribution": dict(sorted(event_counts.items())),
        "gps_degraded_flight_percentage": 100 * gps_degraded / total if total else 0,
        "failsafe_flight_percentage": 100 * failsafe / total if total else 0,
        "battery_remaining_minimum_distribution": {
            "count": len(battery_minima),
            "minimum": min(battery_minima, default=None),
            "maximum": max(battery_minima, default=None),
            "mean": fmean(battery_minima) if battery_minima else None,
        },
        "px4_version_distribution": dict(sorted(versions.items())),
        "quality_issue_distribution": dict(sorted(issue_codes.items())),
        "corrupt_log_count": issue_codes[QualityCode.CORRUPT_LOG.value],
        "incomplete_log_count": issue_codes[QualityCode.MISSING_TOPIC.value],
        "failed_log_count": len(failed_logs),
    }
