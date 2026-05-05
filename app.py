# from __future__ import annotations

# import asyncio
# import base64
# import csv
# import json
# import os
# import random
# import re
# import ssl
# import tempfile
# import uuid
# from pathlib import Path
# from typing import Any

# import aiohttp
# import certifi
# import fitz
# import websockets
# from dotenv import load_dotenv
# from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, WebSocket
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import HTMLResponse, JSONResponse, Response
# from fastapi.websockets import WebSocketDisconnect
# from openai import OpenAI
# from pydantic import BaseModel
# from twilio.rest import Client
# from twilio.twiml.voice_response import Connect, VoiceResponse

# from biomarkers import analyze_reference_ranges, get_women_advisory
# from database import add_patient, get_patient, get_patients, init_db, update_patient
# from ml_engine import DF, ENCODERS, FEATURE_COLS, MODEL, get_distribution_data, predict_risk
# from pdf_report import generate_pdf
# from voice_prompts import build_screening_prompt

# BASE_DIR = Path(__file__).resolve().parent
# RECORDINGS_DIR = BASE_DIR / "recordings"
# RECORDINGS_DIR.mkdir(exist_ok=True)

# load_dotenv(BASE_DIR / ".env")

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o-mini")
# TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
# TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
# NGROK_URL = os.getenv("NGROK_URL", "")

# SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
# OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
# TWILIO_CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else None
# CALL_CONTEXTS: dict[str, dict[str, Any]] = {}

# app = FastAPI(title="HeartLens MVP")
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# init_db()


# class HeartAssessmentRequest(BaseModel):
#     name: str
#     age: int
#     sex: str
#     life_stage: str = "not_applicable"
#     phone: str | None = None
#     resting_blood_pressure: float
#     cholestoral: float
#     oldpeak: float
#     Max_heart_rate: float
#     chest_pain_type: str
#     fasting_blood_sugar: str
#     rest_ecg: str
#     exercise_induced_angina: str
#     slope: str
#     vessels_colored_by_flourosopy: str
#     thalassemia: str
#     # Extended fields from lab report
#     hdl: float | None = None
#     ldl: float | None = None
#     triglycerides: float | None = None
#     hba1c: float | None = None
#     hs_crp: float | None = None
#     serum_creatinine: float | None = None
#     tsh: float | None = None
#     bmi: float | None = None
#     waist_circumference: float | None = None
#     spo2: float | None = None
#     resting_pulse_rate: float | None = None
#     smoking_status: str | None = None
#     family_history: str | None = None
#     current_medications: str | None = None


# class PatientCreateRequest(BaseModel):
#     name: str
#     age: int | None = None
#     sex: str | None = None
#     life_stage: str | None = None
#     phone: str | None = None


# class VoiceCallRequest(BaseModel):
#     phone: str
#     patient_name: str
#     patient_age: int
#     patient_sex: str
#     life_stage: str = "not_applicable"
#     risk_score: float = 0.0
#     gap_summary: str = ""
#     patient_id: int | None = None


# class ReportRequest(BaseModel):
#     patient: dict[str, Any]
#     risk_result: dict[str, Any]
#     voice_report: dict[str, Any] | None = None


# def _build_analysis_payload(payload: dict[str, Any]) -> dict[str, Any]:
#     risk_result = predict_risk(payload, MODEL, ENCODERS, FEATURE_COLS)
#     reference_ranges = analyze_reference_ranges(payload, int(payload["age"]))
#     women_advisory = []
#     if payload["sex"] == "Female":
#         women_advisory = get_women_advisory(int(payload["age"]), float(payload["Max_heart_rate"]))
#     return {
#         **risk_result,
#         "reference_ranges": reference_ranges,
#         "distribution_data": get_distribution_data(DF, payload["sex"]),
#         "women_advisory": women_advisory,
#         "gap_count": sum(1 for item in reference_ranges if item.get("gap")),
#         "total_biomarkers": len(reference_ranges),
#     }


# def _extract_text_from_pdf_bytes(data: bytes) -> str:
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
#         temp_file.write(data)
#         temp_path = temp_file.name
#     try:
#         document = fitz.open(temp_path)
#         text = "\n".join(page.get_text() for page in document)
#         document.close()
#     finally:
#         Path(temp_path).unlink(missing_ok=True)
#     return text


# async def _call_openai_json(prompt: str) -> dict[str, Any] | None:
#     if OPENAI_CLIENT is None:
#         return None

#     def _sync_call() -> dict[str, Any] | None:
#         response = OPENAI_CLIENT.chat.completions.create(
#             model=OPENAI_TEXT_MODEL,
#             messages=[
#                 {"role": "system", "content": "Return valid JSON only."},
#                 {"role": "user", "content": prompt},
#             ],
#             response_format={"type": "json_object"},
#         )
#         content = response.choices[0].message.content or "{}"
#         return json.loads(content)

#     try:
#         return await asyncio.to_thread(_sync_call)
#     except Exception:
#         return None


# def _heuristic_report_extract(text: str) -> dict[str, Any]:
#     values: dict[str, Any] = {
#         "name": None,
#         "age": None,
#         "sex": None,
#         "life_stage": "not_applicable",
#         "phone": None,
#         "resting_blood_pressure": None,
#         "cholestoral": None,
#         "oldpeak": None,
#         "Max_heart_rate": None,
#         "chest_pain_type": None,
#         "fasting_blood_sugar": None,
#         "rest_ecg": None,
#         "exercise_induced_angina": None,
#         "slope": None,
#         "vessels_colored_by_flourosopy": None,
#         "thalassemia": None,
#         "hdl": None,
#         "ldl": None,
#         "triglycerides": None,
#         "hba1c": None,
#         "hs_crp": None,
#         "serum_creatinine": None,
#         "tsh": None,
#         "bmi": None,
#         "waist_circumference": None,
#         "spo2": None,
#         "resting_pulse_rate": None,
#         "smoking_status": None,
#         "family_history": None,
#         "current_medications": None,
#     }
#     lower_text = text.lower()
#     original_text = text  # keep original case for name extraction

#     # --- Demographics ---
#     name_match = re.search(r"patient\s*name\s*[:.]\s*([A-Za-z .\-]+)", original_text, re.IGNORECASE)
#     if name_match:
#         values["name"] = name_match.group(1).strip().rstrip(".")

#     age_match = re.search(r"(?:age\s*/?\s*sex|age)[^\d]{0,10}(\d{1,3})\s*(?:years|yrs|y)", lower_text)
#     if age_match:
#         values["age"] = int(age_match.group(1))

#     sex_match = re.search(r"(?:age\s*/?\s*sex|sex)[^a-z]{0,10}(male|female)", lower_text)
#     if sex_match:
#         values["sex"] = sex_match.group(1).capitalize()

#     phone_match = re.search(r"(?:contact|phone|mobile|tel)[^\d]{0,10}([\d\+\-\s]{7,15})", lower_text)
#     if phone_match:
#         values["phone"] = phone_match.group(1).strip()

#     # Life stage
#     if "postmenopaus" in lower_text:
#         values["life_stage"] = "postmenopause"
#     elif "perimenopaus" in lower_text:
#         values["life_stage"] = "perimenopause"
#     elif "pregnan" in lower_text:
#         values["life_stage"] = "pregnancy"

#     # --- Numeric vitals ---
#     numeric_patterns: dict[str, list[str]] = {
#         "resting_blood_pressure": [
#             r"(?:resting\s+)?blood\s*pressure[^\d]{0,20}(\d{2,3})",
#             r"\b(1[0-2]\d|[89]\d)\s*mmhg\b",
#         ],
#         "cholestoral": [
#             r"total\s+chol(?:esterol)?[^\d]{0,20}(\d{2,3})",
#             r"chol(?:esterol)?[^\d]{0,20}(\d{2,3})",
#         ],
#         "oldpeak": [
#             r"(?:oldpeak|st\s*depression)[^\d]{0,20}(\d+(?:\.\d+)?)",
#         ],
#         "Max_heart_rate": [
#             r"(?:max(?:imum)?\s*heart\s*rate\s*(?:achieved)?|max\s*hr)[^\d]{0,20}(\d{2,3})",
#             r"heart\s*rate\s*achieved[^\d]{0,20}(\d{2,3})",
#         ],
#         "hdl": [r"hdl\s*(?:cholesterol)?[^\d]{0,20}(\d+(?:\.\d+)?)"],
#         "ldl": [r"ldl\s*(?:cholesterol)?[^\d]{0,20}(\d+(?:\.\d+)?)"],
#         "triglycerides": [r"triglycerid\w*[^\d]{0,20}(\d+(?:\.\d+)?)"],
#         "hba1c": [r"hba1c[^\d]{0,20}(\d+(?:\.\d+)?)", r"\ba1c[^\d]{0,20}(\d+(?:\.\d+)?)"],
#         "hs_crp": [r"hs[\-\s]?crp[^\d]{0,20}(\d+(?:\.\d+)?)", r"c[\-\s]?reactive[^\d]{0,20}(\d+(?:\.\d+)?)"],
#         "serum_creatinine": [r"(?:serum\s+)?creatinine[^\d]{0,20}(\d+(?:\.\d+)?)"],
#         "tsh": [r"\btsh[^\d]{0,20}(\d+(?:\.\d+)?)"],
#         "bmi": [r"(?:bmi|body\s*mass\s*index)[^\d]{0,20}(\d+(?:\.\d+)?)"],
#         "waist_circumference": [r"waist\s*(?:circumference)?[^\d]{0,20}(\d+(?:\.\d+)?)"],
#         "spo2": [r"spo2[^\d]{0,20}(\d+(?:\.\d+)?)", r"pulse\s*ox[^\d]{0,20}(\d+(?:\.\d+)?)"],
#         "resting_pulse_rate": [r"(?:resting\s+)?pulse\s*(?:rate)?[^\d]{0,20}(\d{2,3})"],
#     }
#     for key, regexes in numeric_patterns.items():
#         for pattern in regexes:
#             match = re.search(pattern, lower_text)
#             if match:
#                 val_str = match.group(1)
#                 values[key] = float(val_str) if "." in val_str else int(val_str)
#                 break

