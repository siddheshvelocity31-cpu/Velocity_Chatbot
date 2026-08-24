"""Tools package exporting all callable functions and metadata for Gemini."""

from tools.weather import get_current_weather
from tools.calculator import calculate_expression
from tools.database import search_knowledge_base
from tools.datetime_tool import get_current_time
from tools.automotive import get_car_details
from tools.gadgets import get_laptop_specs, get_mobile_specs
from tools.travel import get_holiday_package

AVAILABLE_TOOLS = [
    get_current_weather,
    calculate_expression,
    search_knowledge_base,
    get_current_time,
    get_car_details,
    get_laptop_specs,
    get_mobile_specs,
    get_holiday_package,
]

TOOL_METADATA = {
    "get_current_weather": {
        "description": "Fetches current weather and temperature for any city",
        "icon": "🌤️"
    },
    "calculate_expression": {
        "description": "Calculates math equations safely",
        "icon": "🧮"
    },
    "search_knowledge_base": {
        "description": "Searches policies, company knowledge, and FAQ",
        "icon": "📚"
    },
    "get_current_time": {
        "description": "Gets current date and time for any world timezone",
        "icon": "🕒"
    },
    "get_car_details": {
        "description": "Looks up car specs, horsepower, 0-60, range, and pricing",
        "icon": "🏎️"
    },
    "get_laptop_specs": {
        "description": "Provides detailed specs, CPU, RAM, display, and pricing for any laptop",
        "icon": "💻"
    },
    "get_mobile_specs": {
        "description": "Provides camera, processor, battery, and specs for any mobile phone",
        "icon": "📱"
    },
    "get_holiday_package": {
        "description": "Calculates holiday package estimates with round-trip train/flight costs and cheapest to richest hotels",
        "icon": "🏖️"
    },
}

__all__ = [
    "get_current_weather",
    "calculate_expression",
    "search_knowledge_base",
    "get_current_time",
    "get_car_details",
    "get_laptop_specs",
    "get_mobile_specs",
    "get_holiday_package",
    "AVAILABLE_TOOLS",
    "TOOL_METADATA",
]

