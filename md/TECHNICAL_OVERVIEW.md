# Application Technical Overview

This document provides a step-by-step technical summary of the application, suitable for a technical manager. It highlights the main components, their purposes, and the key techniques or technologies used, without going into deep implementation details.

---


## 1. Application Entry Point
- **File:** app.py
- **Purpose:** Main application entry point, runs the FastAPI web server.
- **How it works:**
  - Imports and configures FastAPI, CORS, static file serving, and environment variables.
  - Loads API keys and config from .env.
  - Sets up routes for patient, clinician, and organization workflows.
  - Integrates with modules for database, ML, PDF generation, and voice prompts.
  - Handles file uploads, WebSocket connections, and API endpoints.
  - Uses async programming for efficient request handling.


## 2. Data Handling & Storage
- **File:** database.py
- **Purpose:** Handles all database operations using SQLite.
- **How it works:**
  - Connects to a local SQLite database (patients.db).
  - Defines functions to initialize the schema, add, update, and fetch patient records.
  - Uses SQL queries for CRUD operations.
  - Returns results as dictionaries for easy integration with the rest of the app.


## 3. Machine Learning Engine
- **File:** ml_engine.py
- **Purpose:** Machine learning logic for risk prediction.
- **How it works:**
  - Loads training data from CSV.
  - Encodes categorical variables using scikit-learn’s LabelEncoder.
  - Trains a RandomForestClassifier to predict cardiac risk.
  - Provides functions to encode new patient data and make predictions.
  - Returns risk scores and feature importances for use in reports and dashboards.


## 4. Biomarker Processing
- **File:** biomarkers.py
- **Purpose:** Defines biomarker reference ranges and logic for interpretation.
- **How it works:**
  - Stores reference ranges and interpretation logic for each biomarker (e.g., blood pressure, cholesterol).
  - Provides sex-specific thresholds and color coding for risk zones.
  - Used to generate personalized advice and highlight gaps in care.
  - May use regex or parsing for extracting and matching biomarker values.


## 5. PDF Report Generation
- **File:** generate_lab_report_pdf.py, pdf_report.py
- **Purpose:** Generates PDF reports for patients.
- **How it works:**
  - Uses the FPDF library to create formatted PDF documents.
  - Adds patient details, risk scores, and voice report summaries.
  - Customizes headers, footers, and section formatting.
  - Returns the PDF as bytes for download or email.


## 6. Voice & Symptom Reports
- **File:** voice_prompts.py, recordings/
- **Purpose:** Builds prompts and logic for AI-driven symptom screening calls.
- **How it works:**
  - Defines symptom categories and screening questions.
  - Generates dynamic prompts based on patient data and risk.
  - Integrates with Twilio for voice call automation.
  - May use NLP or regex to extract and summarize symptoms from call transcripts.


## 7. Static Web Frontend
- **Folder:** static/
- **Purpose:** Provides the user interface for patients, clinicians, and organizations.
- **How it works:**
  - HTML files define the structure for each user role.
  - JavaScript files handle form submissions, API calls, and dynamic rendering (e.g., charts, patient lists).
  - CSS styles the UI for a modern, accessible look.
  - Uses fetch/AJAX for real-time updates and PDF downloads.


## 8. Requirements
- **File:** requirements.txt
- **Purpose:** Lists Python dependencies.
- **How it works:**
  - Ensures all necessary packages are installed for the app to run.

---


## General Notes
- The application integrates multiple modules for data processing, ML, reporting, and web UI.
- Uses standard Python libraries and web technologies.
- Data extraction and processing may use regex or parsing techniques where needed.


If you want even more detail on any specific file or workflow, let me know!
*This document is a high-level technical summary. For deeper details, refer to the code or specific module documentation.*