#     # --- Categorical fields ---
#     # Chest pain type
#     cpt_match = re.search(r"chest\s*pain\s*(?:type)?[^a-z]{0,15}(typical\s*angina|atypical\s*angina|non[\-\s]?anginal\s*pain|asymptomatic)", lower_text)
#     if cpt_match:
#         raw = cpt_match.group(1).strip()
#         cpt_map = {"typical angina": "Typical angina", "atypical angina": "Atypical angina",
#                    "non-anginal pain": "Non-anginal pain", "non anginal pain": "Non-anginal pain",
#                    "nonanginal pain": "Non-anginal pain", "asymptomatic": "Asymptomatic"}
#         values["chest_pain_type"] = cpt_map.get(raw.lower().replace("  ", " "), raw.title())

#     # Fasting blood sugar
#     fbs_match = re.search(r"fasting\s*(?:blood)?\s*sugar[^\d]{0,20}[<>]?\s*(\d+)", lower_text)
#     if fbs_match:
#         fbs_val = int(fbs_match.group(1))
#         values["fasting_blood_sugar"] = "Greater than 120 mg/ml" if fbs_val > 120 else "Lower than 120 mg/ml"
#     elif re.search(r"fasting\s*(?:blood)?\s*sugar[^\d]{0,30}normal", lower_text):
#         values["fasting_blood_sugar"] = "Lower than 120 mg/ml"

#     # Rest ECG
#     ecg_match = re.search(r"(?:resting\s+)?(?:ecg|electrocardiogram)[^a-z]{0,30}(normal|st[\-\s]?t\s*wave|left\s*ventricular)", lower_text)
#     if ecg_match:
#         raw_ecg = ecg_match.group(1).strip()
#         if "normal" in raw_ecg:
#             values["rest_ecg"] = "Normal"
#         elif "st" in raw_ecg:
#             values["rest_ecg"] = "ST-T wave abnormality"
#         elif "left" in raw_ecg:
#             values["rest_ecg"] = "Left ventricular hypertrophy"
#     elif re.search(r"(?:rest\s+ecg|resting.*ecg)[^a-z]{0,20}normal", lower_text):
#         values["rest_ecg"] = "Normal"
#     elif "normal sinus rhythm" in lower_text and "no acute st" in lower_text:
#         values["rest_ecg"] = "Normal"

#     # Exercise-induced angina
#     eia_match = re.search(r"exercise\s*induced\s*angina[^a-z]{0,15}(yes|no)", lower_text)
#     if eia_match:
#         values["exercise_induced_angina"] = eia_match.group(1).capitalize()
#     elif re.search(r"exercise\s*induced\s*angina.*\bno\b", lower_text):
#         values["exercise_induced_angina"] = "No"

#     # Slope
#     slope_match = re.search(r"(?:st\s*(?:segment\s*)?slope|slope)[^a-z]{0,15}(upsloping|flat|downsloping)", lower_text)
#     if slope_match:
#         values["slope"] = slope_match.group(1).capitalize()

#     # Vessels coloured by fluoroscopy
#     vessels_match = re.search(r"(?:vessels?\s*(?:colou?red|calcification)|coronary\s*fluoroscopy)[^a-z]{0,30}(zero|one|two|three|four|0|1|2|3|4|no\s*vessel)", lower_text)
#     if vessels_match:
#         raw_v = vessels_match.group(1).strip()
#         v_map = {"0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four",
#                  "zero": "Zero", "one": "One", "two": "Two", "three": "Three", "four": "Four"}
#         if raw_v.startswith("no"):
#             values["vessels_colored_by_flourosopy"] = "Zero"
#         else:
#             values["vessels_colored_by_flourosopy"] = v_map.get(raw_v, "Zero")

#     # Thalassemia / Thallium
#     thal_match = re.search(r"(?:thalass[ae]mia|thallium\s*(?:scan)?\s*(?:pattern)?)[^a-z]{0,20}(normal|fixed\s*(?:defect)?|reversabl?e\s*(?:defect)?)", lower_text)
#     if thal_match:
#         raw_t = thal_match.group(1).strip()
#         if "fixed" in raw_t:
#             values["thalassemia"] = "Fixed Defect"
#         elif "reversa" in raw_t:
#             values["thalassemia"] = "Reversable Defect"
#         else:
#             values["thalassemia"] = "Normal"

#     # Smoking status
#     if "non-smoker" in lower_text or "non smoker" in lower_text:
#         values["smoking_status"] = "Non-smoker"
#     elif "former smoker" in lower_text or "ex-smoker" in lower_text:
#         values["smoking_status"] = "Former smoker"
#     elif "current smoker" in lower_text or "smoker" in lower_text:
#         values["smoking_status"] = "Current smoker"

#     # Family history
#     fh_match = re.search(r"family\s*history[^.\n]{0,80}(father|mother|sibling|parent|brother|sister)[^.\n]{0,80}", lower_text)
#     if fh_match:
#         # Grab full sentence
#         fh_full = re.search(r"family\s*history[^.\n]{0,120}", original_text, re.IGNORECASE)
#         values["family_history"] = fh_full.group(0).strip() if fh_full else "Yes"
#     elif re.search(r"family\s*history.*\bno\b|no.*family\s*history", lower_text):
#         values["family_history"] = "No"

#     # Current medications
#     med_match = re.search(r"(?:current\s*)?medications?[^a-z]{0,10}([^\n]{5,120})", original_text, re.IGNORECASE)
#     if med_match:
#         values["current_medications"] = med_match.group(1).strip()

#     return values


# async def _extract_report_values(text: str) -> dict[str, Any]:
#     prompt = f"""
#     Extract patient demographics AND cardiac biomarker values from the report text below.
#     Return JSON with these exact keys (use null when not found):

#     Demographics:
#     - name: patient full name
#     - age: integer age in years
#     - sex: "Male" or "Female"
#     - life_stage: one of "not_applicable", "perimenopause", "postmenopause", "pregnancy" (look for keywords like postmenopausal)
#     - phone: contact/mobile number as string

#     Vitals & primary biomarkers:
#     - resting_blood_pressure: systolic BP in mmHg (number)
#     - cholestoral: total cholesterol in mg/dL (number)
#     - oldpeak: ST depression value in mm (number)
#     - Max_heart_rate: maximum heart rate achieved in bpm (number)

#     Categorical fields (use EXACT values listed):
#     - chest_pain_type: one of "Typical angina", "Atypical angina", "Non-anginal pain", "Asymptomatic"
#     - fasting_blood_sugar: "Greater than 120 mg/ml" or "Lower than 120 mg/ml"
#     - rest_ecg: one of "Normal", "ST-T wave abnormality", "Left ventricular hypertrophy"
#     - exercise_induced_angina: "Yes" or "No"
#     - slope: one of "Upsloping", "Flat", "Downsloping"
#     - vessels_colored_by_flourosopy: one of "Zero", "One", "Two", "Three", "Four" (check coronary fluoroscopy)
#     - thalassemia: one of "Normal", "Fixed Defect", "Reversable Defect" (check thallium scan pattern)

#     Extended biomarkers (numbers, null if missing):
#     hdl, ldl, triglycerides, hba1c, hs_crp, serum_creatinine, tsh,
#     bmi, waist_circumference, spo2, resting_pulse_rate

#     Lifestyle (strings, null if missing):
#     smoking_status, family_history, current_medications

#     Report text:
#     {text[:6000]}
#     """
#     extracted = await _call_openai_json(prompt)
#     if extracted:
#         # Merge with heuristic as fallback for any nulls
#         heuristic = _heuristic_report_extract(text)
#         for key, val in heuristic.items():
#             if val is not None and extracted.get(key) is None:
#                 extracted[key] = val
#         return extracted
#     return _heuristic_report_extract(text)


# def _mock_voice_report(call_sid: str, payload: VoiceCallRequest) -> dict[str, Any]:
#     report = {
#         "call_sid": call_sid,
#         "status": "completed",
#         "transcript": (
#             f"Mock screening call for {payload.patient_name}. Patient reported exertional fatigue, "
#             "intermittent jaw discomfort, and occasional night-time breathlessness."
#         ),
#         "symptom_report": {
#             "atypical_pain": {"present": True, "details": "Intermittent jaw discomfort", "severity": "moderate"},
#             "respiratory": {"present": True, "details": "Occasional night-time breathlessness", "severity": "moderate"},
#             "gastrointestinal": {"present": False, "details": None, "severity": None},
#             "neurological": {"present": False, "details": None, "severity": None},
#             "fatigue": {"present": True, "details": "Lower exercise tolerance", "severity": "high"},
#             "autonomic": {"present": False, "details": None, "severity": None},
#             "fluid_circulation": {"present": False, "details": None, "severity": None},
#             "pre_event_warning": {"present": True, "details": "Symptoms worsening over two weeks", "severity": "moderate"},
#             "sleep_related": {"present": True, "details": "Night-time breathlessness", "severity": "moderate"},
#             "emotional": {"present": False, "details": None, "severity": None},
#             "hormonal": {"present": payload.life_stage in {"perimenopause", "postmenopause"}, "details": payload.life_stage, "severity": "mild" if payload.life_stage else None},
#             "exertion_related": {"present": True, "details": "Fatigue increases with mild exertion", "severity": "high"},
#         },
#         "red_flags": ["Reduced exercise tolerance", "Jaw discomfort", "Night-time breathlessness"],
#         "recommendation": "Atypical cardiac symptoms were reported. Recommend ECG, troponin testing, and clinician review.",
#     }
#     output_path = RECORDINGS_DIR / f"{call_sid}_symptom_report.json"
#     output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
#     return report


# async def _generate_structured_symptom_report(call_sid: str, transcript_text: str) -> dict[str, Any]:
#     prompt = f"""
#     Convert the following cardiac screening transcript into JSON.
#     Return keys: atypical_pain, respiratory, gastrointestinal, neurological, fatigue,
#     autonomic, fluid_circulation, pre_event_warning, sleep_related, emotional,
#     hormonal, exertion_related, red_flags, recommendation.
#     Each symptom key must contain: present, details, severity.

