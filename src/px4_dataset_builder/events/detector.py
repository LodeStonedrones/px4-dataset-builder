"""Configurable event rules with no learned or proprietary logic."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pandas as pd

from px4_dataset_builder.config.models import EventRuleConfig, RuleKind
from px4_dataset_builder.models import FlightEvent, ParsedFlight, Severity

OPERATORS: dict[str, Callable[[np.ndarray, float], np.ndarray]] = {
    "lt": np.less,
    "le": np.less_equal,
    "gt": np.greater,
    "ge": np.greater_equal,
    "eq": np.equal,
    "ne": np.not_equal,
}


class EventDetector:
    def detect(
        self,
        flight: ParsedFlight,
        data: pd.DataFrame,
        rules: list[EventRuleConfig],
    ) -> list[FlightEvent]:
        events: list[FlightEvent] = []
        time = data["time_s"].to_numpy(dtype=np.float64)
        for rule in rules:
            if rule.signal not in data:
                continue
            values = data[rule.signal].to_numpy(dtype=np.float64)
            if rule.kind == RuleKind.THRESHOLD:
                events.extend(self._threshold(flight.flight_id, time, values, rule))
            elif rule.kind == RuleKind.CHANGE:
                events.extend(self._changes(flight.flight_id, time, values, rule))
            elif rule.kind == RuleKind.EDGE:
                events.extend(self._edges(flight.flight_id, time, values, rule))
            elif rule.kind == RuleKind.GAP:
                events.extend(self._gaps(flight.flight_id, time, values, rule))

        for timestamp, severity, message in flight.logged_messages:
            if severity in {Severity.WARNING, Severity.ERROR, Severity.CRITICAL}:
                events.append(
                    FlightEvent(
                        flight_id=flight.flight_id,
                        name="px4_log_message",
                        start_s=timestamp,
                        end_s=timestamp,
                        severity=severity,
                        observed_value=None,
                        description=message,
                    )
                )
        return sorted(events, key=lambda event: (event.start_s, event.name))

    @staticmethod
    def _threshold(
        flight_id: str,
        time: np.ndarray,
        values: np.ndarray,
        rule: EventRuleConfig,
    ) -> list[FlightEvent]:
        assert rule.operator is not None and rule.threshold is not None
        condition = OPERATORS[rule.operator](values, float(rule.threshold)) & np.isfinite(values)
        return EventDetector._segments(flight_id, time, values, condition, rule)

    @staticmethod
    def _changes(
        flight_id: str,
        time: np.ndarray,
        values: np.ndarray,
        rule: EventRuleConfig,
    ) -> list[FlightEvent]:
        valid_pair = np.isfinite(values[1:]) & np.isfinite(values[:-1])
        indices = np.flatnonzero(valid_pair & (values[1:] != values[:-1])) + 1
        return [
            EventDetector._event(flight_id, rule, time[index], time[index], values[index])
            for index in indices
        ]

    @staticmethod
    def _edges(
        flight_id: str,
        time: np.ndarray,
        values: np.ndarray,
        rule: EventRuleConfig,
    ) -> list[FlightEvent]:
        assert rule.operator is not None and rule.threshold is not None
        condition = OPERATORS[rule.operator](values, float(rule.threshold)) & np.isfinite(values)
        indices = np.flatnonzero(condition[1:] & ~condition[:-1]) + 1
        return [
            EventDetector._event(flight_id, rule, time[index], time[index], values[index])
            for index in indices
        ]

    @staticmethod
    def _gaps(
        flight_id: str,
        time: np.ndarray,
        values: np.ndarray,
        rule: EventRuleConfig,
    ) -> list[FlightEvent]:
        assert rule.threshold is not None
        return EventDetector._segments(
            flight_id,
            time,
            values,
            ~np.isfinite(values),
            rule,
            minimum_duration=float(rule.threshold),
        )

    @staticmethod
    def _segments(
        flight_id: str,
        time: np.ndarray,
        values: np.ndarray,
        condition: np.ndarray,
        rule: EventRuleConfig,
        minimum_duration: float | None = None,
    ) -> list[FlightEvent]:
        if len(condition) == 0:
            return []
        padded = np.r_[False, condition, False].astype(np.int8)
        changes = np.diff(padded)
        starts = np.flatnonzero(changes == 1)
        stops = np.flatnonzero(changes == -1) - 1
        required = rule.min_duration_s if minimum_duration is None else minimum_duration
        events: list[FlightEvent] = []
        for start, stop in zip(starts, stops, strict=True):
            if time[stop] - time[start] < required:
                continue
            finite = values[start : stop + 1][np.isfinite(values[start : stop + 1])]
            observed = float(finite[-1]) if finite.size else None
            events.append(EventDetector._event(flight_id, rule, time[start], time[stop], observed))
        return events

    @staticmethod
    def _event(
        flight_id: str,
        rule: EventRuleConfig,
        start: float,
        end: float,
        observed: float | None,
    ) -> FlightEvent:
        return FlightEvent(
            flight_id=flight_id,
            name=rule.name,
            start_s=float(start),
            end_s=float(end),
            severity=Severity(rule.severity),
            source_signal=rule.signal,
            observed_value=observed,
            threshold=rule.threshold,
            description=rule.description,
        )
