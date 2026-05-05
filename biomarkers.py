from __future__ import annotations

from typing import Any

MC = "#4A90D9"
FC = "#E8688A"
GC = "#27AE60"
GC2 = "#82E0AA"
OC = "#F39C12"
RC = "#E74C3C"


BIOMARKERS: dict[str, dict[str, Any]] = {
    "resting_blood_pressure": {
        "label": "Resting Blood Pressure",
        "unit": "mmHg",
        "chart_range": (80, 180),
        "male_zones": [
            (0, 120, "Optimal", GC),
            (120, 130, "Normal", GC2),
            (130, 140, "Borderline", OC),
            (140, 999, "High", RC),
        ],
        "female_zones": [
            (0, 115, "Optimal", GC),
            (115, 125, "Normal", GC2),
            (125, 132, "Borderline", OC),
            (132, 999, "High", RC),
        ],
        "male_cite": "AHA/ACC 2017: concern threshold >= 130 mmHg",
        "female_cite": (
            "Female-adjusted: concern threshold >= 125 mmHg "
            "(Women's Heart Alliance; SPRINT trial subgroup data)"
        ),
        "gap": (
            "Women develop cardiovascular events at lower absolute BP values than men. "
            "A reading of 128 mmHg appears Normal on male-calibrated tools but Borderline "
            "on female-specific scales, creating a missed early-intervention window."
        ),
    },
    "cholestoral": {
        "label": "Total Cholesterol",
        "unit": "mg/dl",
        "chart_range": (100, 400),
        "male_zones": [
            (0, 200, "Optimal", GC),
            (200, 240, "Borderline", OC),
            (240, 999, "High", RC),
        ],
        "female_zones": [
            (0, 190, "Optimal", GC),
            (190, 220, "Borderline", OC),
            (220, 999, "High", RC),
        ],
        "male_cite": "NCEP ATP III: concern threshold >= 200 mg/dl",
        "female_cite": (
            "Female-adjusted: concern threshold >= 190 mg/dl "
            "(post-menopausal LDL rise documented earlier; Framingham risk sex adjustment)"
        ),
        "gap": (
            "Post-menopausal women experience a sharp LDL rise. Women with confirmed heart "
            "disease averaged higher cholesterol at diagnosis than men at the same disease "
            "stage, consistent with delayed detection under male-calibrated thresholds."
        ),
    },
    "oldpeak": {
        "label": "ST Depression (Oldpeak)",
        "unit": "mm",
        "chart_range": (0.0, 5.0),
        "male_zones": [
            (0.0, 1.0, "Normal", GC),
            (1.0, 2.0, "Moderate", OC),
            (2.0, 999, "Significant", RC),
        ],
        "female_zones": [
            (0.0, 1.5, "Normal", GC),
            (1.5, 2.5, "Moderate", OC),
            (2.5, 999, "Significant", RC),
        ],
        "male_cite": "Standard: ST depression > 1.0 mm = concerning",
        "female_cite": (
            "Female-adjusted: > 1.5 mm more specific in women "
            "(WISE study; Gulati et al., JAMA 2005)"
        ),
        "gap": (
            "ST depression has lower specificity in women. The male 1.0 mm threshold can "
            "generate false positives in female patients, causing diagnostic confusion."
        ),
    },
}

