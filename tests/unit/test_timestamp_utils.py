from datetime import timedelta

from execution.io_utils import utc_now, utc_now_iso


def test_utc_now_returns_timezone_aware_utc_datetime():
    value = utc_now()
    assert value.tzinfo is not None
    assert value.utcoffset() == timedelta(0)


def test_utc_now_iso_preserves_existing_z_suffix_contract():
    value = utc_now_iso(z_suffix=True)
    assert value.endswith("Z")
    parsed = value.replace("Z", "+00:00")
    assert utc_now().fromisoformat(parsed).utcoffset() == timedelta(0)