#     Transcript:
#     {transcript_text[:8000]}
#     """
#     extracted = await _call_openai_json(prompt)
#     if not extracted:
#         extracted = {
#             "atypical_pain": {"present": False, "details": None, "severity": None},
#             "respiratory": {"present": False, "details": None, "severity": None},
#             "gastrointestinal": {"present": False, "details": None, "severity": None},
#             "neurological": {"present": False, "details": None, "severity": None},
#             "fatigue": {"present": False, "details": None, "severity": None},
#             "autonomic": {"present": False, "details": None, "severity": None},
#             "fluid_circulation": {"present": False, "details": None, "severity": None},
#             "pre_event_warning": {"present": False, "details": None, "severity": None},
#             "sleep_related": {"present": False, "details": None, "severity": None},
#             "emotional": {"present": False, "details": None, "severity": None},
#             "hormonal": {"present": False, "details": None, "severity": None},
#             "exertion_related": {"present": False, "details": None, "severity": None},
#             "red_flags": [],
#             "recommendation": "Manual clinical review recommended.",
#         }
#     report = {
#         "call_sid": call_sid,
#         "status": "completed",
#         "transcript": transcript_text,
#         "symptom_report": {key: extracted[key] for key in [
#             "atypical_pain", "respiratory", "gastrointestinal", "neurological", "fatigue",
#             "autonomic", "fluid_circulation", "pre_event_warning", "sleep_related",
#             "emotional", "hormonal", "exertion_related",
#         ] if key in extracted},
#         "red_flags": extracted.get("red_flags", []),
#         "recommendation": extracted.get("recommendation", "Clinical follow-up recommended."),
#     }
#     output_path = RECORDINGS_DIR / f"{call_sid}_symptom_report.json"
#     output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
#     return report


# async def process_recording_after_call(call_sid: str) -> dict[str, Any] | None:
#     if not call_sid or TWILIO_CLIENT is None or OPENAI_CLIENT is None:
#         return None
#     try:
#         recordings = await asyncio.to_thread(TWILIO_CLIENT.recordings.list, call_sid=call_sid)
#         if not recordings:
#             return None
#         recording = recordings[0]
#         recording_url = f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"
#         filename = RECORDINGS_DIR / f"{call_sid}.mp3"
#         async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)) as session:
#             async with session.get(recording_url, ssl=SSL_CONTEXT) as response:
#                 if response.status != 200:
#                     return None
#                 filename.write_bytes(await response.read())
#         with filename.open("rb") as audio_file:
#             transcript = await asyncio.to_thread(
#                 OPENAI_CLIENT.audio.transcriptions.create,
#                 model="whisper-1",
#                 file=audio_file,
#             )
#         transcript_text = transcript.text
#         (RECORDINGS_DIR / f"{call_sid}.txt").write_text(transcript_text, encoding="utf-8")
#         return await _generate_structured_symptom_report(call_sid, transcript_text)
#     except Exception:
#         return None


# def _gap_summary(reference_ranges: list[dict[str, Any]]) -> str:
#     flagged = [item["metric"] for item in reference_ranges if item.get("gap")]
#     if not flagged:
#         return "No diagnostic gap was flagged in the range comparison."
#     return f"Diagnostic gaps were flagged for: {', '.join(flagged)}."


# @app.post("/api/risk/calculate")
# async def calculate_risk(payload: HeartAssessmentRequest) -> dict[str, Any]:
#     return _build_analysis_payload(payload.model_dump())


# @app.post("/api/upload-report")
# @app.post("/api/patient/upload-report")
# async def upload_report(report: UploadFile = File(...)) -> dict[str, Any]:
#     report_bytes = await report.read()
#     text = _extract_text_from_pdf_bytes(report_bytes)
#     values = await _extract_report_values(text)
#     return {
#         "extracted": True,
#         "values": values,
#         "raw_text_snippet": text[:500],
#         "confidence_note": "Review extracted values before analysis. Fields not found were left blank.",
#     }


# @app.get("/api/clinician/patients")
# async def clinician_patients() -> dict[str, Any]:
#     return {"patients": get_patients()}


# @app.post("/api/clinician/patients")
# async def clinician_add_patient(payload: PatientCreateRequest) -> dict[str, Any]:
#     patient_id = add_patient(payload.model_dump())
#     patient = get_patient(patient_id)
#     return {"patient": patient}


# @app.get("/api/clinician/patients/{patient_id}")
# async def clinician_get_patient(patient_id: int) -> dict[str, Any]:
#     patient = get_patient(patient_id)
#     if patient is None:
#         raise HTTPException(status_code=404, detail="Patient not found")
#     return {"patient": patient}


# @app.post("/api/clinician/patients/{patient_id}/upload-report")
# async def clinician_upload_report(patient_id: int, report: UploadFile = File(...)) -> dict[str, Any]:
#     patient = get_patient(patient_id)
#     if patient is None:
#         raise HTTPException(status_code=404, detail="Patient not found")
#     result = await upload_report(report)
#     values = result["values"]
#     db_update = {
#         "name": values.get("name"),
#         "age": values.get("age"),
#         "sex": values.get("sex"),
#         "life_stage": values.get("life_stage"),
#         "phone": values.get("phone"),
#         "resting_blood_pressure": values.get("resting_blood_pressure"),
#         "cholestoral": values.get("cholestoral"),
#         "oldpeak": values.get("oldpeak"),
#         "max_heart_rate": values.get("Max_heart_rate"),
#         "chest_pain_type": values.get("chest_pain_type"),
#         "fasting_blood_sugar": values.get("fasting_blood_sugar"),
#         "rest_ecg": values.get("rest_ecg"),
#         "exercise_induced_angina": values.get("exercise_induced_angina"),
#         "slope": values.get("slope"),
#         "vessels": values.get("vessels_colored_by_flourosopy"),
#         "thalassemia": values.get("thalassemia"),
#         "hdl": values.get("hdl"),
#         "ldl": values.get("ldl"),
#         "triglycerides": values.get("triglycerides"),
#         "hba1c": values.get("hba1c"),
#         "hs_crp": values.get("hs_crp"),
#         "serum_creatinine": values.get("serum_creatinine"),
#         "tsh": values.get("tsh"),
#         "bmi": values.get("bmi"),
#         "waist_circumference": values.get("waist_circumference"),
#         "spo2": values.get("spo2"),
#         "resting_pulse_rate": values.get("resting_pulse_rate"),
#         "smoking_status": values.get("smoking_status"),
#         "family_history": values.get("family_history"),
#         "current_medications": values.get("current_medications"),
#     }
#     update_patient(patient_id, {key: value for key, value in db_update.items() if value is not None})
#     return result


# @app.post("/api/clinician/patients/{patient_id}/analyze")
# async def clinician_analyze(patient_id: int, payload: HeartAssessmentRequest) -> dict[str, Any]:
#     patient = get_patient(patient_id)
#     if patient is None:
#         raise HTTPException(status_code=404, detail="Patient not found")
#     analysis = _build_analysis_payload(payload.model_dump())
#     update_patient(
#         patient_id,
#         {
#             "status": "flagged" if analysis["risk_score"] >= 60 else "assessed",
#             "resting_blood_pressure": payload.resting_blood_pressure,
#             "cholestoral": payload.cholestoral,
#             "oldpeak": payload.oldpeak,
#             "max_heart_rate": payload.Max_heart_rate,
#             "chest_pain_type": payload.chest_pain_type,
#             "fasting_blood_sugar": payload.fasting_blood_sugar,
#             "rest_ecg": payload.rest_ecg,
#             "exercise_induced_angina": payload.exercise_induced_angina,
#             "slope": payload.slope,
#             "vessels": payload.vessels_colored_by_flourosopy,
#             "thalassemia": payload.thalassemia,
#             "hdl": payload.hdl,
#             "ldl": payload.ldl,
#             "triglycerides": payload.triglycerides,
#             "hba1c": payload.hba1c,
#             "hs_crp": payload.hs_crp,
#             "serum_creatinine": payload.serum_creatinine,
#             "tsh": payload.tsh,
#             "bmi": payload.bmi,
#             "waist_circumference": payload.waist_circumference,
#             "spo2": payload.spo2,
#             "resting_pulse_rate": payload.resting_pulse_rate,
#             "smoking_status": payload.smoking_status,
#             "family_history": payload.family_history,
#             "current_medications": payload.current_medications,
#             "risk_score": analysis["risk_score"],
#             "risk_level": analysis["risk_level"],
#             "gap_count": analysis["gap_count"],
#             "analysis_json": analysis,
#         },
#     )
#     return analysis


# @app.post("/api/voice/call")
# async def start_voice_call(payload: VoiceCallRequest) -> dict[str, Any]:
#     call_sid = f"mock-{uuid.uuid4().hex[:10]}"
#     CALL_CONTEXTS[call_sid] = {**payload.model_dump(), "call_status": "in_progress"}

#     if TWILIO_CLIENT and TWILIO_PHONE_NUMBER and NGROK_URL:
#         try:
#             call = await asyncio.to_thread(
#                 TWILIO_CLIENT.calls.create,
#                 url=f"{NGROK_URL}/outgoing-call",
#                 to=payload.phone,
#                 from_=TWILIO_PHONE_NUMBER,
#                 record=True,
#             )
#             call_sid = call.sid
#             CALL_CONTEXTS[call_sid] = {**payload.model_dump(), "call_status": "in_progress"}
#             status = "in_progress"
#         except Exception:
#             status = "in_progress"
#             CALL_CONTEXTS[call_sid]["call_status"] = "in_progress"
#             # Schedule mock completion after a delay
#             asyncio.get_event_loop().call_later(
#                 6, lambda sid=call_sid, p=payload: _complete_mock_call(sid, p)
#             )
#     else:
#         status = "in_progress"
#         # Schedule mock completion after a delay (simulate call duration)
#         asyncio.get_event_loop().call_later(
#             6, lambda sid=call_sid, p=payload: _complete_mock_call(sid, p)
#         )

#     if payload.patient_id is not None:
#         update_patient(payload.patient_id, {"call_sid": call_sid, "call_status": "in_progress"})
#     return {"call_sid": call_sid, "status": status}


# def _complete_mock_call(call_sid: str, payload: VoiceCallRequest) -> None:
#     """Called after delay to simulate call completion."""
#     report = _mock_voice_report(call_sid, payload)
#     if call_sid in CALL_CONTEXTS:
#         CALL_CONTEXTS[call_sid]["call_status"] = "completed"
#     if payload.patient_id is not None:
#         update_patient(payload.patient_id, {"call_status": "completed", "symptom_report_json": report})