# ── Extended biomarkers (optional fields from lab report) ──────────
EXTENDED_BIOMARKERS: dict[str, dict[str, Any]] = {
    "hdl": {
        "label": "HDL Cholesterol",
        "unit": "mg/dL",
        "chart_range": (20, 100),
        "male_zones": [
            (0, 40, "Low", RC),
            (40, 60, "Acceptable", GC2),
            (60, 999, "Optimal", GC),
        ],
        "female_zones": [
            (0, 50, "Low", RC),
            (50, 70, "Acceptable", GC2),
            (70, 999, "Optimal", GC),
        ],
        "male_cite": "AHA: HDL < 40 mg/dL is a major risk factor in men",
        "female_cite": (
            "Female-adjusted: HDL < 50 mg/dL is a risk factor in women "
            "(AHA/ACC guidelines; higher protective threshold for women)"
        ),
        "gap": (
            "Women naturally have higher HDL levels. A value considered acceptable "
            "for men may indicate insufficient cardioprotection in women."
        ),
    },
    "ldl": {
        "label": "LDL Cholesterol",
        "unit": "mg/dL",
        "chart_range": (50, 250),
        "male_zones": [
            (0, 100, "Optimal", GC),
            (100, 130, "Near Optimal", GC2),
            (130, 160, "Borderline High", OC),
            (160, 999, "High", RC),
        ],
        "female_zones": [
            (0, 100, "Optimal", GC),
            (100, 120, "Near Optimal", GC2),
            (120, 150, "Borderline High", OC),
            (150, 999, "High", RC),
        ],
        "male_cite": "NCEP ATP III: LDL < 100 optimal, 130-159 borderline high",
        "female_cite": (
            "Female-adjusted: postmenopausal women experience rapid LDL rise; "
            "earlier intervention threshold recommended (Framingham data)"
        ),
        "gap": (
            "Post-menopausal LDL increases sharply. Women may reach 'borderline' "
            "at lower absolute values than male-calibrated charts suggest."
        ),
    },
    "triglycerides": {
        "label": "Triglycerides",
        "unit": "mg/dL",
        "chart_range": (50, 300),
        "male_zones": [
            (0, 150, "Normal", GC),
            (150, 200, "Borderline High", OC),
            (200, 999, "High", RC),
        ],
        "female_zones": [
            (0, 150, "Normal", GC),
            (150, 175, "Borderline High", OC),
            (175, 999, "High", RC),
        ],
        "male_cite": "AHA: Triglycerides < 150 mg/dL desirable",
        "female_cite": (
            "Female-adjusted: elevated triglycerides carry higher relative "
            "cardiovascular risk in women than in men (Mora et al., Circulation 2008)"
        ),
        "gap": (
            "Triglyceride elevation is a stronger independent risk factor for CVD "
            "in women than men, yet the same thresholds are typically applied."
        ),
    },
    "hba1c": {
        "label": "HbA1c",
        "unit": "%",
        "chart_range": (4.0, 10.0),
        "male_zones": [
            (0, 5.7, "Normal", GC),
            (5.7, 6.5, "Pre-diabetic", OC),
            (6.5, 999, "Diabetic", RC),
        ],
        "female_zones": [
            (0, 5.7, "Normal", GC),
            (5.7, 6.5, "Pre-diabetic", OC),
            (6.5, 999, "Diabetic", RC),
        ],
        "male_cite": "ADA: HbA1c < 5.7% normal, 5.7-6.4% prediabetes",
        "female_cite": (
            "Same thresholds apply, but diabetes confers 2-3x higher relative "
            "cardiovascular risk in women vs men (Peters et al., Diabetologia 2014)"
        ),
        "gap": (
            "While the diagnostic thresholds are identical, the cardiovascular impact "
            "of pre-diabetes and diabetes is disproportionately higher in women."
        ),
    },
    "hs_crp": {
        "label": "hs-CRP",
        "unit": "mg/L",
        "chart_range": (0, 10),
        "male_zones": [
            (0, 1.0, "Low Risk", GC),
            (1.0, 3.0, "Moderate Risk", OC),
            (3.0, 999, "High Risk", RC),
        ],
        "female_zones": [
            (0, 1.0, "Low Risk", GC),
            (1.0, 2.0, "Moderate Risk", OC),
            (2.0, 999, "High Risk", RC),
        ],
        "male_cite": "AHA/CDC: hs-CRP < 1.0 low risk, 1.0-3.0 moderate",
        "female_cite": (
            "Female-adjusted: hs-CRP is a stronger independent predictor of "
            "cardiovascular events in women (JUPITER trial; Ridker et al.)"
        ),
        "gap": (
            "Inflammatory markers like hs-CRP are more predictive of cardiac events "
            "in women. A 'moderate' reading in men may represent 'high risk' in women."
        ),
    },
    "bmi": {
        "label": "Body Mass Index (BMI)",
        "unit": "kg/m²",
        "chart_range": (15, 45),
        "male_zones": [
            (0, 18.5, "Underweight", OC),
            (18.5, 25, "Normal", GC),
            (25, 30, "Overweight", OC),
            (30, 999, "Obese", RC),
        ],
        "female_zones": [
            (0, 18.5, "Underweight", OC),
            (18.5, 25, "Normal", GC),
            (25, 30, "Overweight", OC),
            (30, 999, "Obese", RC),
        ],
        "male_cite": "WHO: BMI 18.5-24.9 normal weight",
        "female_cite": (
            "Same BMI categories, but body composition differs: women have higher "
            "fat percentage at equivalent BMI. Waist circumference may be more predictive."
        ),
        "gap": (
            "BMI does not account for sex-specific body fat distribution. "
            "Central adiposity (waist circumference) is a better cardiac predictor in women."
        ),
    },
    "waist_circumference": {
        "label": "Waist Circumference",
        "unit": "cm",
        "chart_range": (50, 130),
        "male_zones": [
            (0, 94, "Normal", GC),
            (94, 102, "At Risk", OC),
            (102, 999, "High Risk", RC),
        ],
        "female_zones": [
            (0, 80, "Normal", GC),
            (80, 88, "At Risk", OC),
            (88, 999, "High Risk", RC),
        ],
        "male_cite": "IDF/WHO: < 94 cm normal for men",
        "female_cite": (
            "Female-adjusted: < 80 cm normal (IDF); central obesity "
            "begins at a much lower threshold in women"
        ),
        "gap": (
            "Waist circumference thresholds differ significantly by sex. A measurement "
            "of 88 cm is 'normal' for men but 'high risk' for women."
        ),
    },
    "resting_pulse_rate": {
        "label": "Resting Pulse Rate",
        "unit": "bpm",
        "chart_range": (40, 120),
        "male_zones": [
            (0, 60, "Low", GC2),
            (60, 100, "Normal", GC),
            (100, 999, "Elevated", RC),
        ],
        "female_zones": [
            (0, 60, "Low", GC2),
            (60, 100, "Normal", GC),
            (100, 999, "Elevated", RC),
        ],
        "male_cite": "AHA: Normal resting heart rate 60-100 bpm",
        "female_cite": (
            "Same range, but resting tachycardia in women may indicate "
            "autonomic dysfunction or masked cardiac stress"
        ),
        "gap": (
            "While the normal range is the same, persistently elevated resting pulse "
            "in women may warrant additional autonomic evaluation."
        ),
    },
}


