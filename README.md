# Kühlungsborn heute

Tägliche generative Wettergrafik für Kühlungsborn.

Nachsehen unter dem Ordner docs/archive.

## Enthalten

- Python
- Pydantic
- Pillow
- Jinja2
- GitHub Actions
- GitHub Pages

## Daten

- Wetterdaten: Open-Meteo
- Meeresdaten: Open-Meteo
- `WELLE MAX`: Tagesmaximum der signifikanten Wellenhöhe

## Möwenrisiko™

Das Möwenrisiko ist absichtlich ein humorvoller, nicht wissenschaftlicher Index.

Jeder Render zeigt:
- den Prozentwert
- eine kurze Einordnung
- den Hinweis `MÖWENRISIKO™: WISSENSCHAFTLICH VOLLKOMMEN UNBELEGT.`

Die konkrete Rechenformel bleibt bewusst intern und wird nicht im Render angezeigt.

Im Render stehen nur:
- Prozentwert
- kurze Einordnung
- `MÖWENRISIKO™: WISSENSCHAFTLICH VOLLKOMMEN UNBELEGT.`

## Lokal

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
FORCE=1 python generate.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:FORCE="1"
python generate.py
```

## GitHub Pages

- Settings
- Pages
- Deploy from a branch
- `main`
- `/docs`
