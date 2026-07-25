# Crescent Lake Capital — VPA TradingBot

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

## Project structure

```text
app.py
assets/
components/
core/
data/
pages/
.streamlit/
```
