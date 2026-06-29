import re


def normalize_plate_number(plate_number: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", plate_number.upper())
