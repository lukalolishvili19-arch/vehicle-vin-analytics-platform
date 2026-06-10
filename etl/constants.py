"""Column mappings and business rule constants."""

SOURCE_COLUMNS = [
    "Picture Count",
    "Stock Number",
    "Year",
    "Make",
    "Model",
    "Style",
    "Exterior Color",
    "Mileage",
    "Has Condition Report",
    "Grade",
    "Lights",
    "Announcements",
    "Vin",
]

COLUMN_RENAME = {
    "Picture Count": "picture_count",
    "Stock Number": "stock_number",
    "Year": "model_year",
    "Make": "make",
    "Model": "model",
    "Style": "style",
    "Exterior Color": "exterior_color",
    "Mileage": "mileage",
    "Has Condition Report": "has_condition_report",
    "Grade": "grade",
    "Lights": "lights_raw",
    "Announcements": "announcements",
    "Vin": "vin",
}

REQUIRED_COLUMNS = set(SOURCE_COLUMNS)

MIN_YEAR = 1990
MAX_YEAR = 2030
MIN_GRADE = 0.0
MAX_GRADE = 5.0

VIN_LENGTH = 17
VIN_INVALID_CHARS = set("IOQ")

COLOR_NORMALIZATION = {
    "GY": "GRAY",
    "SV": "SILVER",
    "BL": "BLUE",
    "NO COLOR": "UNKNOWN",
}

LIGHT_CODE_MAP = {
    "RED": "RED",
    "GREEN": "GREEN",
    "YELLOW": "YELLOW",
    "WHITE": "WHITE",
    "BLUE": "BLUE",
    "UNKNOWN": "UNKNOWN",
}

ANNOUNCEMENT_KEYWORDS = {
    "is_as_is": ["AS IS", "AS-IS", "ASIS"],
    "is_inop": ["INOP"],
    "has_structural_damage": ["STRUCTURAL"],
    "is_salvage": ["SALVAGE", "TOTAL LOSS"],
    "is_repo": ["REPO"],
    "is_green_light": ["GREEN LIGHT", "GREENLIGHT", "GREEN LIGHT"],
}

REJECTION_CODES = {
    "MISSING_COLUMNS": "MISSING_COLUMNS",
    "INVALID_VIN": "INVALID_VIN",
    "DUPLICATE_VIN": "DUPLICATE_VIN",
    "INVALID_YEAR": "INVALID_YEAR",
    "INVALID_MILEAGE": "INVALID_MILEAGE",
    "INVALID_GRADE": "INVALID_GRADE",
}
