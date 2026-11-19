# AgroMind AI

AgroMind AI is a lightweight Streamlit agriculture website for soil screening, crop and disease model workflows, Open-Meteo weather, irrigation estimates, farm risk, scenario simulation, and an optional Gemini assistant. It includes local account sign-in and keeps saved history scoped to the signed-in user. The deployed runtime excludes optional training, plotting, and TensorFlow dependencies.

> **Model integrity:** Crop and disease predictions are intentionally disabled until you provide documented datasets and train the included models. This application does not fabricate predictions or model accuracy.
>
> **Deployment status:** The app includes lightweight local authentication and is ready for a small demo deployment. Production use still needs email verification/password recovery, HTTPS, and a managed database. Crop/disease models need trained artifacts, and the Gemini assistant needs a secret key.

## Development progress

- [x] Phase 1 — Project setup and dashboard.
- [x] Phase 2 — Soil screening and validation.
- [ ] Phase 3 — Crop model workflow is implemented; training awaits the documented dataset.
- [x] Phase 4 — Open-Meteo weather integration and transparent risk rules.
- [x] Phase 5 — Irrigation screening estimate.
- [ ] Phase 6 — Disease model workflow is implemented; training awaits a separate train/test dataset and TensorFlow.
- [x] Phase 7 — Explainable Farm Risk Engine.
- [x] Phase 8 — What-if simulator.
- [ ] Phase 9 — Gemini integration is implemented; live answers await a configured API key.
- [x] Phase 10 — SQLite history, account sign-in, and automated tests. Demo deployment configuration is included; email verification, password recovery, and deployment-specific storage remain future work.

The local account system stores salted PBKDF2-SHA256 password hashes, limits repeated failed sign-in attempts, and signs users out after 30 minutes idle. Registration does not send verification email, and there is no password-reset flow; use HTTPS and a supported persistent database before opening the app to the public.

## Run locally

Use Python 3.11 for the app. Install only the core runtime requirements:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Create an account on the sign-in screen the first time you open the app. The app creates a local SQLite database at `data/agromind.db`. Set `AGROMIND_DATABASE_PATH` to use another location.

For development and tests, install the additional tools with `python -m pip install -r requirements-dev.txt`.

## Deploy with Docker

Docker deployment is the recommended prototype path because the Compose configuration keeps SQLite data in a persistent named volume:

```powershell
docker compose up --build -d
docker compose ps
```

Open `http://localhost:8501`. For the optional Gemini assistant, set `GEMINI_API_KEY` in the deployment environment before starting the service. Do not place keys in the image or commit them. To stop the service without deleting history, run `docker compose down`; the named volume remains. Back up the `agromind-data` volume before upgrades or host changes.

The container uses Python 3.11, installs only core app dependencies, runs as a non-root user, and has an HTTP health check. Docker must be installed and running on the deployment host.

## Deploy on Streamlit Community Cloud

Push this project to a GitHub repository, select `app.py` as the app entry point, and choose Python 3.11 in the deployment settings. Add optional credentials through the app's Streamlit secrets settings:

```toml
GEMINI_API_KEY = "your-key"
GEMINI_MODEL = "gemini-2.0-flash"
```

Community-hosted local SQLite files may not provide durable storage across rebuilds or instance replacement. Use Docker with a persistent volume for durable prototype history, or plan a supported managed database before production use.

## Optional Gemini assistant

For local development, set the API key in the shell before starting Streamlit:

```powershell
$env:GEMINI_API_KEY = "your-key"
streamlit run app.py
```

Do not commit real API keys. `.env.example` documents supported variables; the app reads environment variables directly.

## Project layout

- `app.py` — Sign-in gate and authenticated Streamlit page router.
- `pages/` — Soil, crop, disease, climate, water, risk, simulator, assistant, and history pages.
- `services/` — Soil, model inference, Open-Meteo, irrigation, risk, and Gemini logic.
- `services/auth_service.py` and `utils/auth_ui.py` — Password hashing, login throttling, and account UI.
- `models/` — Separate crop and MobileNetV2 training workflows.
- `database/` — SQLite schema and parameterized history helpers.
- `utils/` — Shared validation, constants, and UI helpers.
- `datasets/` — Empty dataset locations; provide documented, licensed datasets locally.
- `trained_models/` — Empty model artifact location; generated models are excluded from source control by default.
- `tests/` — Automated tests for calculations, validation, risk, database, and model-unavailable behavior.
- `Dockerfile`, `compose.yaml`, `.dockerignore` — Container build and deployment configuration.
- `requirements.txt`, `requirements-training.txt`, `requirements-dev.txt`, `requirements-disease.txt` — Core, optional training/test, and optional TensorFlow dependencies.
- `spec.md` — Full product requirements.

## Training the crop recommendation model

Place a documented public crop recommendation CSV at:

`datasets/crop_recommendation/Crop_recommendation.csv`

The CSV must include `N`, `P`, `K`, `temperature`, `humidity`, `ph`, `rainfall`, and `label` columns. Install the requirements and run:

```powershell
python -m models.train_crop_model
```

Install the extra training dependency first with `python -m pip install -r requirements-training.txt`. The script uses a held-out test split and saves the fitted model and measured evaluation report under `trained_models/`.

## Training disease detection

Install the optional, large disease-training dependencies with `python -m pip install -r requirements-disease.txt`, then place a documented image dataset in class-named folders:

```text
datasets/plant_disease/
  train/
    class_name/
      image.jpg
  test/
    class_name/
      image.jpg
```

Train and evaluate on the separate test folder:

```powershell
python -m models.train_disease_model
```

The model uses MobileNetV2 transfer learning. The initial workflow freezes the pretrained backbone; class coverage and dataset licensing/documentation must be checked before using results beyond a demo.

TensorFlow support varies by operating system and Python version. Use a TensorFlow-supported Python version (for example, Python 3.11) for this optional workflow; the core dashboard and non-TensorFlow modules can use the project environment shown above.

## Pages

The Streamlit app includes soil intelligence, crop recommendation, disease detection, climate intelligence, water management, farm risk, what-if simulation, AI assistant, and local history pages.

## Important limitations

- Soil nutrient bands and climate thresholds are generic screening defaults, not locally calibrated advice.
- Irrigation estimates require ET0 and Kc inputs and do not infer soil water-holding capacity; no water savings are claimed.
- Weather retrieval requires internet access and valid coordinates.
- Disease predictions cover only the model's training classes; low-confidence images are reported as uncertain.
- The risk score is an unweighted mean of available rule-based component scores. Missing inputs are listed, and the score is not a guarantee of farm performance.
- Accounts use locally stored password hashes; registration email verification and password recovery are not implemented. Configure HTTPS and durable, access-controlled storage for public use.
- Local SQLite storage is designed for a small single-instance demo, not concurrent multi-instance production use.

## Tests

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest
```

See [spec.md](./spec.md) for the full project requirements and planned development phases.
