# Crescent Lake Capital — VPA Trading Platform v5

## Improvements in v5

- No automatic page list on the login screen
- Theme selection moved to Settings
- Last selected theme is retained in session and URL
- Centered branding on login and sidebar
- Separate high-contrast logo assets for Light and Dark modes
- Product renamed to VPA Trading Platform
- Streamlit page modules renamed from `pages/` to `views/` to prevent automatic navigation

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

## Required repository structure

```text
app.py
requirements.txt
README.md
assets/
components/
core/
data/
views/
.streamlit/
```
