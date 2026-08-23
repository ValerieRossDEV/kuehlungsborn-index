from datetime import datetime

from .models import Conditions, DailyAssessment


def _clamp(value: float) -> int:
    return max(0, min(100, round(value)))


def calculate_score(c: Conditions) -> int:
    score = 46

    if 10 <= c.wind_speed < 20:
        score += 12
    elif 20 <= c.wind_speed < 35:
        score += 20
    elif 35 <= c.wind_speed < 50:
        score += 14
    elif c.wind_speed >= 50:
        score += 5

    if 16 <= c.temperature <= 24:
        score += 12
    elif 10 <= c.temperature < 16 or 24 < c.temperature <= 28:
        score += 7
    elif c.temperature > 28:
        score += 3

    score += min(c.sunshine_hours * 1.6, 14)
    score -= c.rain_probability * 0.10

    if c.wave_height_max is not None:
        if 0.4 <= c.wave_height_max <= 1.6:
            score += 8
        elif c.wave_height_max > 2.5:
            score -= 3

    return _clamp(score)


def calculate_gull_risk(
    c: Conditions,
    now: datetime,
) -> int:
    """
    Deliberately playful, non-scientific model.

    The calculation stays internal. The rendered poster only shows
    the resulting percentage, a short interpretation, and the
    disclaimer that the index is scientifically unsupported.
    """
    risk = 35

    if now.weekday() >= 5:
        risk += 12

    if c.temperature >= 18:
        risk += 12

    if c.wind_speed < 28:
        risk += 12
    elif c.wind_speed > 45:
        risk -= 10

    if c.rain_probability > 70:
        risk -= 12

    return _clamp(risk)


def gull_text(risk: int) -> str:
    if risk >= 80:
        return "POMMES GEHÖREN JETZT DER MÖWE."
    if risk >= 60:
        return "FISCHBRÖTCHEN NUR UNTER AUFSICHT."
    if risk >= 40:
        return "VERDÄCHTIGE BLICKE AUS DER LUFT."
    return "SNACKLAGE WEITGEHEND ENTSPANNT."


def sea_verdict(c: Conditions) -> tuple[str, str]:
    if c.wind_gusts >= 60 or (
        c.wind_speed >= 45
        and c.rain_probability >= 70
    ):
        return (
            "NUR WENN DU WAS ZU BEWEISEN HAST.",
            "HEUTE GEWINNT EHER DIE OSTSEE.",
        )

    if c.rain_probability >= 75:
        return (
            "JA. ABER WASSERDICHT.",
            "MEER JA, FRISUR NEIN.",
        )

    if c.wind_speed >= 32:
        return (
            "JA. ABER JACKE.",
            "SOLIDER KÜHLUNGSBORNER SEITENWIND.",
        )

    if c.temperature >= 24 and c.rain_probability < 35:
        return (
            "JA. SOFORT.",
            "BEVOR ALLE ANDEREN DIESELBE IDEE HABEN.",
        )

    if c.temperature < 8:
        return (
            "JA. MÜTZE.",
            "DIE OSTSEE HAT SCHLIESSLICH NICHT GESCHLOSSEN.",
        )

    if c.sunshine_hours >= 6 and c.rain_probability < 45:
        return (
            "JA.",
            "SIEHT VERDÄCHTIG ANGENEHM AUS.",
        )

    return (
        "JA. IST IMMERHIN KÜHLUNGSBORN.",
        "EIN BISSCHEN WETTER GEHÖRT DAZU.",
    )


def calculate_assessment(
    c: Conditions,
    now: datetime,
) -> DailyAssessment:
    verdict, subtitle = sea_verdict(c)
    gull_risk = calculate_gull_risk(c, now)

    return DailyAssessment(
        score=calculate_score(c),
        gull_risk=gull_risk,
        verdict=verdict,
        verdict_subtitle=subtitle,
        gull_risk_summary=gull_text(gull_risk),
    )


def score_text(score: int) -> str:
    if score >= 90:
        return "KÜHLUNGSBORN IN REINFORM"
    if score >= 75:
        return "ORDENTLICH KÜHLUNGSBORN"
    if score >= 55:
        return "ERKENNBAR KÜHLUNGSBORN"
    if score >= 35:
        return "HEUTE ETWAS ZURÜCKHALTEND"
    return "KÜHLUNGSBORN HAT HEUTE HOMEOFFICE"
