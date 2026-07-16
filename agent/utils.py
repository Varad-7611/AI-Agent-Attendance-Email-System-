from datetime import datetime

def get_today_date_str(format_str: str = "%d-%m-%Y") -> str:
    """Returns today's date formatted as a string."""
    return datetime.now().strftime(format_str)

def get_current_month_str() -> str:
    """Returns current month/year to filter whole month files (e.g. -07-2026)"""
    return datetime.now().strftime("-%m-%Y")
