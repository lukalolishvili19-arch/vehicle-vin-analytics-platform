"""Unit tests for ETL validation."""

from etl.validate.rules import validate_dataframe
from etl.validate.vin import is_valid_vin


def test_valid_vin():
    ok, msg = is_valid_vin("WBA83GG04T7T08094")
    assert ok is True
    assert msg is None


def test_invalid_vin_length():
    ok, msg = is_valid_vin("SHORT")
    assert ok is False
    assert "length" in msg.lower()


def test_validate_dataframe_splits_quarantine():
    import pandas as pd

    df = pd.DataFrame(
        [
            {
                "picture_count": 1,
                "stock_number": "1",
                "model_year": 2020,
                "make": "BMW",
                "model": "X3",
                "style": "330i",
                "exterior_color": "BLACK",
                "mileage": 1000,
                "has_condition_report": True,
                "grade": 4.0,
                "lights_raw": "Green",
                "announcements": "",
                "vin": "WBA83GG04T7T08094",
                "batch_id": "test",
                "source_file": "test.csv",
                "ingested_at": "2026-01-01T00:00:00+00:00",
            },
            {
                "picture_count": 1,
                "stock_number": "2",
                "model_year": 2020,
                "make": "BMW",
                "model": "X3",
                "style": "330i",
                "exterior_color": "BLACK",
                "mileage": 1000,
                "has_condition_report": True,
                "grade": 4.0,
                "lights_raw": "Green",
                "announcements": "",
                "vin": "BAD",
                "batch_id": "test",
                "source_file": "test.csv",
                "ingested_at": "2026-01-01T00:00:00+00:00",
            },
        ]
    )

    valid, quarantine = validate_dataframe(df)
    assert len(valid) == 1
    assert len(quarantine) == 1
    assert quarantine.iloc[0]["rejection_code"] == "INVALID_VIN"
