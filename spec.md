# AgroMind AI — Project Specification

## Project overview

AgroMind AI is a beginner-friendly, AI/ML-based agriculture platform for farmers, agricultural students, and researchers. It brings soil analysis, crop recommendations, crop disease detection, weather risk analysis, and irrigation guidance into one application so users can make more informed, resource-efficient, and climate-resilient farming decisions.

**Core objective:** Transform available agricultural data into practical, understandable recommendations.

**Central innovation:** The Farm Risk Intelligence Engine combines outputs from the other modules and explains the resulting risks and recommended actions.

## Target users and experience

Build a professional, responsive AgriTech dashboard with a forest-green, emerald, white, light-green, and neutral-grey palette. Provide clear navigation, readable forms and results, charts, loading states, useful errors, and empty states. The app should be approachable to beginners without looking like a basic demo.

## Product modules

1. **Soil Intelligence**
   - Accept soil pH, nitrogen, phosphorus, potassium, moisture, and temperature; organic carbon is optional.
   - Assess fertility, identify potential nutrient deficiencies, and provide improvement suggestions.
   - Validate inputs and support saved soil reports.

2. **Crop Recommendation**
   - Use a trained Random Forest classifier with a documented public crop recommendation dataset.
   - Inputs: soil pH, N-P-K, temperature, humidity, and rainfall.
   - Return the top three suitable crops, suitability scores, growing-condition explanations, and precautions.
   - Keep training and inference separate; report only measured evaluation results.

3. **Crop Disease Detection**
   - Analyze uploaded leaf images using MobileNetV2 transfer learning and a documented dataset such as PlantVillage.
   - Show supported disease predictions, confidence, visible symptoms, and preventive guidance.
   - Clearly communicate uncertainty for unsupported, unclear, or low-confidence images.
   - Save detection records.

4. **Climate Intelligence**
   - Retrieve real weather information from the Open-Meteo API.
   - Show current conditions and rainfall forecasts, and assess drought, excess-rainfall, and heat-stress risks using transparent initial rules.
   - Distinguish observed/forecast weather from estimated agricultural risk and include crop-specific guidance where data supports it.

5. **Smart Water Management**
   - Initially accept manually entered soil moisture and use available crop and rainfall information to estimate crop water requirements and irrigation recommendations.
   - Explain the estimation logic and support water-usage records and reports.
   - Do not claim water savings without measured values and a clearly defined baseline.

6. **AI Farming Assistant**
   - Integrate Gemini through an environment-configured API key.
   - Support Hindi and English questions about farming and explain available soil, crop, disease, climate, and irrigation results.
   - Ground responses in available application data; do not invent measurements or predictions.
   - Handle missing configuration, API errors, and unavailable connectivity gracefully.

7. **Farm Risk Intelligence Engine**
   - Combine available soil, crop, disease, climate, and water information.
   - Report a farm health score from 0–100, soil condition, climate risk, crop health, water requirement status, and priority actions.
   - Use explainable scoring; show factors that increase or decrease risk and make missing inputs explicit.
   - Avoid arbitrary scores and unsupported conclusions.

8. **What-if Farm Simulator**
   - Let users vary rainfall, temperature, soil moisture, and irrigation availability.
   - Compare baseline and modified estimates for risk and water requirements.
   - Label all results as simulations, not guaranteed predictions.

9. **Reports and history**
   - Persist relevant reports, recommendations, detections, weather, irrigation, risk assessments, and assistant conversations with timestamps and applicable user/farm identifiers.

## Required pages

1. Landing Page
2. Login / Registration
3. Main Dashboard
4. Soil Intelligence
5. Crop Recommendation
6. Disease Detection
7. Climate Intelligence
8. Water Management
9. Farm Risk Intelligence
10. What-if Simulator
11. AI Farming Assistant
12. Reports and History

## Technology and architecture

Use the specified beginner-friendly stack:

- **Language and UI:** Python and Streamlit
- **Machine learning:** scikit-learn
- **Deep learning:** TensorFlow/Keras
- **Data:** Pandas and NumPy
- **Charts:** Plotly
- **Persistence:** SQLite
- **Weather:** Open-Meteo
- **Assistant:** Gemini API

Keep functionality modular. Do not introduce React, Node.js, MongoDB, or additional frameworks unless approved. Separate UI pages, services, model training/inference, database access, utilities, datasets, and tests rather than placing all logic in `app.py`.

The planned project structure includes `app.py`, `config.py`, `requirements.txt`, `README.md`, `.env.example`, `.gitignore`, a `pages/` directory, `models/`, `services/`, `database/`, `utils/`, `assets/`, `datasets/`, `notebooks/`, `trained_models/`, and `tests/`.

## Data, security, and reliability

- Use SQLite tables for users, farms, soil reports, crop recommendations, disease detections, weather records, irrigation records, risk assessments, and AI conversations.
- Use parameterized SQL queries. If authentication is implemented, hash passwords securely.
- Keep secrets in environment variables; `.env.example` contains placeholders only. Never commit actual API keys.
- Validate inputs and handle API failures, unavailable internet, missing data, unsupported inputs, and absent optional services explicitly.
- Keep the app usable without optional APIs wherever practical.
- Identify demo data clearly; never present fabricated model predictions, metrics, measurements, or savings as real.

## Machine-learning integrity

- Train a real Random Forest crop model with documented data, preprocessing, a train/test split, and suitable evaluation metrics.
- Train or fine-tune a real MobileNetV2 disease model with a documented dataset and separate test evaluation.
- Save and load trained models; keep training code separate from inference.
- Display actual evaluation metrics only. Clearly handle unsupported inputs and uncertain predictions.

## Development sequence

Complete and test each phase before proceeding:

1. Project setup, folder structure, and dashboard.
2. Soil Intelligence.
3. Crop Recommendation model.
4. Climate Intelligence API.
5. Smart Water Management.
6. Crop Disease Detection.
7. Farm Risk Intelligence Engine.
8. What-if Simulator.
9. Gemini AI Farming Assistant.
10. Database integration, testing, and deployment.

Update the README as development progresses and maintain a development progress checklist. Ask for approval before major architecture changes.

## Completion criteria

The project is complete when the Streamlit app runs and required pages are accessible; soil inputs are validated; crop and disease results come from genuine trained models; weather comes from the real API; irrigation uses available crop, soil, and weather data; the risk engine explains how available module outputs affect its assessments; the simulator compares scenarios; the assistant works when configured; reports and history can be stored; and missing data or service failures are handled clearly.

## Product principle

**AgroMind AI — Predict the Risk. Protect the Crop. Optimize Every Resource.**