# @app.get("/api/voice/report/{call_sid}")
# async def get_voice_report(call_sid: str) -> dict[str, Any]:
#     report_path = RECORDINGS_DIR / f"{call_sid}_symptom_report.json"
#     if report_path.exists():
#         report = json.loads(report_path.read_text(encoding="utf-8"))
#         report["status"] = "completed"
#         return report
#     if call_sid in CALL_CONTEXTS:
#         return {"call_sid": call_sid, "status": CALL_CONTEXTS[call_sid].get("call_status", "in_progress")}
#     raise HTTPException(status_code=404, detail="Call not found")


# @app.post("/api/report/generate")
# async def report_generate(payload: ReportRequest) -> Response:
#     pdf_bytes = generate_pdf(payload.patient, payload.risk_result, payload.voice_report)
#     filename = f"HeartLens_{payload.patient.get('name', 'patient').replace(' ', '_')}.pdf"
#     headers = {"Content-Disposition": f"attachment; filename={filename}"}
#     return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


# class FinalReportRequest(BaseModel):
#     patient: dict[str, Any]
#     risk_result: dict[str, Any]
#     voice_report: dict[str, Any]


# @app.post("/api/voice/final-report")
# async def generate_final_report(payload: FinalReportRequest) -> dict[str, Any]:
#     """Combine risk analysis + voice transcript and send to LLM for comprehensive clinical report."""
#     vr = payload.voice_report
#     rr = payload.risk_result
#     pt = payload.patient

#     transcript = vr.get("transcript", "")
#     red_flags = vr.get("red_flags", [])
#     symptom_report = vr.get("symptom_report", {})

#     # Build symptom summary from structured report
#     symptom_lines = []
#     for cat, info in symptom_report.items():
#         if isinstance(info, dict) and info.get("present"):
#             det = info.get("details", cat.replace("_", " "))
#             sev = info.get("severity", "unknown")
#             symptom_lines.append(f"- {cat.replace('_', ' ').title()}: {det} (severity: {sev})")
#     symptom_summary = "\n".join(symptom_lines) if symptom_lines else "No atypical symptoms reported."

#     # Reference range gap summary
#     ref_ranges = rr.get("reference_ranges", [])
#     gap_lines = []
#     for r in ref_ranges:
#         if r.get("gap"):
#             gap_lines.append(f"- {r['metric']}: {r['value']} {r['unit']} — Male: {r['male_status']}, Female: {r['female_status']}. {r.get('gap_explanation', '')}")
#     gap_summary = "\n".join(gap_lines) if gap_lines else "No diagnostic gaps detected."

#     prompt = f"""You are a senior cardiologist AI assistant. Generate a comprehensive clinical assessment report.

# PATIENT:
#   Name: {pt.get('name', 'Unknown')}
#   Age: {pt.get('age', 'N/A')} | Sex: {pt.get('sex', 'N/A')} | Life stage: {pt.get('life_stage', 'N/A')}

# ML RISK ASSESSMENT:
#   Risk score: {rr.get('risk_score', 0)}% ({rr.get('risk_level', 'N/A')})
#   Diagnostic gaps: {rr.get('gap_count', 0)} / {rr.get('total_biomarkers', 0)}

# BIOMARKER GAPS:
# {gap_summary}

# VOICE SCREENING TRANSCRIPT:
# {transcript[:4000]}

# DETECTED ATYPICAL SYMPTOMS:
# {symptom_summary}

# RED FLAGS: {', '.join(red_flags) if red_flags else 'None'}

# WOMEN-SPECIFIC ADVISORIES: {', '.join(rr.get('women_advisory', [])) or 'None'}

# Generate a JSON response with these keys:
# - "clinical_summary": 3-4 sentence executive summary of findings
# - "risk_interpretation": Interpret the ML risk score in clinical context (2-3 sentences)
# - "symptom_analysis": Analysis of reported symptoms, especially atypical ones (2-4 sentences)
# - "gap_analysis": What the diagnostic gaps mean clinically (2-3 sentences)
# - "recommended_tests": Array of recommended follow-up tests/procedures
# - "recommended_actions": Array of recommended clinical actions
# - "urgency": "routine" | "soon" | "urgent" — how quickly follow-up is needed
# - "urgency_rationale": Why this urgency level (1-2 sentences)
# - "final_assessment": Comprehensive 4-6 sentence final clinical assessment tying everything together
# """

#     llm_result = await _call_openai_json(prompt)
#     if not llm_result:
#         # Fallback: generate a heuristic report
#         risk_score = rr.get("risk_score", 0)
#         urgency = "urgent" if risk_score >= 70 or len(red_flags) >= 3 else "soon" if risk_score >= 40 or len(red_flags) >= 1 else "routine"
#         llm_result = {
#             "clinical_summary": f"Patient {pt.get('name', '')} presents with a {rr.get('risk_level', 'moderate')} cardiac risk score of {risk_score:.0f}%. "
#                                 f"{len(red_flags)} red flag(s) were identified during voice screening. "
#                                 f"{rr.get('gap_count', 0)} diagnostic gap(s) were found across gender-specific biomarker ranges.",
#             "risk_interpretation": f"The ML model predicts a {risk_score:.0f}% cardiac risk, classified as {rr.get('risk_level', 'N/A')}. "
#                                    "This should be correlated with clinical presentation and symptom screening findings.",
#             "symptom_analysis": f"Voice screening identified: {', '.join(red_flags) if red_flags else 'no concerning symptoms'}. "
#                                 "Atypical presentations warrant clinical attention, especially in female patients.",
#             "gap_analysis": f"{rr.get('gap_count', 0)} biomarker(s) showed different classifications under male vs. female reference ranges, "
#                            "indicating potential under-detection with standard thresholds.",
#             "recommended_tests": ["12-lead ECG", "Troponin levels", "Lipid panel review", "Stress echocardiography"],
#             "recommended_actions": ["Schedule cardiology consultation", "Review current medications", "Lifestyle counseling"],
#             "urgency": urgency,
#             "urgency_rationale": f"Based on {risk_score:.0f}% risk score and {len(red_flags)} red flag(s).",
#             "final_assessment": f"Patient requires {urgency} follow-up given the combination of ML risk prediction, "
#                                 f"voice screening findings, and biomarker analysis.",
#         }

#     return {
#         "final_report": llm_result,
#         "generated_at": json.dumps({"timestamp": str(uuid.uuid4())}),
#     }


# @app.post("/api/org/upload-batch")
# async def org_upload_batch(file: UploadFile = File(...)) -> dict[str, Any]:
#     content = (await file.read()).decode("utf-8")
#     reader = csv.DictReader(content.splitlines())
#     results = []
#     for row in reader:
#         age = int(row.get("age") or random.randint(35, 75))
#         sex = row.get("sex") or random.choice(["Female", "Male"])
#         base = random.uniform(15, 75)
#         if sex == "Female" and age >= 50:
#             base += random.uniform(5, 15)
#         score = round(min(base, 95.0), 1)
#         risk_level = "Low Risk" if score < 30 else "Moderate Risk" if score < 60 else "High Risk"
#         flagged = score >= 40
#         results.append(
#             {
#                 "name": row.get("name", "Unknown"),
#                 "phone": row.get("phone", ""),
#                 "age": age,
#                 "sex": sex,
#                 "simulated_risk_score": score,
#                 "risk_level": risk_level,
#                 "flagged": flagged,
#                 "flag_reason": "High simulated risk score" if flagged else None,
#             }
#         )
#     await asyncio.sleep(1)
#     flagged_count = sum(1 for item in results if item["flagged"])
#     avg_score = round(sum(item["simulated_risk_score"] for item in results) / len(results), 1) if results else 0.0
#     return {"total": len(results), "processed": len(results), "flagged": flagged_count, "average_score": avg_score, "results": results}


# @app.api_route("/outgoing-call", methods=["GET", "POST"])
# async def outgoing_call(request: Request) -> HTMLResponse:
#     call_sid = ""
#     if request.method == "POST":
#         form = await request.form()
#         call_sid = str(form.get("CallSid") or "")
#     response = VoiceResponse()
#     response.pause(length=1)
#     connect = Connect()
#     stream_url = f"wss://{request.url.hostname}/media-stream"
#     if call_sid:
#         stream_url += f"?call_sid={call_sid}"
#     connect.stream(url=stream_url)
#     response.append(connect)
#     return HTMLResponse(content=str(response), media_type="application/xml")


# @app.websocket("/media-stream")
# async def media_stream(websocket: WebSocket) -> None:
#     await websocket.accept()
#     call_sid = websocket.query_params.get("call_sid", "")
#     context = CALL_CONTEXTS.get(call_sid, {})
#     if not OPENAI_CLIENT or not OPENAI_API_KEY:
#         await websocket.close()
#         return
#     prompt = build_screening_prompt(
#         patient_name=context.get("patient_name", "Patient"),
#         age=int(context.get("patient_age", 50)),
#         sex=context.get("patient_sex", "Female"),
#         life_stage=context.get("life_stage", "not_applicable"),
#         risk_score=float(context.get("risk_score", 0.0)),
#         gap_summary=context.get("gap_summary", ""),
#     )
#     stream_sid: str | None = None

#     async with websockets.connect(
#         "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2025-06-03",
#         ssl=SSL_CONTEXT,
#         additional_headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "OpenAI-Beta": "realtime=v1"},
#     ) as openai_ws:
#         await openai_ws.send(
#             json.dumps(
#                 {
#                     "type": "session.update",
#                     "session": {
#                         "turn_detection": {"type": "server_vad"},
#                         "input_audio_format": "g711_ulaw",
#                         "output_audio_format": "g711_ulaw",
#                         "voice": "alloy",
#                         "instructions": prompt,
#                         "modalities": ["audio", "text"],
#                         "temperature": 0.7,
#                     },
#                 }
#             )
#         )
#         # Trigger the AI to deliver its opening greeting
#         await openai_ws.send(json.dumps({"type": "response.create"}))

#         async def receive_from_twilio() -> None:
#             nonlocal stream_sid
#             try:
#                 async for message in websocket.iter_text():
#                     data = json.loads(message)
#                     if data.get("event") == "start":
#                         stream_sid = data["start"]["streamSid"]
#                     elif data.get("event") == "media":
#                         await openai_ws.send(json.dumps({"type": "input_audio_buffer.append", "audio": data["media"]["payload"]}))
#                     elif data.get("event") == "stop":
#                         report = await process_recording_after_call(call_sid)
#                         if report:
#                             patient_id = context.get("patient_id")
#                             if patient_id is not None:
#                                 update_patient(patient_id, {"call_status": "completed", "symptom_report_json": report})
#                         break
#             except WebSocketDisconnect:
#                 pass

