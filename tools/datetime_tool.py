"""Date and time lookup tool for the Gemini Chatbot."""

from datetime import datetime, timezone
import zoneinfo
from typing import Dict, Any


def get_current_time(tz_name: str = "UTC") -> Dict[str, Any]:
    """Get the current date, time, and day of the week for a specific timezone.

    Args:
        tz_name: Standard timezone name (e.g. 'UTC', 'Asia/Kolkata', 'America/New_York', 'Europe/London', 'Asia/Tokyo'). Defaults to 'UTC'.

    Returns:
        A dictionary with ISO datetime, formatted time, timezone name, and day of week.
    """
    try:
        aliases = {
            "ist": "Asia/Kolkata",
            "india": "Asia/Kolkata",
            "est": "America/New_York",
            "edt": "America/New_York",
            "pst": "America/Los_Angeles",
            "pdt": "America/Los_Angeles",
            "gmt": "UTC",
            "bst": "Europe/London",
            "tokyo": "Asia/Tokyo",
            "london": "Europe/London",
        }
        
        lookup_tz = aliases.get(tz_name.strip().lower(), tz_name.strip())
        
        try:
            tz = zoneinfo.ZoneInfo(lookup_tz)
        except Exception:
            tz = timezone.utc
            lookup_tz = "UTC (fallback)"

        now = datetime.now(tz)
        return {
            "status": "success",
            "timezone": lookup_tz,
            "current_time": now.strftime("%I:%M:%S %p"),
            "current_date": now.strftime("%Y-%m-%d"),
            "day_of_week": now.strftime("%A"),
            "iso_format": now.isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to get time for timezone '{tz_name}': {str(e)}"
        }
