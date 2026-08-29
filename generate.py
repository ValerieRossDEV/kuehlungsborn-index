from __future__ import annotations

import os
import shutil

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from kuehlungsborn.artwork import render_daily_image
from kuehlungsborn.gallery import build_gallery
from kuehlungsborn.scoring import calculate_assessment
from kuehlungsborn.weather import TIMEZONE, fetch_conditions


ROOT = Path(__file__).parent
DOCS = ROOT / "docs"
ARCHIVE = DOCS / "archive"


FORCE = (
    os.getenv(
        "FORCE",
        "0",
    )
    == "1"
)


def main() -> None:
    now = datetime.now(
        ZoneInfo(TIMEZONE)
    )

    today = now.strftime(
        "%Y-%m-%d"
    )

    output = (
        ARCHIVE
        / f"{today}.png"
    )

    if output.exists() and not FORCE:
        print(
            f"Skipping: {output.name} already exists."
        )
        return

    conditions = fetch_conditions()

    assessment = calculate_assessment(
        conditions,
        now,
    )

    render_daily_image(
        path=output,
        now=now,
        c=conditions,
        assessment=assessment,
    )

    shutil.copyfile(
        output,
        DOCS / "latest.png",
    )

    build_gallery(ROOT)

    print(f"Created {output}")
    print(
        f"Möwenrisiko: {assessment.gull_risk}% "
        f"({assessment.gull_risk_summary})"
    )


if __name__ == "__main__":
    main()