#         async def send_to_twilio() -> None:
#             async for message in openai_ws:
#                 data = json.loads(message)
#                 if data.get("type") == "response.audio.delta" and data.get("delta"):
#                     # OpenAI delta is already base64-encoded G.711 µ-law; pass it through directly
#                     await websocket.send_json({"event": "media", "streamSid": stream_sid or call_sid, "media": {"payload": data["delta"]}})

#         await asyncio.gather(receive_from_twilio(), send_to_twilio())


# @app.get("/api/health")
# async def health() -> dict[str, Any]:
#     return {"status": "ok", "patients": len(get_patients())}


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "5050")))
from __future__ import annotations

import asyncio
import base64
import csv
import json
import os
import random
import re
import ssl
import tempfile
import uuid
from pathlib import Path
from typing import Any

import aiohttp
import certifi
import fitz
import websockets
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.websockets import WebSocketDisconnect
from openai import OpenAI
from pydantic import BaseModel
from twilio.rest import Client
from twilio.twiml.voice_response import Connect, VoiceResponse

from biomarkers import analyze_reference_ranges, get_women_advisory
from database import add_patient, get_patient, get_patients, init_db, update_patient
from ml_engine import DF, ENCODERS, FEATURE_COLS, MODEL, get_distribution_data, predict_risk
from pdf_report import generate_pdf
from voice_prompts import build_screening_prompt

BASE_DIR = Path(__file__).resolve().parent
RECORDINGS_DIR = BASE_DIR / "recordings"
RECORDINGS_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-4o-mini")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
NGROK_URL = os.getenv("NGROK_URL", "")

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
TWILIO_CLIENT = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else None
CALL_CONTEXTS: dict[str, dict[str, Any]] = {}

app = FastAPI(title="HeartLens MVP")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
init_db()


class HeartAssessmentRequest(BaseModel):
    name: str
    age: int
    sex: str
    life_stage: str = "not_applicable"
    phone: str | None = None
    resting_blood_pressure: float
    cholestoral: float
    oldpeak: float
    Max_heart_rate: float
    chest_pain_type: str
    fasting_blood_sugar: str
    rest_ecg: str
    exercise_induced_angina: str
    slope: str
    vessels_colored_by_flourosopy: str
    thalassemia: str
    # Extended fields from lab report
    hdl: float | None = None
    ldl: float | None = None
    triglycerides: float | None = None
    hba1c: float | None = None
    hs_crp: float | None = None
    serum_creatinine: float | None = None
    tsh: float | None = None
    bmi: float | None = None
    waist_circumference: float | None = None
    spo2: float | None = None
    resting_pulse_rate: float | None = None
    smoking_status: str | None = None
    family_history: str | None = None
    current_medications: str | None = None


class PatientCreateRequest(BaseModel):
    name: str
    age: int | None = None
    sex: str | None = None
    life_stage: str | None = None
    phone: str | None = None


class VoiceCallRequest(BaseModel):
    phone: str
    patient_name: str
    patient_age: int
    patient_sex: str
    life_stage: str = "not_applicable"
    risk_score: float = 0.0
    gap_summary: str = ""
    patient_id: int | None = None


class ReportRequest(BaseModel):
    patient: dict[str, Any]
    risk_result: dict[str, Any]
    voice_report: dict[str, Any] | None = None


def _build_analysis_payload(payload: dict[str, Any]) -> dict[str, Any]:
    risk_result = predict_risk(payload, MODEL, ENCODERS, FEATURE_COLS)
    reference_ranges = analyze_reference_ranges(payload, int(payload["age"]))
    women_advisory = []
    if payload["sex"] == "Female":
        women_advisory = get_women_advisory(int(payload["age"]), float(payload["Max_heart_rate"]))
    return {
        **risk_result,
        "reference_ranges": reference_ranges,
        "distribution_data": get_distribution_data(DF, payload["sex"]),
        "women_advisory": women_advisory,
        "gap_count": sum(1 for item in reference_ranges if item.get("gap")),
        "total_biomarkers": len(reference_ranges),
    }


