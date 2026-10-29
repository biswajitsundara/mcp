
"""Open-Meteo API service methods."""

import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


async def find_city(client: httpx.AsyncClient, city: str) -> dict:
    """Resolve a city name to coordinates."""

    response = await client.get(
        GEOCODING_URL,
        params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        },
    )
    response.raise_for_status()

    locations = response.json().get("results", [])

    if not locations:
        raise ValueError(f"No location found for '{city}'.")

    location = locations[0]

    return {
        "city": location["name"],
        "country": location.get("country"),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
    }


async def fetch_current_weather(
    client: httpx.AsyncClient,
    latitude: float,
    longitude: float,
) -> dict:
    """Fetch and normalize current weather data."""

    response = await client.get(
        WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,"
                "apparent_temperature,"
                "relative_humidity_2m,"
                "wind_speed_10m,"
                "weather_code"
            ),
            "timezone": "auto",
        },
    )
    response.raise_for_status()

    current = response.json().get("current")

    if not current:
        raise RuntimeError("No current weather data returned.")

    return {
        "temperature_c": current["temperature_2m"],
        "feels_like_c": current["apparent_temperature"],
        "humidity_percent": current["relative_humidity_2m"],
        "wind_speed_kmh": current["wind_speed_10m"],
        "observed_at": current["time"],
    }
