# Patient Flow

This document explains what happens in the patient assessment flow from the frontend to the backend.

## 1. Entry Point

The patient assessment UI is implemented in the React frontend.

Main screen:
- `frontend/src/routes/assessment.tsx`

This page allows the user to:
- upload a lab report PDF
- review or edit extracted patient fields
- submit the full assessment for risk analysis
- trigger a voice screening call
- download a final PDF report

## 2. Initial Form State

When the page loads, the frontend creates a form object with default values for:
- patient details: name, age, sex, life stage, phone
- primary cardiac inputs: blood pressure, cholesterol, max heart rate, oldpeak
- categorical inputs: chest pain type, fasting blood sugar, ECG, angina, slope, vessels, thalassemia
- extended biomarkers: HDL, LDL, triglycerides, HbA1c, hs-CRP, BMI, SpO2, smoking status, family history

This means the page can work in two modes:
- manual entry
- report-assisted entry

## 3. Lab Report Upload Flow

When the user uploads a PDF, the frontend calls:
- `api.uploadReport(file)`

That sends a `POST` request to:
- `/api/upload-report`

Backend steps:
1. FastAPI reads the uploaded PDF bytes.
2. `_extract_text_from_pdf_bytes()` extracts raw text from the PDF using PyMuPDF.
3. `_extract_report_values()` attempts structured extraction.

Extraction strategy:
1. AI-first:
   - If `OPENAI_API_KEY` is configured, the backend sends the extracted text to OpenAI with a strict JSON prompt.
   - The prompt asks for demographics, vitals, categorical values, and extended biomarkers.
2. Heuristic fallback:
   - `_heuristic_report_extract()` uses regex and text matching if AI is unavailable or misses fields.
3. Merge:
   - If AI returns partial output, heuristic extraction fills in any `null` fields.

Returned payload:
- `values`: extracted fields
- `raw_text_snippet`: beginning of the extracted text
- `confidence_note`: reminder to review the values

Frontend behavior after upload:
1. The returned `values` are merged into the current form.
2. Any non-empty extracted field overwrites the current value.
3. The user can still manually correct anything before submitting.

## 4. Which Fields Are Extracted

The upload flow currently tries to extract these patient fields:

Demographics:
- `name`
- `age`
- `sex`
- `life_stage`
- `phone`

Primary analysis inputs:
- `resting_blood_pressure`
- `cholestoral`
- `oldpeak`
- `Max_heart_rate`
- `chest_pain_type`
- `fasting_blood_sugar`
- `rest_ecg`
- `exercise_induced_angina`
- `slope`
- `vessels_colored_by_flourosopy`
- `thalassemia`

Extended biomarkers and history:
- `hdl`
- `ldl`
- `triglycerides`
- `hba1c`
- `hs_crp`
- `serum_creatinine`
- `tsh`
- `bmi`
- `waist_circumference`
- `spo2`
- `resting_pulse_rate`
- `smoking_status`
- `family_history`
- `current_medications`

## 5. Risk Calculation Flow

When the user submits the assessment form, the frontend calls:
- `api.calculateRisk(form)`

That sends a `POST` request to:
- `/api/risk/calculate`

Backend steps:
1. FastAPI validates the payload against `HeartAssessmentRequest`.
2. `_build_analysis_payload()` is called.
3. `predict_risk()` in `ml_engine.py` runs the ML model.
4. `analyze_reference_ranges()` checks biomarkers against reference thresholds.
5. `get_distribution_data()` prepares healthy vs disease comparison data.
6. For female patients, `get_women_advisory()` adds sex-specific guidance.

Returned result includes:
- `risk_score`
- `risk_level`
- `risk_color`
- `feature_importance`
- `reference_ranges`
- `distribution_data`
- `women_advisory`
- `gap_count`
- `total_biomarkers`

Frontend behavior after analysis:
- the result is displayed in the assessment page
- the user can then move to voice screening or PDF generation

## 6. Clinician Patient-Specific Upload Flow

There is also a clinician-specific upload route:
- `/api/clinician/patients/{patient_id}/upload-report`

This flow does everything the generic upload route does, and then also updates the patient record in the database.

Fields saved to the database include:
- demographics: name, age, sex, life stage, phone
- biomarker values
- categorical assessment values
- history and medication fields

So in clinician mode, upload does not just extract values for display. It also persists them.

## 7. Voice Screening Flow

After risk analysis, the frontend can trigger a voice screening call.

Frontend call:
- `api.voiceCall(...)`

Backend route:
- `/api/voice/call`

Payload sent from frontend includes:
- phone
- patient name
- patient age
- patient sex
- life stage
- risk score
- gap summary

Backend behavior:
- if Twilio and OpenAI are configured, the app can initiate a real call flow
- if not, the app can return a mock symptom report flow for development

Voice report retrieval:
- frontend later calls `/api/voice/report/{call_sid}`

Voice processing path:
1. call recording is fetched
2. audio is transcribed
3. transcript is converted into structured symptom JSON
4. red flags and recommendation are generated
5. report is written into `recordings/`

## 8. PDF Report Generation Flow

When the user downloads the report, the frontend sends:
- `patient`: current form values
- `risk_result`: ML analysis result
- `voice_report`: optional voice screening result

Backend route:
- `/api/report/generate`

Backend behavior:
1. `generate_pdf()` builds a final PDF report.
2. The PDF includes the patient context, risk interpretation, and any voice findings.
3. The frontend receives the PDF blob and downloads it in the browser.

## 9. Data Persistence

Patient persistence is handled through SQLite in `backend/database.py`.

Patient records may contain:
- profile details
- uploaded/extracted biomarker values
- analysis output
- symptom report JSON
- risk status and gap counts

The main persistence points are:
- patient creation
- clinician report upload
- clinician analysis submission

## 10. Current End-to-End Summary

The current patient flow is:
1. User opens the React assessment page.
2. User uploads a lab report or enters values manually.
3. Backend extracts structured fields from the report using AI plus regex fallback.
4. Frontend merges extracted values into the form.
5. User reviews and edits the form.
6. User submits the form for ML risk analysis.
7. Backend returns risk score, biomarker gap analysis, and advisory content.
8. User can optionally start a voice screening call.
9. User can download a final PDF report.

## 11. Important Notes

- Upload extraction is not fully deterministic because AI extraction may vary slightly when enabled.
- Regex fallback is important for structured reports and for environments without OpenAI configured.
- The frontend always allows manual correction after extraction.
- The clinician-specific upload flow persists extracted data, while the generic patient upload flow primarily returns extracted values to the frontend.
- The risk model depends on the required structured fields being present in expected formats.

## 12. Main Files Involved

Frontend:
- `frontend/src/routes/assessment.tsx`
- `frontend/src/lib/api.ts`

Backend:
- `backend/app.py`
- `backend/ml_engine.py`
- `backend/biomarkers.py`
- `backend/database.py`
- `backend/pdf_report.py`
- `backend/voice_prompts.py`
