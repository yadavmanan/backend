from __future__ import annotations

from pathlib import Path

SYMPTOM_CATEGORIES = [
    "Atypical pain patterns: jaw, neck, throat, shoulder, upper back, or arm discomfort",
    "Chest discomfort described as pressure, heaviness, fullness, or burning rather than classic pain",
    "Respiratory symptoms such as breathlessness, air hunger, or difficulty lying flat",
    "Gastrointestinal symptoms such as nausea, indigestion, bloating, or upper abdominal pain",
    "Neurological symptoms such as dizziness, presyncope, confusion, or concentration changes",
    "Sudden fatigue or major drop in exercise tolerance",
    "Autonomic symptoms such as cold sweats, palpitations, anxiety, or unexplained weakness",
    "Fluid or circulation signs such as swelling in legs, ankles, or feet",
    "Warning symptoms in the days or weeks before the current concern",
    "Sleep-related symptoms such as waking breathless or worsening symptoms at night",
    "Hormonal or life-stage interactions, including pregnancy, postpartum, peri-menopause, or post-menopause",
    "Exertion-related symptom triggers and recovery pattern",
]

HIDDEN_SYMPTOMS_PATH = Path(__file__).resolve().parents[1] / "hidden_symptomps.md"


def _knowledge_excerpt() -> str:
    try:
        text = HIDDEN_SYMPTOMS_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    return text[:2500]


def build_screening_prompt(
    patient_name: str,
    age: int,
    sex: str,
    life_stage: str,
    risk_score: float,
    gap_summary: str,
) -> str:
    categories = "\n".join(f"{index}. {item}" for index, item in enumerate(SYMPTOM_CATEGORIES, start=1))
    return f"""You are a cardiac health screening assistant from HeartLens.

You are calling {patient_name}, a {age}-year-old {sex} patient in the life stage '{life_stage}'.
Their preliminary risk score is {risk_score}%. {gap_summary}

Goal:
- Screen for atypical cardiac symptoms that are commonly missed, especially in women.
- Ask about the following symptom areas one at a time in a calm, empathetic, conversational tone.
- Keep the call concise, around 3 to 5 minutes.
- Do not diagnose. Collect screening information and suggest clinical follow-up when concerning findings appear.

Symptom categories to cover:
{categories}

Call style:
- Start by introducing HeartLens and confirming the patient is comfortable to continue.
- Ask short, plain-language questions.
- If the patient reports a symptom, ask one brief follow-up about timing, severity, and trigger.
- Adapt to sex and life stage. For example, ask post-menopausal patients about fatigue, sleep changes, and breathlessness.
- End by briefly summarizing what was reported and advising medical review if needed.

Clinical reference excerpt:
{_knowledge_excerpt()}
"""