from pydantic import BaseModel, ConfigDict, Field


class Conditions(BaseModel):
    model_config = ConfigDict(frozen=True)

    temperature: float
    feels_like: float
    precipitation: float = Field(ge=0)
    weather_code: int = Field(ge=0)
    cloud_cover: int = Field(ge=0, le=100)

    wind_speed: float = Field(ge=0)
    wind_direction: float = Field(ge=0, le=360)
    wind_gusts: float = Field(ge=0)

    temp_max: float
    temp_min: float
    rain_probability: int = Field(ge=0, le=100)
    sunshine_hours: float = Field(ge=0, le=24)

    wave_height_max: float | None = Field(default=None, ge=0)
    wave_direction: float | None = Field(default=None, ge=0, le=360)
    wave_period: float | None = Field(default=None, ge=0)
    sea_temperature: float | None = None


class DailyAssessment(BaseModel):
    model_config = ConfigDict(frozen=True)

    score: int = Field(ge=0, le=100)
    gull_risk: int = Field(ge=0, le=100)

    verdict: str = Field(min_length=1)
    verdict_subtitle: str = Field(min_length=1)

    gull_risk_summary: str = Field(min_length=1)