def _extract_text_from_pdf_bytes(data: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(data)
        temp_path = temp_file.name
    try:
        document = fitz.open(temp_path)
        text = "\n".join(page.get_text() for page in document)
        document.close()
    finally:
        Path(temp_path).unlink(missing_ok=True)
    return text


async def _call_openai_json(prompt: str) -> dict[str, Any] | None:
    if OPENAI_CLIENT is None:
        return None

    def _sync_call() -> dict[str, Any] | None:
        response = OPENAI_CLIENT.chat.completions.create(
            model=OPENAI_TEXT_MODEL,
            messages=[
                {"role": "system", "content": "Return valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        return json.loads(content)

    try:
        return await asyncio.to_thread(_sync_call)
    except Exception:
        return None


def _heuristic_report_extract(text: str) -> dict[str, Any]:
    values: dict[str, Any] = {
        "name": None,
        "age": None,
        "sex": None,
        "life_stage": "not_applicable",
        "phone": None,
        "resting_blood_pressure": None,
        "cholestoral": None,
        "oldpeak": None,
        "Max_heart_rate": None,
        "chest_pain_type": None,
        "fasting_blood_sugar": None,
        "rest_ecg": None,
        "exercise_induced_angina": None,
        "slope": None,
        "vessels_colored_by_flourosopy": None,
        "thalassemia": None,
        "hdl": None,
        "ldl": None,
        "triglycerides": None,
        "hba1c": None,
        "hs_crp": None,
        "serum_creatinine": None,
        "tsh": None,
        "bmi": None,
        "waist_circumference": None,
        "spo2": None,
        "resting_pulse_rate": None,
        "smoking_status": None,
        "family_history": None,
        "current_medications": None,
    }
    lower_text = text.lower()
    original_text = text  # keep original case for name extraction

    # --- Demographics ---
    name_match = re.search(r"patient\s*name\s*[:.]\s*([A-Za-z .\-]+)", original_text, re.IGNORECASE)
    if name_match:
        values["name"] = name_match.group(1).strip().rstrip(".")

    age_match = re.search(r"(?:age\s*/?\s*sex|age)[^\d]{0,10}(\d{1,3})\s*(?:years|yrs|y)", lower_text)
    if age_match:
        values["age"] = int(age_match.group(1))

    sex_match = re.search(r"(?:age\s*/?\s*sex|sex)[^a-z]{0,10}(male|female)", lower_text)
    if sex_match:
        values["sex"] = sex_match.group(1).capitalize()

    phone_match = re.search(r"(?:contact|phone|mobile|tel)[^\d]{0,10}([\d\+\-\s]{7,15})", lower_text)
    if phone_match:
        values["phone"] = phone_match.group(1).strip()

    # Life stage
    if "postmenopaus" in lower_text:
        values["life_stage"] = "postmenopause"
    elif "perimenopaus" in lower_text:
        values["life_stage"] = "perimenopause"
    elif "pregnan" in lower_text:
        values["life_stage"] = "pregnancy"

    # --- Numeric vitals ---
    numeric_patterns: dict[str, list[str]] = {
        "resting_blood_pressure": [
            r"(?:resting\s+)?blood\s*pressure[^\d]{0,20}(\d{2,3})",
            r"\b(1[0-2]\d|[89]\d)\s*mmhg\b",
        ],
        "cholestoral": [
            r"total\s+chol(?:esterol)?[^\d]{0,20}(\d{2,3})",
            r"chol(?:esterol)?[^\d]{0,20}(\d{2,3})",
        ],
        "oldpeak": [
            r"(?:oldpeak|st\s*depression)[^\d]{0,20}(\d+(?:\.\d+)?)",
        ],
        "Max_heart_rate": [
            r"(?:max(?:imum)?\s*heart\s*rate\s*(?:achieved)?|max\s*hr)[^\d]{0,20}(\d{2,3})",
            r"heart\s*rate\s*achieved[^\d]{0,20}(\d{2,3})",
        ],
        "hdl": [r"hdl\s*(?:cholesterol)?[^\d]{0,20}(\d+(?:\.\d+)?)"],
        "ldl": [r"ldl\s*(?:cholesterol)?[^\d]{0,20}(\d+(?:\.\d+)?)"],
        "triglycerides": [r"triglycerid\w*[^\d]{0,20}(\d+(?:\.\d+)?)"],
        "hba1c": [r"hba1c[^\d]{0,20}(\d+(?:\.\d+)?)", r"\ba1c[^\d]{0,20}(\d+(?:\.\d+)?)"],
        "hs_crp": [r"hs[\-\s]?crp[^\d]{0,20}(\d+(?:\.\d+)?)", r"c[\-\s]?reactive[^\d]{0,20}(\d+(?:\.\d+)?)"],
        "serum_creatinine": [r"(?:serum\s+)?creatinine[^\d]{0,20}(\d+(?:\.\d+)?)"],
        "tsh": [r"\btsh[^\d]{0,20}(\d+(?:\.\d+)?)"],
        "bmi": [r"(?:bmi|body\s*mass\s*index)[^\d]{0,20}(\d+(?:\.\d+)?)"],
        "waist_circumference": [r"waist\s*(?:circumference)?[^\d]{0,20}(\d+(?:\.\d+)?)"],
        "spo2": [r"spo2[^\d]{0,20}(\d+(?:\.\d+)?)", r"pulse\s*ox[^\d]{0,20}(\d+(?:\.\d+)?)"],
        "resting_pulse_rate": [r"(?:resting\s+)?pulse\s*(?:rate)?[^\d]{0,20}(\d{2,3})"],
    }
    for key, regexes in numeric_patterns.items():
        for pattern in regexes:
            match = re.search(pattern, lower_text)
            if match:
                val_str = match.group(1)
                values[key] = float(val_str) if "." in val_str else int(val_str)
                break

    # --- Categorical fields ---
    # Chest pain type
    cpt_match = re.search(r"chest\s*pain\s*(?:type)?[^a-z]{0,15}(typical\s*angina|atypical\s*angina|non[\-\s]?anginal\s*pain|asymptomatic)", lower_text)
    if cpt_match:
        raw = cpt_match.group(1).strip()
        cpt_map = {"typical angina": "Typical angina", "atypical angina": "Atypical angina",
                   "non-anginal pain": "Non-anginal pain", "non anginal pain": "Non-anginal pain",
                   "nonanginal pain": "Non-anginal pain", "asymptomatic": "Asymptomatic"}
        values["chest_pain_type"] = cpt_map.get(raw.lower().replace("  ", " "), raw.title())

    # Fasting blood sugar
    fbs_match = re.search(r"fasting\s*(?:blood)?\s*sugar[^\d]{0,20}[<>]?\s*(\d+)", lower_text)
    if fbs_match:
        fbs_val = int(fbs_match.group(1))
        values["fasting_blood_sugar"] = "Greater than 120 mg/ml" if fbs_val > 120 else "Lower than 120 mg/ml"
    elif re.search(r"fasting\s*(?:blood)?\s*sugar[^\d]{0,30}normal", lower_text):
        values["fasting_blood_sugar"] = "Lower than 120 mg/ml"

    # Rest ECG
    ecg_match = re.search(r"(?:resting\s+)?(?:ecg|electrocardiogram)[^a-z]{0,30}(normal|st[\-\s]?t\s*wave|left\s*ventricular)", lower_text)
    if ecg_match:
        raw_ecg = ecg_match.group(1).strip()
        if "normal" in raw_ecg:
            values["rest_ecg"] = "Normal"
        elif "st" in raw_ecg:
            values["rest_ecg"] = "ST-T wave abnormality"
        elif "left" in raw_ecg:
            values["rest_ecg"] = "Left ventricular hypertrophy"
    elif re.search(r"(?:rest\s+ecg|resting.*ecg)[^a-z]{0,20}normal", lower_text):
        values["rest_ecg"] = "Normal"
    elif "normal sinus rhythm" in lower_text and "no acute st" in lower_text:
        values["rest_ecg"] = "Normal"

    # Exercise-induced angina
    eia_match = re.search(r"exercise\s*induced\s*angina[^a-z]{0,15}(yes|no)", lower_text)
    if eia_match:
        values["exercise_induced_angina"] = eia_match.group(1).capitalize()
    elif re.search(r"exercise\s*induced\s*angina.*\bno\b", lower_text):
        values["exercise_induced_angina"] = "No"

    # Slope
    slope_match = re.search(r"(?:st\s*(?:segment\s*)?slope|slope)[^a-z]{0,15}(upsloping|flat|downsloping)", lower_text)
    if slope_match:
        values["slope"] = slope_match.group(1).capitalize()

    # Vessels coloured by fluoroscopy
    vessels_match = re.search(r"(?:vessels?\s*(?:colou?red|calcification)|coronary\s*fluoroscopy)[^a-z]{0,30}(zero|one|two|three|four|0|1|2|3|4|no\s*vessel)", lower_text)
    if vessels_match:
        raw_v = vessels_match.group(1).strip()
        v_map = {"0": "Zero", "1": "One", "2": "Two", "3": "Three", "4": "Four",
                 "zero": "Zero", "one": "One", "two": "Two", "three": "Three", "four": "Four"}
        if raw_v.startswith("no"):
            values["vessels_colored_by_flourosopy"] = "Zero"
        else:
            values["vessels_colored_by_flourosopy"] = v_map.get(raw_v, "Zero")

    # Thalassemia / Thallium
    thal_match = re.search(r"(?:thalass[ae]mia|thallium\s*(?:scan)?\s*(?:pattern)?)[^a-z]{0,20}(normal|fixed\s*(?:defect)?|reversabl?e\s*(?:defect)?)", lower_text)
    if thal_match:
        raw_t = thal_match.group(1).strip()
        if "fixed" in raw_t:
            values["thalassemia"] = "Fixed Defect"
        elif "reversa" in raw_t:
            values["thalassemia"] = "Reversable Defect"
        else:
            values["thalassemia"] = "Normal"

    # Smoking status
    if "non-smoker" in lower_text or "non smoker" in lower_text:
        values["smoking_status"] = "Non-smoker"
    elif "former smoker" in lower_text or "ex-smoker" in lower_text:
        values["smoking_status"] = "Former smoker"
    elif "current smoker" in lower_text or "smoker" in lower_text:
        values["smoking_status"] = "Current smoker"

    # Family history
    fh_match = re.search(r"family\s*history[^.\n]{0,80}(father|mother|sibling|parent|brother|sister)[^.\n]{0,80}", lower_text)
    if fh_match:
        # Grab full sentence
        fh_full = re.search(r"family\s*history[^.\n]{0,120}", original_text, re.IGNORECASE)
        values["family_history"] = fh_full.group(0).strip() if fh_full else "Yes"
    elif re.search(r"family\s*history.*\bno\b|no.*family\s*history", lower_text):
        values["family_history"] = "No"

    # Current medications
    med_match = re.search(r"(?:current\s*)?medications?[^a-z]{0,10}([^\n]{5,120})", original_text, re.IGNORECASE)
    if med_match:
        values["current_medications"] = med_match.group(1).strip()

    return values


async def _extract_report_values(text: str) -> dict[str, Any]:
    prompt = f"""
    Extract patient demographics AND cardiac biomarker values from the report text below.
    Return JSON with these exact keys (use null when not found):

    Demographics:
    - name: patient full name
    - age: integer age in years
    - sex: "Male" or "Female"
    - life_stage: one of "not_applicable", "perimenopause", "postmenopause", "pregnancy" (look for keywords like postmenopausal)
    - phone: contact/mobile number as string

    Vitals & primary biomarkers:
    - resting_blood_pressure: systolic BP in mmHg (number)
    - cholestoral: total cholesterol in mg/dL (number)
    - oldpeak: ST depression value in mm (number)
    - Max_heart_rate: maximum heart rate achieved in bpm (number)

    Categorical fields (use EXACT values listed):
    - chest_pain_type: one of "Typical angina", "Atypical angina", "Non-anginal pain", "Asymptomatic"
    - fasting_blood_sugar: "Greater than 120 mg/ml" or "Lower than 120 mg/ml"
    - rest_ecg: one of "Normal", "ST-T wave abnormality", "Left ventricular hypertrophy"
    - exercise_induced_angina: "Yes" or "No"
    - slope: one of "Upsloping", "Flat", "Downsloping"
    - vessels_colored_by_flourosopy: one of "Zero", "One", "Two", "Three", "Four" (check coronary fluoroscopy)
    - thalassemia: one of "Normal", "Fixed Defect", "Reversable Defect" (check thallium scan pattern)

    Extended biomarkers (numbers, null if missing):
    hdl, ldl, triglycerides, hba1c, hs_crp, serum_creatinine, tsh,
    bmi, waist_circumference, spo2, resting_pulse_rate

    Lifestyle (strings, null if missing):
    smoking_status, family_history, current_medications

    Report text:
    {text[:6000]}
    """
    extracted = await _call_openai_json(prompt)
    if extracted:
        # Merge with heuristic as fallback for any nulls
        heuristic = _heuristic_report_extract(text)
        for key, val in heuristic.items():
            if val is not None and extracted.get(key) is None:
                extracted[key] = val
        return extracted
    return _heuristic_report_extract(text)


def _mock_voice_report(call_sid: str, payload: VoiceCallRequest) -> dict[str, Any]:
    report = {
        "call_sid": call_sid,
        "status": "completed",
        "transcript": (
            f"Mock screening call for {payload.patient_name}. Patient reported exertional fatigue, "
            "intermittent jaw discomfort, and occasional night-time breathlessness."
        ),
        "symptom_report": {
            "atypical_pain": {"present": True, "details": "Intermittent jaw discomfort", "severity": "moderate"},
            "respiratory": {"present": True, "details": "Occasional night-time breathlessness", "severity": "moderate"},
            "gastrointestinal": {"present": False, "details": None, "severity": None},
            "neurological": {"present": False, "details": None, "severity": None},
            "fatigue": {"present": True, "details": "Lower exercise tolerance", "severity": "high"},
            "autonomic": {"present": False, "details": None, "severity": None},
            "fluid_circulation": {"present": False, "details": None, "severity": None},
            "pre_event_warning": {"present": True, "details": "Symptoms worsening over two weeks", "severity": "moderate"},
            "sleep_related": {"present": True, "details": "Night-time breathlessness", "severity": "moderate"},
            "emotional": {"present": False, "details": None, "severity": None},
            "hormonal": {"present": payload.life_stage in {"perimenopause", "postmenopause"}, "details": payload.life_stage, "severity": "mild" if payload.life_stage else None},
            "exertion_related": {"present": True, "details": "Fatigue increases with mild exertion", "severity": "high"},
        },
        "red_flags": ["Reduced exercise tolerance", "Jaw discomfort", "Night-time breathlessness"],
        "recommendation": "Atypical cardiac symptoms were reported. Recommend ECG, troponin testing, and clinician review.",
    }
    output_path = RECORDINGS_DIR / f"{call_sid}_symptom_report.json"
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


async def _generate_structured_symptom_report(call_sid: str, transcript_text: str) -> dict[str, Any]:
    prompt = f"""
    Convert the following cardiac screening transcript into JSON.
    Return keys: atypical_pain, respiratory, gastrointestinal, neurological, fatigue,
    autonomic, fluid_circulation, pre_event_warning, sleep_related, emotional,
    hormonal, exertion_related, red_flags, recommendation.
    Each symptom key must contain: present, details, severity.

    Transcript:
    {transcript_text[:8000]}
    """
    extracted = await _call_openai_json(prompt)
    if not extracted:
        extracted = {
            "atypical_pain": {"present": False, "details": None, "severity": None},
            "respiratory": {"present": False, "details": None, "severity": None},
            "gastrointestinal": {"present": False, "details": None, "severity": None},
            "neurological": {"present": False, "details": None, "severity": None},
            "fatigue": {"present": False, "details": None, "severity": None},
            "autonomic": {"present": False, "details": None, "severity": None},
            "fluid_circulation": {"present": False, "details": None, "severity": None},
            "pre_event_warning": {"present": False, "details": None, "severity": None},
            "sleep_related": {"present": False, "details": None, "severity": None},
            "emotional": {"present": False, "details": None, "severity": None},
            "hormonal": {"present": False, "details": None, "severity": None},
            "exertion_related": {"present": False, "details": None, "severity": None},
            "red_flags": [],
            "recommendation": "Manual clinical review recommended.",
        }
    report = {
        "call_sid": call_sid,
        "status": "completed",
        "transcript": transcript_text,
        "symptom_report": {key: extracted[key] for key in [
            "atypical_pain", "respiratory", "gastrointestinal", "neurological", "fatigue",
            "autonomic", "fluid_circulation", "pre_event_warning", "sleep_related",
            "emotional", "hormonal", "exertion_related",
        ] if key in extracted},
        "red_flags": extracted.get("red_flags", []),
        "recommendation": extracted.get("recommendation", "Clinical follow-up recommended."),
    }
    output_path = RECORDINGS_DIR / f"{call_sid}_symptom_report.json"
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


async def process_recording_after_call(call_sid: str) -> dict[str, Any] | None:
    if not call_sid or TWILIO_CLIENT is None or OPENAI_CLIENT is None:
        return None
    try:
        recordings = await asyncio.to_thread(TWILIO_CLIENT.recordings.list, call_sid=call_sid)
        if not recordings:
            return None
        recording = recordings[0]
        recording_url = f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}"
        filename = RECORDINGS_DIR / f"{call_sid}.mp3"
        async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)) as session:
            async with session.get(recording_url, ssl=SSL_CONTEXT) as response:
                if response.status != 200:
                    return None
                filename.write_bytes(await response.read())
        with filename.open("rb") as audio_file:
            transcript = await asyncio.to_thread(
                OPENAI_CLIENT.audio.transcriptions.create,
                model="whisper-1",
                file=audio_file,
            )
        transcript_text = transcript.text
        (RECORDINGS_DIR / f"{call_sid}.txt").write_text(transcript_text, encoding="utf-8")
        return await _generate_structured_symptom_report(call_sid, transcript_text)
    except Exception:
        return None


def _gap_summary(reference_ranges: list[dict[str, Any]]) -> str:
    flagged = [item["metric"] for item in reference_ranges if item.get("gap")]
    if not flagged:
        return "No diagnostic gap was flagged in the range comparison."
    return f"Diagnostic gaps were flagged for: {', '.join(flagged)}."


@app.post("/api/risk/calculate")
async def calculate_risk(payload: HeartAssessmentRequest) -> dict[str, Any]:
    return _build_analysis_payload(payload.model_dump())


@app.post("/api/upload-report")
@app.post("/api/patient/upload-report")
async def upload_report(report: UploadFile = File(...)) -> dict[str, Any]:
    report_bytes = await report.read()
    text = _extract_text_from_pdf_bytes(report_bytes)
    values = await _extract_report_values(text)
    return {
        "extracted": True,
        "values": values,
        "raw_text_snippet": text[:500],
        "confidence_note": "Review extracted values before analysis. Fields not found were left blank.",
    }


@app.get("/api/clinician/patients")
async def clinician_patients() -> dict[str, Any]:
    return {"patients": get_patients()}


@app.post("/api/clinician/patients")
async def clinician_add_patient(payload: PatientCreateRequest) -> dict[str, Any]:
    patient_id = add_patient(payload.model_dump())
    patient = get_patient(patient_id)
    return {"patient": patient}


@app.get("/api/clinician/patients/{patient_id}")
async def clinician_get_patient(patient_id: int) -> dict[str, Any]:
    patient = get_patient(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"patient": patient}


@app.post("/api/clinician/patients/{patient_id}/upload-report")
async def clinician_upload_report(patient_id: int, report: UploadFile = File(...)) -> dict[str, Any]:
    patient = get_patient(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    result = await upload_report(report)
    values = result["values"]
    db_update = {
        "name": values.get("name"),
        "age": values.get("age"),
        "sex": values.get("sex"),
        "life_stage": values.get("life_stage"),
        "phone": values.get("phone"),
        "resting_blood_pressure": values.get("resting_blood_pressure"),
        "cholestoral": values.get("cholestoral"),
        "oldpeak": values.get("oldpeak"),
        "max_heart_rate": values.get("Max_heart_rate"),
        "chest_pain_type": values.get("chest_pain_type"),
        "fasting_blood_sugar": values.get("fasting_blood_sugar"),
        "rest_ecg": values.get("rest_ecg"),
        "exercise_induced_angina": values.get("exercise_induced_angina"),
        "slope": values.get("slope"),
        "vessels": values.get("vessels_colored_by_flourosopy"),
        "thalassemia": values.get("thalassemia"),
        "hdl": values.get("hdl"),
        "ldl": values.get("ldl"),
        "triglycerides": values.get("triglycerides"),
        "hba1c": values.get("hba1c"),
        "hs_crp": values.get("hs_crp"),
        "serum_creatinine": values.get("serum_creatinine"),
        "tsh": values.get("tsh"),
        "bmi": values.get("bmi"),
        "waist_circumference": values.get("waist_circumference"),
        "spo2": values.get("spo2"),
        "resting_pulse_rate": values.get("resting_pulse_rate"),
        "smoking_status": values.get("smoking_status"),
        "family_history": values.get("family_history"),
        "current_medications": values.get("current_medications"),
    }
    update_patient(patient_id, {key: value for key, value in db_update.items() if value is not None})
    return result


@app.post("/api/clinician/patients/{patient_id}/analyze")
async def clinician_analyze(patient_id: int, payload: HeartAssessmentRequest) -> dict[str, Any]:
    patient = get_patient(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    analysis = _build_analysis_payload(payload.model_dump())
    update_patient(
        patient_id,
        {
            "status": "flagged" if analysis["risk_score"] >= 60 else "assessed",
            "resting_blood_pressure": payload.resting_blood_pressure,
            "cholestoral": payload.cholestoral,
            "oldpeak": payload.oldpeak,
            "max_heart_rate": payload.Max_heart_rate,
            "chest_pain_type": payload.chest_pain_type,
            "fasting_blood_sugar": payload.fasting_blood_sugar,
            "rest_ecg": payload.rest_ecg,
            "exercise_induced_angina": payload.exercise_induced_angina,
            "slope": payload.slope,
            "vessels": payload.vessels_colored_by_flourosopy,
            "thalassemia": payload.thalassemia,
            "hdl": payload.hdl,
            "ldl": payload.ldl,
            "triglycerides": payload.triglycerides,
            "hba1c": payload.hba1c,
            "hs_crp": payload.hs_crp,
            "serum_creatinine": payload.serum_creatinine,
            "tsh": payload.tsh,
            "bmi": payload.bmi,
            "waist_circumference": payload.waist_circumference,
            "spo2": payload.spo2,
            "resting_pulse_rate": payload.resting_pulse_rate,
            "smoking_status": payload.smoking_status,
            "family_history": payload.family_history,
            "current_medications": payload.current_medications,
            "risk_score": analysis["risk_score"],
            "risk_level": analysis["risk_level"],
            "gap_count": analysis["gap_count"],
            "analysis_json": analysis,
        },
    )
    return analysis


@app.post("/api/voice/call")
async def start_voice_call(payload: VoiceCallRequest) -> dict[str, Any]:
    call_sid = f"mock-{uuid.uuid4().hex[:10]}"
    CALL_CONTEXTS[call_sid] = {**payload.model_dump(), "call_status": "in_progress"}

    if TWILIO_CLIENT and TWILIO_PHONE_NUMBER and NGROK_URL:
        try:
            call = await asyncio.to_thread(
                TWILIO_CLIENT.calls.create,
                url=f"{NGROK_URL}/outgoing-call",
                to=payload.phone,
                from_=TWILIO_PHONE_NUMBER,
                record=True,
            )
            call_sid = call.sid
            CALL_CONTEXTS[call_sid] = {**payload.model_dump(), "call_status": "in_progress"}
            status = "in_progress"
        except Exception:
            status = "in_progress"
            CALL_CONTEXTS[call_sid]["call_status"] = "in_progress"
            # Schedule mock completion after a delay
            asyncio.get_event_loop().call_later(
                6, lambda sid=call_sid, p=payload: _complete_mock_call(sid, p)
            )
    else:
        status = "in_progress"
        # Schedule mock completion after a delay (simulate call duration)
        asyncio.get_event_loop().call_later(
            6, lambda sid=call_sid, p=payload: _complete_mock_call(sid, p)
        )

    if payload.patient_id is not None:
        update_patient(payload.patient_id, {"call_sid": call_sid, "call_status": "in_progress"})
    return {"call_sid": call_sid, "status": status}


def _complete_mock_call(call_sid: str, payload: VoiceCallRequest) -> None:
    """Called after delay to simulate call completion."""
    report = _mock_voice_report(call_sid, payload)
    if call_sid in CALL_CONTEXTS:
        CALL_CONTEXTS[call_sid]["call_status"] = "completed"
    if payload.patient_id is not None:
        update_patient(payload.patient_id, {"call_status": "completed", "symptom_report_json": report})


@app.get("/api/voice/report/{call_sid}")
async def get_voice_report(call_sid: str) -> dict[str, Any]:
    report_path = RECORDINGS_DIR / f"{call_sid}_symptom_report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["status"] = "completed"
        return report
    if call_sid in CALL_CONTEXTS:
        return {"call_sid": call_sid, "status": CALL_CONTEXTS[call_sid].get("call_status", "in_progress")}
    raise HTTPException(status_code=404, detail="Call not found")


@app.post("/api/voice/transcribe/{call_sid}")
async def transcribe_call(call_sid: str) -> dict[str, Any]:
    """Transcribe recording and generate structured symptom report on demand."""
    # Return existing report if already processed
    report_path = RECORDINGS_DIR / f"{call_sid}_symptom_report.json"
    if report_path.exists():
        return json.loads(report_path.read_text(encoding="utf-8"))
    # Try real Twilio recording + Whisper transcription
    report = await process_recording_after_call(call_sid)
    if report:
        context = CALL_CONTEXTS.get(call_sid, {})
        patient_id = context.get("patient_id")
        if patient_id is not None:
            update_patient(patient_id, {"call_status": "completed", "symptom_report_json": report})
        if call_sid in CALL_CONTEXTS:
            CALL_CONTEXTS[call_sid]["call_status"] = "completed"
        return report
    # Fall back to mock report when no real recording is available
    context = CALL_CONTEXTS.get(call_sid, {})
    if not context:
        raise HTTPException(status_code=404, detail="Call context not found")
    mock_payload = VoiceCallRequest(
        phone=context.get("phone", ""),
        patient_name=context.get("patient_name", "Patient"),
        patient_age=int(context.get("patient_age", 50)),
        patient_sex=context.get("patient_sex", "Female"),
        life_stage=context.get("life_stage", "not_applicable"),
        risk_score=float(context.get("risk_score", 0.0)),
        gap_summary=context.get("gap_summary", ""),
        patient_id=context.get("patient_id"),
    )
    report = _mock_voice_report(call_sid, mock_payload)
    if mock_payload.patient_id is not None:
        update_patient(mock_payload.patient_id, {"call_status": "completed", "symptom_report_json": report})
    if call_sid in CALL_CONTEXTS:
        CALL_CONTEXTS[call_sid]["call_status"] = "completed"
    return report


@app.post("/api/report/generate")
async def report_generate(payload: ReportRequest) -> Response:
    pdf_bytes = generate_pdf(payload.patient, payload.risk_result, payload.voice_report)
    filename = f"HeartLens_{payload.patient.get('name', 'patient').replace(' ', '_')}.pdf"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)


class FinalReportRequest(BaseModel):
    patient: dict[str, Any]
    risk_result: dict[str, Any]
    voice_report: dict[str, Any]


@app.post("/api/voice/final-report")
async def generate_final_report(payload: FinalReportRequest) -> dict[str, Any]:
    """Combine risk analysis + voice transcript and send to LLM for comprehensive clinical report."""
    vr = payload.voice_report
    rr = payload.risk_result
    pt = payload.patient

    transcript = vr.get("transcript", "")
    red_flags = vr.get("red_flags", [])
    symptom_report = vr.get("symptom_report", {})

    # Build symptom summary from structured report
    symptom_lines = []
    for cat, info in symptom_report.items():
        if isinstance(info, dict) and info.get("present"):
            det = info.get("details", cat.replace("_", " "))
            sev = info.get("severity", "unknown")
            symptom_lines.append(f"- {cat.replace('_', ' ').title()}: {det} (severity: {sev})")
    symptom_summary = "\n".join(symptom_lines) if symptom_lines else "No atypical symptoms reported."

    # Reference range gap summary
    ref_ranges = rr.get("reference_ranges", [])
    gap_lines = []
    for r in ref_ranges:
        if r.get("gap"):
            gap_lines.append(f"- {r['metric']}: {r['value']} {r['unit']} — Male: {r['male_status']}, Female: {r['female_status']}. {r.get('gap_explanation', '')}")
    gap_summary = "\n".join(gap_lines) if gap_lines else "No diagnostic gaps detected."

    prompt = f"""You are a senior cardiologist AI assistant. Generate a comprehensive clinical assessment report.

PATIENT:
  Name: {pt.get('name', 'Unknown')}
  Age: {pt.get('age', 'N/A')} | Sex: {pt.get('sex', 'N/A')} | Life stage: {pt.get('life_stage', 'N/A')}

ML RISK ASSESSMENT:
  Risk score: {rr.get('risk_score', 0)}% ({rr.get('risk_level', 'N/A')})
  Diagnostic gaps: {rr.get('gap_count', 0)} / {rr.get('total_biomarkers', 0)}

BIOMARKER GAPS:
{gap_summary}

VOICE SCREENING TRANSCRIPT:
{transcript[:4000]}

DETECTED ATYPICAL SYMPTOMS:
{symptom_summary}

RED FLAGS: {', '.join(red_flags) if red_flags else 'None'}

WOMEN-SPECIFIC ADVISORIES: {', '.join(rr.get('women_advisory', [])) or 'None'}

Generate a JSON response with these keys:
- "clinical_summary": 3-4 sentence executive summary of findings
- "risk_interpretation": Interpret the ML risk score in clinical context (2-3 sentences)
- "symptom_analysis": Analysis of reported symptoms, especially atypical ones (2-4 sentences)
- "gap_analysis": What the diagnostic gaps mean clinically (2-3 sentences)
- "recommended_tests": Array of recommended follow-up tests/procedures
- "recommended_actions": Array of recommended clinical actions
- "urgency": "routine" | "soon" | "urgent" — how quickly follow-up is needed
- "urgency_rationale": Why this urgency level (1-2 sentences)
- "final_assessment": Comprehensive 4-6 sentence final clinical assessment tying everything together
"""

    llm_result = await _call_openai_json(prompt)
    if not llm_result:
        # Fallback: generate a heuristic report
        risk_score = rr.get("risk_score", 0)
        urgency = "urgent" if risk_score >= 70 or len(red_flags) >= 3 else "soon" if risk_score >= 40 or len(red_flags) >= 1 else "routine"
        llm_result = {
            "clinical_summary": f"Patient {pt.get('name', '')} presents with a {rr.get('risk_level', 'moderate')} cardiac risk score of {risk_score:.0f}%. "
                                f"{len(red_flags)} red flag(s) were identified during voice screening. "
                                f"{rr.get('gap_count', 0)} diagnostic gap(s) were found across gender-specific biomarker ranges.",
            "risk_interpretation": f"The ML model predicts a {risk_score:.0f}% cardiac risk, classified as {rr.get('risk_level', 'N/A')}. "
                                   "This should be correlated with clinical presentation and symptom screening findings.",
            "symptom_analysis": f"Voice screening identified: {', '.join(red_flags) if red_flags else 'no concerning symptoms'}. "
                                "Atypical presentations warrant clinical attention, especially in female patients.",
            "gap_analysis": f"{rr.get('gap_count', 0)} biomarker(s) showed different classifications under male vs. female reference ranges, "
                           "indicating potential under-detection with standard thresholds.",
            "recommended_tests": ["12-lead ECG", "Troponin levels", "Lipid panel review", "Stress echocardiography"],
            "recommended_actions": ["Schedule cardiology consultation", "Review current medications", "Lifestyle counseling"],
            "urgency": urgency,
            "urgency_rationale": f"Based on {risk_score:.0f}% risk score and {len(red_flags)} red flag(s).",
            "final_assessment": f"Patient requires {urgency} follow-up given the combination of ML risk prediction, "
                                f"voice screening findings, and biomarker analysis.",
        }

    return {
        "final_report": llm_result,
        "generated_at": json.dumps({"timestamp": str(uuid.uuid4())}),
    }


@app.post("/api/org/upload-batch")
async def org_upload_batch(file: UploadFile = File(...)) -> dict[str, Any]:
    content = (await file.read()).decode("utf-8")
    reader = csv.DictReader(content.splitlines())
    results = []
    for row in reader:
        age = int(row.get("age") or random.randint(35, 75))
        sex = row.get("sex") or random.choice(["Female", "Male"])
        base = random.uniform(15, 75)
        if sex == "Female" and age >= 50:
            base += random.uniform(5, 15)
        score = round(min(base, 95.0), 1)
        risk_level = "Low Risk" if score < 30 else "Moderate Risk" if score < 60 else "High Risk"
        flagged = score >= 40
        results.append(
            {
                "name": row.get("name", "Unknown"),
                "phone": row.get("phone", ""),
                "age": age,
                "sex": sex,
                "simulated_risk_score": score,
                "risk_level": risk_level,
                "flagged": flagged,
                "flag_reason": "High simulated risk score" if flagged else None,
            }
        )
    await asyncio.sleep(1)
    flagged_count = sum(1 for item in results if item["flagged"])
    avg_score = round(sum(item["simulated_risk_score"] for item in results) / len(results), 1) if results else 0.0
    return {"total": len(results), "processed": len(results), "flagged": flagged_count, "average_score": avg_score, "results": results}


@app.api_route("/outgoing-call", methods=["GET", "POST"])
async def outgoing_call(request: Request) -> HTMLResponse:
    call_sid = ""
    if request.method == "POST":
        form = await request.form()
        call_sid = str(form.get("CallSid") or "")
    response = VoiceResponse()
    response.pause(length=1)
    connect = Connect()
    stream_url = f"wss://{request.url.hostname}/media-stream"
    if call_sid:
        stream_url += f"?call_sid={call_sid}"
    connect.stream(url=stream_url)
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")


@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    call_sid = websocket.query_params.get("call_sid", "")
    context = CALL_CONTEXTS.get(call_sid, {})
    if not OPENAI_CLIENT or not OPENAI_API_KEY:
        await websocket.close()
        return
    prompt = build_screening_prompt(
        patient_name=context.get("patient_name", "Patient"),
        age=int(context.get("patient_age", 50)),
        sex=context.get("patient_sex", "Female"),
        life_stage=context.get("life_stage", "not_applicable"),
        risk_score=float(context.get("risk_score", 0.0)),
        gap_summary=context.get("gap_summary", ""),
    )
    stream_sid: str | None = None

    async with websockets.connect(
        "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2025-06-03",
        ssl=SSL_CONTEXT,
        additional_headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "OpenAI-Beta": "realtime=v1"},
    ) as openai_ws:
        await openai_ws.send(
            json.dumps(
                {
                    "type": "session.update",
                    "session": {
                        "turn_detection": {"type": "server_vad"},
                        "input_audio_format": "g711_ulaw",
                        "output_audio_format": "g711_ulaw",
                        "voice": "alloy",
                        "instructions": prompt,
                        "modalities": ["audio", "text"],
                        "temperature": 0.7,
                    },
                }
            )
        )
        # Trigger the AI to deliver its opening greeting
        await openai_ws.send(json.dumps({"type": "response.create"}))

        async def receive_from_twilio() -> None:
            nonlocal stream_sid
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)
                    if data.get("event") == "start":
                        stream_sid = data["start"]["streamSid"]
                    elif data.get("event") == "media":
                        await openai_ws.send(json.dumps({"type": "input_audio_buffer.append", "audio": data["media"]["payload"]}))
                    elif data.get("event") == "stop":
                        # Mark call as ended; transcription happens on-demand when user clicks Generate Report
                        if call_sid in CALL_CONTEXTS:
                            CALL_CONTEXTS[call_sid]["call_status"] = "call_ended"
                        patient_id = context.get("patient_id")
                        if patient_id is not None:
                            update_patient(patient_id, {"call_status": "call_ended"})
                        break
            except WebSocketDisconnect:
                pass

        async def send_to_twilio() -> None:
            async for message in openai_ws:
                data = json.loads(message)
                if data.get("type") == "response.audio.delta" and data.get("delta"):
                    # OpenAI delta is already base64-encoded G.711 µ-law; pass it through directly
                    await websocket.send_json({"event": "media", "streamSid": stream_sid or call_sid, "media": {"payload": data["delta"]}})

        await asyncio.gather(receive_from_twilio(), send_to_twilio())


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "patients": len(get_patients())}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "5050")))
