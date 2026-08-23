from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


def build_gallery(root: Path) -> None:
    docs = root / "docs"
    archive = docs / "archive"
    templates = root / "templates"

    environment = Environment(
        loader=FileSystemLoader(templates),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = environment.get_template("index.html.j2")

    images = []

    for image in sorted(
        archive.glob("*.png"),
        reverse=True,
    ):
        try:
            date = datetime.strptime(
                image.stem,
                "%Y-%m-%d",
            )
            label = date.strftime(
                "%d.%m.%Y"
            )
        except ValueError:
            label = image.stem

        images.append(
            {
                "filename": image.name,
                "date": label,
            }
        )

    html = template.render(
        images=images,
        latest=images[0] if images else None,
    )

    (
        docs / "index.html"
    ).write_text(
        html,
        encoding="utf-8",
    )
