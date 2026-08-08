"""Flight-level split assignment.

Samples from a flight are never split. Drone/date strategies keep the entire group in
one partition. Event strategy stratifies by the complete event-name signature.
"""

from __future__ import annotations

import hashlib
import random
from collections import defaultdict
from collections.abc import Callable

from px4_dataset_builder.config.models import SplitConfig, SplitStrategy
from px4_dataset_builder.models import ProcessedFlight

SPLITS = ("train", "validation", "test")


def assign_splits(flights: list[ProcessedFlight], config: SplitConfig) -> dict[str, str]:
    if not flights:
        return {}
    if config.strategy == SplitStrategy.FLIGHT:
        return {
            flight.metadata.flight_id: _stable_partition(
                flight.metadata.flight_id, config, SplitStrategy.FLIGHT.value
            )
            for flight in flights
        }
    if config.strategy == SplitStrategy.EVENT:
        strata: dict[str, list[ProcessedFlight]] = defaultdict(list)
        for flight in flights:
            signature = ",".join(sorted({event.name for event in flight.events})) or "no_event"
            strata[signature].append(flight)
        result: dict[str, str] = {}
        for signature, members in sorted(strata.items()):
            result.update(
                _assign_groups(members, config, lambda item: item.metadata.flight_id, signature)
            )
        return result

    if config.strategy == SplitStrategy.DRONE:
        key_function = _drone_key
    elif config.strategy == SplitStrategy.DATE:
        key_function = _date_key
    else:
        key_function = _flight_key
    return _assign_groups(flights, config, key_function, config.strategy.value)


def _assign_groups(
    flights: list[ProcessedFlight],
    config: SplitConfig,
    key_function: Callable[[ProcessedFlight], str],
    salt: str,
) -> dict[str, str]:
    groups: dict[str, list[ProcessedFlight]] = defaultdict(list)
    for flight in flights:
        groups[key_function(flight)].append(flight)
    keys = list(groups)
    if config.strategy == SplitStrategy.RANDOM:
        random.Random(config.seed).shuffle(keys)
    else:
        keys.sort(
            key=lambda key: hashlib.sha256(f"{config.seed}:{salt}:{key}".encode()).hexdigest()
        )

    total = len(flights)
    targets = {
        "train": total * config.train,
        "validation": total * config.validation,
        "test": total * config.test,
    }
    counts = dict.fromkeys(SPLITS, 0)
    result: dict[str, str] = {}
    for key in keys:
        group = groups[key]
        split = max(
            SPLITS,
            key=lambda candidate: (
                targets[candidate] - counts[candidate],
                -SPLITS.index(candidate),
            ),
        )
        for flight in group:
            result[flight.metadata.flight_id] = split
        counts[split] += len(group)
    return result


def _drone_key(item: ProcessedFlight) -> str:
    return item.metadata.drone_id or "unknown"


def _date_key(item: ProcessedFlight) -> str:
    return item.metadata.start_timestamp[:10] if item.metadata.start_timestamp else "unknown"


def _flight_key(item: ProcessedFlight) -> str:
    return item.metadata.flight_id


def _stable_partition(key: str, config: SplitConfig, salt: str) -> str:
    digest = hashlib.sha256(f"{config.seed}:{salt}:{key}".encode()).digest()
    value = int.from_bytes(digest, "big") / 2 ** (8 * len(digest))
    if value < config.train:
        return "train"
    if value < config.train + config.validation:
        return "validation"
    return "test"
