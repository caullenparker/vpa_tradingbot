# Crescent Lake Capital Trading Platform — Version 4

A modular Streamlit platform for:

- Dashboard
- VPA Market Scanner
- Portfolio
- Performance Tracker
- Trade Journal
- Bot Control Center
- Settings
- Crescent Lake Capital branding
- Light and dark themes

## Local run

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Render

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
python -m streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

Environment variables:

```text
APP_USERNAME
APP_PASSWORD
```

## Important GitHub upload rule

Upload the contents of this folder to the repository root.

The repository root must show:

```text
app.py
requirements.txt
README.md
assets/
components/
core/
data/
pages/
.streamlit/
```

Do not upload only the three top-level files. The folders are required.
