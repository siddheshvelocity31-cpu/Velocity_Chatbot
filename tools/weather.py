"""Weather lookup tool for the Gemini Chatbot."""

from typing import Dict, Any

# Mock weather database for demonstration
MOCK_WEATHER_DATA: Dict[str, Dict[str, Any]] = {
    "tokyo": {
        "city": "Tokyo",
        "country": "Japan",
        "temperature_c": 18,
        "temperature_f": 64.4,
        "condition": "Clear and Sunny",
        "humidity": "45%",
        "wind_speed": "12 km/h",
    },
    "london": {
        "city": "London",
        "country": "United Kingdom",
        "temperature_c": 11,
        "temperature_f": 51.8,
        "condition": "Light Rain",
        "humidity": "82%",
        "wind_speed": "20 km/h",
    },
    "new york": {
        "city": "New York",
        "country": "United States",
        "temperature_c": 15,
        "temperature_f": 59.0,
        "condition": "Partly Cloudy",
        "humidity": "58%",
        "wind_speed": "15 km/h",
    },
    "paris": {
        "city": "Paris",
        "country": "France",
        "temperature_c": 14,
        "temperature_f": 57.2,
        "condition": "Breezy",
        "humidity": "60%",
        "wind_speed": "18 km/h",
    },
    "san francisco": {
        "city": "San Francisco",
        "country": "United States",
        "temperature_c": 16,
        "temperature_f": 60.8,
        "condition": "Foggy",
        "humidity": "75%",
        "wind_speed": "14 km/h",
    },
    "mumbai": {
        "city": "Mumbai",
        "country": "India",
        "temperature_c": 31,
        "temperature_f": 87.8,
        "condition": "Warm and Humid",
        "humidity": "78%",
        "wind_speed": "10 km/h",
    },
    "delhi": {
        "city": "New Delhi",
        "country": "India",
        "temperature_c": 34,
        "temperature_f": 93.2,
        "condition": "Hot and Sunny",
        "humidity": "52%",
        "wind_speed": "9 km/h",
    },
    "bengaluru": {
        "city": "Bengaluru",
        "country": "India",
        "temperature_c": 24,
        "temperature_f": 75.2,
        "condition": "Pleasant and Scattered Clouds",
        "humidity": "62%",
        "wind_speed": "8 km/h",
    },
    "chennai": {
        "city": "Chennai",
        "country": "India",
        "temperature_c": 33,
        "temperature_f": 91.4,
        "condition": "Hot and Humid",
        "humidity": "80%",
        "wind_speed": "11 km/h",
    },
    "hyderabad": {
        "city": "Hyderabad",
        "country": "India",
        "temperature_c": 29,
        "temperature_f": 84.2,
        "condition": "Warm with Light Clouds",
        "humidity": "58%",
        "wind_speed": "10 km/h",
    },
    "kolkata": {
        "city": "Kolkata",
        "country": "India",
        "temperature_c": 30,
        "temperature_f": 86.0,
        "condition": "Warm and Partly Cloudy",
        "humidity": "72%",
        "wind_speed": "7 km/h",
    },
    "pune": {
        "city": "Pune",
        "country": "India",
        "temperature_c": 27,
        "temperature_f": 80.6,
        "condition": "Pleasant with Light Breeze",
        "humidity": "60%",
        "wind_speed": "10 km/h",
    },
    "jaipur": {
        "city": "Jaipur",
        "country": "India",
        "temperature_c": 35,
        "temperature_f": 95.0,
        "condition": "Hot and Dry",
        "humidity": "30%",
        "wind_speed": "12 km/h",
    },
    "ahmedabad": {
        "city": "Ahmedabad",
        "country": "India",
        "temperature_c": 36,
        "temperature_f": 96.8,
        "condition": "Scorching Hot",
        "humidity": "27%",
        "wind_speed": "9 km/h",
    },
    "dubai": {
        "city": "Dubai",
        "country": "United Arab Emirates",
        "temperature_c": 41,
        "temperature_f": 105.8,
        "condition": "Hot and Sunny",
        "humidity": "38%",
        "wind_speed": "16 km/h",
    },
    "sydney": {
        "city": "Sydney",
        "country": "Australia",
        "temperature_c": 20,
        "temperature_f": 68.0,
        "condition": "Sunny with Mild Breeze",
        "humidity": "55%",
        "wind_speed": "19 km/h",
    },
    "toronto": {
        "city": "Toronto",
        "country": "Canada",
        "temperature_c": 8,
        "temperature_f": 46.4,
        "condition": "Overcast and Cool",
        "humidity": "70%",
        "wind_speed": "22 km/h",
    },
    "berlin": {
        "city": "Berlin",
        "country": "Germany",
        "temperature_c": 10,
        "temperature_f": 50.0,
        "condition": "Cloudy with Drizzle",
        "humidity": "77%",
        "wind_speed": "17 km/h",
    },
    "rome": {
        "city": "Rome",
        "country": "Italy",
        "temperature_c": 22,
        "temperature_f": 71.6,
        "condition": "Warm and Clear",
        "humidity": "50%",
        "wind_speed": "12 km/h",
    },
    "beijing": {
        "city": "Beijing",
        "country": "China",
        "temperature_c": 16,
        "temperature_f": 60.8,
        "condition": "Hazy",
        "humidity": "48%",
        "wind_speed": "13 km/h",
    },
    "shanghai": {
        "city": "Shanghai",
        "country": "China",
        "temperature_c": 19,
        "temperature_f": 66.2,
        "condition": "Partly Cloudy",
        "humidity": "65%",
        "wind_speed": "14 km/h",
    },
    "singapore": {
        "city": "Singapore",
        "country": "Singapore",
        "temperature_c": 30,
        "temperature_f": 86.0,
        "condition": "Tropical and Humid",
        "humidity": "83%",
        "wind_speed": "9 km/h",
    },
    "seoul": {
        "city": "Seoul",
        "country": "South Korea",
        "temperature_c": 14,
        "temperature_f": 57.2,
        "condition": "Partly Cloudy",
        "humidity": "55%",
        "wind_speed": "15 km/h",
    },
    "moscow": {
        "city": "Moscow",
        "country": "Russia",
        "temperature_c": 3,
        "temperature_f": 37.4,
        "condition": "Cold and Snowy",
        "humidity": "85%",
        "wind_speed": "20 km/h",
    },
    "sao paulo": {
        "city": "São Paulo",
        "country": "Brazil",
        "temperature_c": 25,
        "temperature_f": 77.0,
        "condition": "Warm with Afternoon Showers",
        "humidity": "74%",
        "wind_speed": "11 km/h",
    },
    "los angeles": {
        "city": "Los Angeles",
        "country": "United States",
        "temperature_c": 23,
        "temperature_f": 73.4,
        "condition": "Sunny and Clear",
        "humidity": "42%",
        "wind_speed": "12 km/h",
    },
    "chicago": {
        "city": "Chicago",
        "country": "United States",
        "temperature_c": 12,
        "temperature_f": 53.6,
        "condition": "Windy and Cloudy",
        "humidity": "65%",
        "wind_speed": "30 km/h",
    },
    "bangkok": {
        "city": "Bangkok",
        "country": "Thailand",
        "temperature_c": 32,
        "temperature_f": 89.6,
        "condition": "Hot and Partly Cloudy",
        "humidity": "76%",
        "wind_speed": "10 km/h",
    },
    "istanbul": {
        "city": "Istanbul",
        "country": "Turkey",
        "temperature_c": 17,
        "temperature_f": 62.6,
        "condition": "Mild with Light Clouds",
        "humidity": "60%",
        "wind_speed": "16 km/h",
    },
    "amsterdam": {
        "city": "Amsterdam",
        "country": "Netherlands",
        "temperature_c": 9,
        "temperature_f": 48.2,
        "condition": "Rainy and Windy",
        "humidity": "88%",
        "wind_speed": "25 km/h",
    },
    "madrid": {
        "city": "Madrid",
        "country": "Spain",
        "temperature_c": 20,
        "temperature_f": 68.0,
        "condition": "Sunny and Warm",
        "humidity": "40%",
        "wind_speed": "14 km/h",
    },
    "cairo": {
        "city": "Cairo",
        "country": "Egypt",
        "temperature_c": 36,
        "temperature_f": 96.8,
        "condition": "Hot and Dry",
        "humidity": "28%",
        "wind_speed": "13 km/h",
    },
    "nairobi": {
        "city": "Nairobi",
        "country": "Kenya",
        "temperature_c": 20,
        "temperature_f": 68.0,
        "condition": "Pleasant and Partly Cloudy",
        "humidity": "62%",
        "wind_speed": "10 km/h",
    },
    "mexico city": {
        "city": "Mexico City",
        "country": "Mexico",
        "temperature_c": 19,
        "temperature_f": 66.2,
        "condition": "Mild with Clouds",
        "humidity": "55%",
        "wind_speed": "11 km/h",
    },
    "kuala lumpur": {
        "city": "Kuala Lumpur",
        "country": "Malaysia",
        "temperature_c": 31,
        "temperature_f": 87.8,
        "condition": "Hot with Afternoon Thunderstorms",
        "humidity": "82%",
        "wind_speed": "8 km/h",
    },
    "jakarta": {
        "city": "Jakarta",
        "country": "Indonesia",
        "temperature_c": 30,
        "temperature_f": 86.0,
        "condition": "Hot and Humid",
        "humidity": "80%",
        "wind_speed": "9 km/h",
    },
    "riyadh": {
        "city": "Riyadh",
        "country": "Saudi Arabia",
        "temperature_c": 43,
        "temperature_f": 109.4,
        "condition": "Extremely Hot and Dry",
        "humidity": "15%",
        "wind_speed": "14 km/h",
    },
    "johannesburg": {
        "city": "Johannesburg",
        "country": "South Africa",
        "temperature_c": 17,
        "temperature_f": 62.6,
        "condition": "Mild and Clear",
        "humidity": "45%",
        "wind_speed": "12 km/h",
    },
}


