
"""MCP server: exposes weather tools with progress reporting."""

import httpx
from fastmcp import FastMCP, Context

from weather_service import find_city, fetch_current_weather

mcp = FastMCP("Weather Server")


@mcp.tool
async def get_weather(city: str, ctx: Context) -> dict:
    """Get current temperature, condition, humidity and wind for a city."""

    city = city.strip()

    if not city:
        raise ValueError("City cannot be empty.")

    async with httpx.AsyncClient(timeout=15.0) as client:

        # Stage 1: Geocoding
        await ctx.report_progress(
            progress=1,
            total=3,
            message=f"Finding location for {city}...",
        )

        try:
            location = await find_city(client, city)

            # Stage 2: Report that geocoding succeeded
            await ctx.report_progress(
                progress=2,
                total=3,
                message=(
                    f"Found {location['city']}, "
                    f"{location.get('country') or 'unknown country'}. "
                    "Fetching current weather..."
                ),
            )

            # Stage 3: Fetch current weather
            weather = await fetch_current_weather(
                client,
                location["latitude"],
                location["longitude"],
            )

            await ctx.report_progress(
                progress=3,
                total=3,
                message="Weather lookup complete.",
            )

        except httpx.HTTPError as exc:
            raise RuntimeError(
                "Unable to retrieve weather from Open-Meteo."
            ) from exc

    # Return only the fields useful to the AI agent.
    return {
        "city": location["city"],
        "country": location["country"],
        **weather,
    }


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000,
    )
