"""VIN validation utilities."""

from __future__ import annotations

import re

from etl.constants import VIN_INVALID_CHARS, VIN_LENGTH


def is_valid_vin(vin: str | None) -> tuple[bool, str | None]:
    if vin is None or not str(vin).strip():
        return False, "VIN is empty"

    vin = str(vin).strip().upper()
    if len(vin) != VIN_LENGTH:
        return False, f"VIN length must be {VIN_LENGTH}, got {len(vin)}"

    if not re.fullmatch(r"[A-HJ-NPR-Z0-9]{17}", vin):
        invalid = set(vin) & VIN_INVALID_CHARS
        if invalid:
            return False, f"VIN contains invalid characters: {sorted(invalid)}"
        return False, "VIN contains invalid characters"

    return True, None