# Country / region name → representative city alias map
# Used to resolve when Gemini model passes a country name instead of a city
COUNTRY_ALIASES: Dict[str, str] = {
    # India
    "india": "mumbai",
    "indian": "mumbai",
    # Japan
    "japan": "tokyo",
    "japanese": "tokyo",
    # United Kingdom
    "uk": "london",
    "united kingdom": "london",
    "england": "london",
    "britain": "london",
    "great britain": "london",
    # United States
    "usa": "new york",
    "us": "new york",
    "united states": "new york",
    "america": "new york",
    # France
    "france": "paris",
    "french": "paris",
    # Germany
    "germany": "berlin",
    "german": "berlin",
    # Italy
    "italy": "rome",
    "italian": "rome",
    # Spain
    "spain": "madrid",
    "spanish": "madrid",
    # Netherlands
    "netherlands": "amsterdam",
    "holland": "amsterdam",
    "dutch": "amsterdam",
    # Russia
    "russia": "moscow",
    "russian": "moscow",
    # China
    "china": "beijing",
    "chinese": "beijing",
    # South Korea
    "south korea": "seoul",
    "korea": "seoul",
    "korean": "seoul",
    # Thailand
    "thailand": "bangkok",
    "thai": "bangkok",
    # Malaysia
    "malaysia": "kuala lumpur",
    # Indonesia
    "indonesia": "jakarta",
    # UAE
    "uae": "dubai",
    "united arab emirates": "dubai",
    # Saudi Arabia
    "saudi arabia": "riyadh",
    "saudi": "riyadh",
    # Turkey
    "turkey": "istanbul",
    "turkish": "istanbul",
    # Egypt
    "egypt": "cairo",
    "egyptian": "cairo",
    # Brazil
    "brazil": "sao paulo",
    "brazilian": "sao paulo",
    # Canada
    "canada": "toronto",
    "canadian": "toronto",
    # Mexico
    "mexico": "mexico city",
    "mexican": "mexico city",
    # Australia
    "australia": "sydney",
    "australian": "sydney",
    # Kenya
    "kenya": "nairobi",
    "kenyan": "nairobi",
    # South Africa
    "south africa": "johannesburg",
    # Singapore
    "singapore": "singapore",
    # New Delhi aliases
    "new delhi": "delhi",
    "delhi ncr": "delhi",
    # City aliases
    "bangalore": "bengaluru",
    "calcutta": "kolkata",
    "madras": "chennai",
    "bombay": "mumbai",
    "la": "los angeles",
    "nyc": "new york",
    "sf": "san francisco",
}