def classify(value: float, zones: list[tuple[float, float, str, str]]) -> tuple[str, str]:
    for lo, hi, label, color in zones:
        if lo <= value < hi:
            return label, color
    _, _, label, color = zones[-1]
    return label, color


def analyze_reference_ranges(patient_data: dict[str, Any], age: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    for metric_key in ["resting_blood_pressure", "cholestoral", "oldpeak"]:
        spec = BIOMARKERS[metric_key]
        value = float(patient_data[metric_key])
        male_status, male_color = classify(value, spec["male_zones"])
        female_status, female_color = classify(value, spec["female_zones"])
        results.append(
            {
                "metric_key": metric_key,
                "metric": spec["label"],
                "value": value,
                "unit": spec["unit"],
                "male_status": male_status,
                "male_color": male_color,
                "female_status": female_status,
                "female_color": female_color,
                "gap": male_status != female_status,
                "gap_explanation": spec["gap"],
                "male_cite": spec["male_cite"],
                "female_cite": spec["female_cite"],
                "male_zones": spec["male_zones"],
                "female_zones": spec["female_zones"],
                "chart_range": spec["chart_range"],
            }
        )

    # ── Extended biomarkers (only when values are provided) ────────
    for metric_key, spec in EXTENDED_BIOMARKERS.items():
        raw_value = patient_data.get(metric_key)
        if raw_value is None:
            continue
        try:
            value = float(raw_value)
        except (ValueError, TypeError):
            continue
        male_status, male_color = classify(value, spec["male_zones"])
        female_status, female_color = classify(value, spec["female_zones"])
        results.append(
            {
                "metric_key": metric_key,
                "metric": spec["label"],
                "value": value,
                "unit": spec["unit"],
                "male_status": male_status,
                "male_color": male_color,
                "female_status": female_status,
                "female_color": female_color,
                "gap": male_status != female_status,
                "gap_explanation": spec["gap"],
                "male_cite": spec["male_cite"],
                "female_cite": spec["female_cite"],
                "male_zones": spec["male_zones"],
                "female_zones": spec["female_zones"],
                "chart_range": spec["chart_range"],
            }
        )

    max_hr = float(patient_data["Max_heart_rate"])
    male_predicted = 220 - age
    female_predicted = 206 - (0.88 * age)
    male_85 = 0.85 * male_predicted
    female_85 = 0.85 * female_predicted
    male_status = "Adequate" if max_hr >= male_85 else "Inadequate"
    female_status = "Adequate" if max_hr >= female_85 else "Inadequate"
    results.append(
        {
            "metric_key": "Max_heart_rate",
            "metric": "Max Heart Rate",
            "value": max_hr,
            "unit": "bpm",
            "male_predicted": male_predicted,
            "female_predicted": round(female_predicted, 2),
            "male_85_target": round(male_85, 2),
            "female_85_target": round(female_85, 2),
            "male_status": male_status,
            "male_color": GC if male_status == "Adequate" else RC,
            "female_status": female_status,
            "female_color": GC if female_status == "Adequate" else RC,
            "gap": male_status != female_status,
            "gap_explanation": (
                "Stress-test targets differ by sex. Gulati's formula generally sets a lower "
                "expected maximum heart rate for women than the male 220-age formula."
            ),
        }
    )

    return results


def get_women_advisory(age: int, max_hr: float) -> list[str]:
    female_predicted = 206 - (0.88 * age)
    return [
        "Atypical symptoms such as jaw pain, back pain, fatigue, nausea, or breathlessness can be cardiac warning signs even without chest pain.",
        (
            f"Stress-test context: Gulati's formula gives a predicted max heart rate of "
            f"{female_predicted:.1f} bpm for age {age}, compared with 220-age."
        ),
        "If fluoroscopy shows zero blocked vessels but symptoms persist, evaluate for microvascular disease (INOCA or MINOCA).",
        "Blood pressure and cholesterol thresholds are often based on male-dominant trial data, so earlier action at lower values may be warranted.",
        f"Current max heart rate entered is {max_hr:.1f} bpm. Pair this with ECG and symptom context rather than using heart rate alone.",
    ]