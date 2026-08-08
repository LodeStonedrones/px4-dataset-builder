import pytest
from pydantic import ValidationError

from px4_dataset_builder.config.models import BuildConfig, EventRuleConfig


def threshold_rule(name: str = "battery_low", signal: str = "battery.remaining") -> dict:
    return EventRuleConfig(
        name=name,
        kind="threshold",
        signal=signal,
        operator="lt",
        threshold=0.2,
        description="Test rule.",
    ).model_dump()


@pytest.mark.parametrize(
    ("update", "message"),
    [
        ({"signals": []}, "signals must contain"),
        ({"signals": ["*", "battery.remaining"]}, "wildcard must be used on its own"),
        ({"signals": ["not.a.signal"]}, "unknown canonical signals"),
        (
            {"signals": ["battery.voltage_v"], "event_rules": [threshold_rule()]},
            "requires signal 'battery.remaining' to be selected",
        ),
        (
            {"event_rules": [threshold_rule(signal="not.a.signal")]},
            "uses unknown canonical signal",
        ),
        (
            {"event_rules": [threshold_rule(), threshold_rule()]},
            "duplicate event rule name",
        ),
    ],
)
def test_build_config_rejects_silent_signal_and_rule_errors(update: dict, message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        BuildConfig.model_validate(update)