def get_current_weather(city: str) -> Dict[str, Any]:
    """Get current weather conditions and temperature for a given city or country.

    Args:
        city: The name of the city or country the user specifically mentioned.
              Examples: 'India', 'Mumbai', 'Delhi', 'London', 'New York', 'Tokyo', 'Dubai'.
              Always pass exactly what the user asked about — if user says 'India' pass 'India',
              if user says 'Mumbai' pass 'Mumbai', if user says 'Japan' pass 'Japan'.
              Do NOT default to Tokyo or any other city when the user asked about a different country.

    Returns:
        A dictionary containing temperature, weather condition, humidity, and wind speed.
    """
    normalized_city = city.strip().lower()

    # Resolve country names and aliases to representative city
    if normalized_city in COUNTRY_ALIASES:
        normalized_city = COUNTRY_ALIASES[normalized_city]

    if normalized_city in MOCK_WEATHER_DATA:
        return {
            "status": "success",
            "data": MOCK_WEATHER_DATA[normalized_city]
        }

    # Generic fallback response for unmocked cities
    return {
        "status": "success",
        "data": {
            "city": city.title(),
            "country": "Unknown Region",
            "temperature_c": 21,
            "temperature_f": 69.8,
            "condition": "Partly Cloudy",
            "humidity": "55%",
            "wind_speed": "10 km/h",
            "note": "Standard simulated weather reading"
        }
    }
