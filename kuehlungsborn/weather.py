import httpx

from .models import Conditions


LAT = 54.15
LON = 11.75
TIMEZONE = "Europe/Berlin"

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    return float(value)


def _first_or_none(values: object) -> object | None:
    if not values:
        return None
    if isinstance(values, list):
        return values[0] if values else None
    return None


def fetch_conditions() -> Conditions:
    weather_params = {
        "latitude": LAT,
        "longitude": LON,
        "timezone": TIMEZONE,
        "forecast_days": 1,
        "current": ",".join(
            [
                "temperature_2m",
                "apparent_temperature",
                "precipitation",
                "weather_code",
                "cloud_cover",
                "wind_speed_10m",
                "wind_direction_10m",
                "wind_gusts_10m",
            ]
        ),
        "daily": ",".join(
            [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_max",
                "sunshine_duration",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
            ]
        ),
    }

    marine_params = {
        "latitude": LAT,
        "longitude": LON,
        "timezone": TIMEZONE,
        "forecast_days": 1,
        "current": "sea_surface_temperature",
        "daily": ",".join(
            [
                "wave_height_max",
                "wave_direction_dominant",
                "wave_period_max",
            ]
        ),
    }

    with httpx.Client(timeout=15.0) as client:
        weather_response = client.get(
            WEATHER_URL,
            params=weather_params,
        )
        weather_response.raise_for_status()
        weather = weather_response.json()

        marine: dict = {}

        try:
            marine_response = client.get(
                MARINE_URL,
                params=marine_params,
            )
            marine_response.raise_for_status()
            marine = marine_response.json()
        except httpx.HTTPError:
            marine = {}

    current = weather["current"]
    daily = weather["daily"]

    sea = marine.get("current", {})
    marine_daily = marine.get("daily", {})

    return Conditions(
        temperature=current["temperature_2m"],
        feels_like=current["apparent_temperature"],
        precipitation=current["precipitation"],
        weather_code=current["weather_code"],
        cloud_cover=current["cloud_cover"],
        wind_speed=current["wind_speed_10m"],
        wind_direction=current["wind_direction_10m"],
        wind_gusts=current["wind_gusts_10m"],
        temp_max=daily["temperature_2m_max"][0],
        temp_min=daily["temperature_2m_min"][0],
        rain_probability=(
            daily["precipitation_probability_max"][0] or 0
        ),
        sunshine_hours=(
            daily["sunshine_duration"][0] or 0
        ) / 3600,
        wave_height_max=_optional_float(
            _first_or_none(
                marine_daily.get("wave_height_max")
            )
        ),
        wave_direction=_optional_float(
            _first_or_none(
                marine_daily.get("wave_direction_dominant")
            )
        ),
        wave_period=_optional_float(
            _first_or_none(
                marine_daily.get("wave_period_max")
            )
        ),
        sea_temperature=_optional_float(
            sea.get("sea_surface_temperature")
        ),
    )
