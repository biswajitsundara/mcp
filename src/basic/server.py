"""MCP SERVER: exposes weather tools. Knows nothing about LLMs."""

from fastmcp import FastMCP

mcp = FastMCP("Weather Server")

# Mock data so the demo needs no API keys.
WEATHER = {
    "london": {"temp_c": 14, "condition": "Cloudy", "humidity": 78, "wind_kph": 18},
    "tokyo": {"temp_c": 22, "condition": "Sunny", "humidity": 55, "wind_kph": 9},
    "new york": {"temp_c": 11, "condition": "Rainy", "humidity": 85, "wind_kph": 24},
    "mumbai": {"temp_c": 31, "condition": "Humid", "humidity": 88, "wind_kph": 12},
    "delhi": {"temp_c": 36, "condition": "Hazy", "humidity": 40, "wind_kph": 10},
}

AQI = {"london": 42, "tokyo": 35, "new york": 58, "mumbai": 120, "delhi": 210}

SUN = {
    "london": ("06:52", "17:05"),
    "tokyo": ("06:03", "16:58"),
    "new york": ("06:48", "17:52"),
    "mumbai": ("06:35", "18:04"),
    "delhi": ("06:40", "17:48"),
}


def _lookup(table: dict, city: str):
    """Case-insensitive lookup with a clear error message for unknown cities."""
    key = city.strip().lower()
    if key not in table:
        raise ValueError(
            f"No data for '{city}'. Available cities: {', '.join(sorted(table))}"
        )
    return table[key]


@mcp.tool
def get_weather(city: str) -> dict:
    """Get the current weather for a city (mock data for the demo)."""
    return {"city": city, **_lookup(WEATHER, city)}


@mcp.tool
def get_air_quality(city: str) -> dict:
    """Get the air quality index (AQI) and health category for a city."""
    aqi = _lookup(AQI, city)
    if aqi <= 50:
        category = "Good"
    elif aqi <= 100:
        category = "Moderate"
    elif aqi <= 150:
        category = "Unhealthy for sensitive groups"
    else:
        category = "Unhealthy"
    return {"city": city, "aqi": aqi, "category": category}


@mcp.tool
def get_sunrise_sunset(city: str) -> dict:
    """Get today's local sunrise and sunset times for a city."""
    sunrise, sunset = _lookup(SUN, city)
    return {"city": city, "sunrise": sunrise, "sunset": sunset}


# Run this in the CLI : uv run src/basic/server.py
# Streamable HTTP transport; endpoint is http://127.0.0.1:8000/mcp
if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8000)
