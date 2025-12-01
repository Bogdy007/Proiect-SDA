Inventar Echipamente IT — Frontend + API

A small internal web application for tracking IT equipment and peripherals. The project contains a static frontend (HTML/CSS/vanilla JS) and a Python Flask backend that exposes a REST-style API and generates printable PDF sheets for assets.

The UI is in Romanian and targets internal use (Parchetul de pe lângă Tribunalul Brașov).


## Overview
- Frontend: static pages (`index.html`, `detalii.html`, `formular.html`, `select_type.html`) styled with `style.css` and using Font Awesome CDN.
- Backend: `Flask` app in `main.py` providing endpoints for listing, viewing, adding, updating, deleting assets and interventions, plus generating PDFs with `fpdf2` using the bundled `DejaVuSans.ttf` font.
- Database: MySQL (credentials currently hardcoded in `main.py`).
- PDF: Generated via the `/api/print/<nr_inventar>` endpoint.


## Tech Stack
- Language: Python 3.10+ (recommended)
- Frameworks/Libraries (Backend):
  - Flask
  - flask-cors
  - mysql-connector-python
  - fpdf2
- Frontend: HTML5, CSS3, vanilla JavaScript, Font Awesome (CDN)
- Database: MySQL 8.x (table names: `Echipamente`, `Periferice`, `Interventii` assumed by code)


## Project Structure
Frontend/
- DejaVuSans.ttf               — Font used by fpdf2 for Unicode PDFs
- detalii.html                 — Details page for a selected asset
- formular.html                — Form page (add/edit equipment/peripheral)
- images/logo_intro.png        — Logo used in UI and favicon
- index.html                   — Main listing & filtering page
- main.py                      — Flask backend (API + PDF)
- select_type.html             — Select type of item to add
- style.css                    — Global styles


## Backend API — Entry Point and Endpoints
- Entry point file: `main.py`
- Flask app variable: `app`
- CORS: enabled for all origins
- Detected routes (summary):
  - GET `/api/assets/all` — list (with filters via query params: `nr_inventar`, `utilizator`, `etaj`, `nume`, `serie`, `ip`, `tip`)
  - GET `/api/echipament/<nr_inventar>` — details for an equipment row (table `Echipamente`)
  - GET `/api/periferic/<nr_inventar>` — details for a peripheral row (table `Periferice`)
  - POST `/api/echipamente/add` — add equipment
  - POST `/api/periferice/add` — add peripheral
  - PUT `/api/echipamente/update/<id_vechi>` — update equipment (by old inventory id)
  - PUT `/api/periferice/update/<id_vechi>` — update peripheral (by old inventory id)
  - POST `/api/assets/delete/<nr_inventar>` — delete asset (equipment or peripheral)
  - GET `/api/interventii/<nr_inventar>` — list interventions for an asset
  - POST `/api/interventii/add` — add intervention
  - GET `/api/print/<nr_inventar>` — generate asset sheet as PDF

Note: There is no `if __name__ == "__main__": app.run()` block; use Flask CLI to run.


## Requirements
- Python 3.10 or newer
- MySQL server (local or remote)
- Pip (Python package installer)

Python packages (install manually if `requirements.txt` is not present):
- Flask
- flask-cors
- mysql-connector-python
- fpdf2

TODO: Add a `requirements.txt` file with pinned versions.


## Configuration (Environment Variables)
Database credentials are currently hardcoded in `main.py` as:

data_base = {
    'host': 'localhost',
    'database': 'inventar_it',
    'user': 'root',
    'password': 'root',
    'port': 3306
}

Recommended: move these to environment variables and read them in `main.py`. Suggested variables:
- `DB_HOST`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_PORT` (optional, default 3306)

TODO: Refactor `main.py` to load DB config from environment variables safely.


## Setup and Run
1) Create and activate a virtual environment (recommended):

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

2) Install dependencies:

pip install Flask flask-cors mysql-connector-python fpdf2

3) Prepare the MySQL database:
- Create database `inventar_it` (or your preferred name)
- Create tables `Echipamente`, `Periferice`, and `Interventii` with the columns used in the code
- Ensure user credentials match those configured in `main.py`

TODO: Provide schema (DDL) scripts for all tables.

4) Run the backend (Flask CLI):

# from the project root where main.py lives
export FLASK_APP=main.py           # PowerShell: $env:FLASK_APP = "main.py"
export FLASK_ENV=development       # optional for auto-reload; PS: $env:FLASK_ENV = "development"
flask run --host=127.0.0.1 --port=5000

The API will be available at http://127.0.0.1:5000

5) Open the frontend:
- Simply open `index.html` in your browser, or
- Serve the folder over a simple HTTP server (helps with relative paths):

# Python 3
python -m http.server 8080
# then navigate to http://127.0.0.1:8080/index.html

The frontend expects the API at http://127.0.0.1:5000 (see JS constants in HTML files). Adjust if running on a different host/port.


## Scripts and Useful Commands
- Install dependencies: `pip install Flask flask-cors mysql-connector-python fpdf2`
- Start backend (dev): `FLASK_APP=main.py flask run`
- Serve static frontend locally: `python -m http.server 8080`
- Generate a PDF for a given asset: open `http://127.0.0.1:5000/api/print/<NR_INVENTAR>` in the browser



## Environment and Assets
- Font file `DejaVuSans.ttf` must remain accessible relative to `main.py` for PDF generation via fpdf2 (`pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)`).
- CORS is enabled with `flask-cors` allowing the static frontend to call the API from `file://` or another port.


## Acknowledgements
- Font Awesome for icons (loaded via CDN)
- fpdf2 for PDF generation
