from fpdf import FPDF
import os

# ── Colour palette ─────────────────────────────────────────────────
NAVY   = (0, 40, 85)
DKBLUE = (0, 61, 115)
LTBLUE = (220, 233, 245)
ACCENT = (0, 122, 204)
WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GREY   = (100, 100, 100)
LTGREY = (230, 230, 230)
RED    = (180, 30, 30)
GREEN  = (30, 130, 60)

# ── Data ───────────────────────────────────────────────────────────
patient = dict(
    name="Ananya", phone="9625020380", age=55, sex="Female",
    life_stage="Postmenopausal", dob="14 August 1970",
    patient_id="AP-118492",
)
report_meta = dict(
    report_date="04 May 2026", collection_date="03 May 2026",
    collection_time="08:10 AM", accession="APD-CRS-2026-05114",
    lab="Apollo Diagnostics, South Extension Collection Center",
    report_type="Executive Cardiac Risk Screening Panel",
    referring="Self Referred", status="Final",
    barcode="2026051140118492",
)


# ── PDF class ──────────────────────────────────────────────────────
class LabReport(FPDF):
    _skip_header = False          # suppress header on cover page

    # ── header (pages 2+) ──────────────────────────────────────────
    def header(self):
        if self._skip_header:
            return
        # navy bar
        self.set_fill_color(*NAVY)
        self.rect(0, 0, 210, 18, "F")
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*WHITE)
        self.set_xy(10, 4)
        self.cell(100, 10, "Apollo Diagnostics")
        self.set_font("Helvetica", "", 8)
        self.set_xy(120, 4)
        self.cell(80, 5, "NABL Accredited | ISO 15189:2022", align="R")
        self.set_xy(120, 9)
        self.cell(80, 5, f"Accession: {report_meta['accession']}", align="R")
        # thin accent line
        self.set_fill_color(*ACCENT)
        self.rect(0, 18, 210, 1.2, "F")
        self.set_y(24)

    # ── footer ─────────────────────────────────────────────────────
    def footer(self):
        self.set_y(-18)
        self.set_draw_color(*LTGREY)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*GREY)
        self.cell(0, 4,
                  "Apollo Diagnostics  |  CIN: U85110KA2015PTC080553  |  "
                  "Regd. Office: #19, Swamy Vivekananda Road, Halasuru, "
                  "Bengaluru 560008", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(95, 4,
                  "This report is intended for physician review. "
                  "Not for medico-legal purposes.", align="L")
        self.cell(95, 4,
                  f"Page {self.page_no()}/{{nb}}", align="R")

    # ── watermark ──────────────────────────────────────────────────
    def _watermark(self):
        self.set_font("Helvetica", "B", 52)
        self.set_text_color(235, 235, 235)
        with self.rotation(35, 105, 148):
            self.text(40, 160, "APOLLO DIAGNOSTICS")
        self.set_text_color(*BLACK)

    # ── section heading ────────────────────────────────────────────
    def section(self, title):
        self.ln(3)
        self.set_fill_color(*NAVY)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_text_color(*BLACK)

    # ── sub-heading ────────────────────────────────────────────────
    def sub_section(self, title):
        self.ln(2)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*DKBLUE)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*ACCENT)
        self.line(self.l_margin, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.set_text_color(*BLACK)

    # ── key-value pair row ─────────────────────────────────────────
    def kv(self, key, value, bold_val=False):
        self.set_font("Helvetica", "B", 9)
        self.cell(55, 6, key)
        self.set_font("Helvetica", "B" if bold_val else "", 9)
        self.cell(0, 6, str(value), new_x="LMARGIN", new_y="NEXT")

    # ── table with header ──────────────────────────────────────────
    def data_table(self, headers, rows, col_widths=None, flag_col=None):
        if col_widths is None:
            n = len(headers)
            col_widths = [int(190 / n)] * n
            col_widths[-1] = 190 - sum(col_widths[:-1])  # absorb rounding
        # header row
        self.set_font("Helvetica", "B", 8.5)
        self.set_fill_color(*NAVY)
        self.set_text_color(*WHITE)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True, align="C")
        self.ln()
        # data rows
        self.set_font("Helvetica", "", 8.5)
        alt = False
        for row in rows:
            if alt:
                self.set_fill_color(*LTBLUE)
            else:
                self.set_fill_color(*WHITE)
            for i, val in enumerate(row):
                align = "L" if i == 0 else "C"
                # colour the flag column
                if flag_col is not None and i == flag_col:
                    v = str(val).strip().upper()
                    if v in ("HIGH", "ELEVATED", "ABOVE OPTIMAL",
                             "BORDERLINE HIGH", "OVERWEIGHT", "REDUCED"):
                        self.set_text_color(*RED)
                    elif v in ("NORMAL", "ACCEPTABLE", "DESIRABLE"):
                        self.set_text_color(*GREEN)
                    else:
                        self.set_text_color(*BLACK)
                else:
                    self.set_text_color(*BLACK)
                self.cell(col_widths[i], 6.5, str(val), border=1,
                          fill=True, align=align)
            self.ln()
            alt = not alt
        self.set_text_color(*BLACK)
        self.ln(2)

    # ── note / remark box ──────────────────────────────────────────
    def note_box(self, text, *, color=LTBLUE):
        self.set_fill_color(*color)
        self.set_font("Helvetica", "I", 8.5)
        self.set_text_color(60, 60, 60)
        x = self.get_x()
        y = self.get_y()
        self.set_draw_color(*ACCENT)
        # left accent bar
        self.rect(x, y, 2, 18, "F")
        self.set_fill_color(*color)
        self.set_x(x + 4)
        self.multi_cell(184, 5, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_text_color(*BLACK)

    # ── horizontal divider ─────────────────────────────────────────
    def divider(self):
        self.set_draw_color(*LTGREY)
        y = self.get_y()
        self.line(10, y, 200, y)
        self.ln(3)


# ── Build PDF ──────────────────────────────────────────────────────
pdf = LabReport()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=22)

# ═══════════════════════════════════════════════════════════════════
# PAGE 1 — COVER
# ═══════════════════════════════════════════════════════════════════
pdf._skip_header = True
pdf.add_page()

# Full-width navy banner
pdf.set_fill_color(*NAVY)
pdf.rect(0, 0, 210, 60, "F")
pdf.set_font("Helvetica", "B", 28)
pdf.set_text_color(*WHITE)
pdf.set_xy(0, 12)
pdf.cell(210, 14, "Apollo Diagnostics", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 11)
pdf.cell(210, 7, "A Unit of Apollo Hospitals Enterprise Ltd.", align="C",
         new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 9)
pdf.cell(210, 6,
         "NABL Accredited  |  CAP Certified  |  ISO 15189:2022  |  "
         "ICMR-Approved Testing Facility", align="C",
         new_x="LMARGIN", new_y="NEXT")
# thin gold accent
pdf.set_fill_color(218, 165, 32)
pdf.rect(0, 60, 210, 2, "F")

# Report title block
pdf.ln(12)
pdf.set_text_color(*NAVY)
pdf.set_font("Helvetica", "B", 20)
pdf.cell(0, 12, "Comprehensive Cardiac", align="C",
         new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 12, "Screening Report", align="C",
         new_x="LMARGIN", new_y="NEXT")
pdf.ln(6)
pdf.set_draw_color(*ACCENT)
pdf.line(60, pdf.get_y(), 150, pdf.get_y())
pdf.ln(8)

# Patient info box on cover
pdf.set_fill_color(*LTBLUE)
pdf.set_draw_color(*NAVY)
bx = 30; by = pdf.get_y(); bw = 150; bh = 58
pdf.rect(bx, by, bw, bh, "D")
pdf.rect(bx, by, bw, 9, "F")
pdf.set_font("Helvetica", "B", 10)
pdf.set_text_color(*NAVY)
pdf.set_xy(bx + 2, by + 1.5)
pdf.cell(bw - 4, 6, "PATIENT INFORMATION", align="C")
pdf.set_font("Helvetica", "", 9.5)
pdf.set_text_color(*BLACK)
info_lines = [
    ("Patient Name", patient["name"]),
    ("Patient ID", patient["patient_id"]),
    ("Age / Sex", f"{patient['age']} Years / {patient['sex']}"),
    ("Date of Birth", patient["dob"]),
    ("Contact", patient["phone"]),
    ("Report Date", report_meta["report_date"]),
    ("Sample Collected", f"{report_meta['collection_date']}  {report_meta['collection_time']}"),
]
yy = by + 12
for k, v in info_lines:
    pdf.set_xy(bx + 6, yy)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(45, 6, k + ":")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(90, 6, v)
    yy += 6.5

pdf.set_y(by + bh + 8)
# Accession + barcode placeholder
pdf.set_font("Courier", "B", 11)
pdf.set_text_color(*NAVY)
pdf.cell(0, 7, f"|||  {report_meta['barcode']}  |||", align="C",
         new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 8)
pdf.set_text_color(*GREY)
pdf.cell(0, 5, f"Accession No: {report_meta['accession']}",
         align="C", new_x="LMARGIN", new_y="NEXT")

# Confidentiality strip at bottom
pdf.set_y(255)
pdf.set_fill_color(*NAVY)
pdf.rect(0, 270, 210, 27, "F")
pdf.set_text_color(*WHITE)
pdf.set_font("Helvetica", "I", 8)
pdf.set_xy(10, 273)
pdf.multi_cell(190, 4,
    "CONFIDENTIAL: This document contains private health information "
    "protected under applicable data-protection regulations. "
    "Unauthorized reproduction or distribution is prohibited. "
    "Refer all queries to the issuing laboratory.\n"
    "Apollo Diagnostics  |  CIN: U85110KA2015PTC080553  |  "
    "Toll-Free: 1800-123-0100  |  www.apollodiagnostics.in",
    align="C")

pdf._skip_header = False

# ═══════════════════════════════════════════════════════════════════
# PAGE 2 — PATIENT DEMOGRAPHICS  &  CLINICAL SUMMARY
# ═══════════════════════════════════════════════════════════════════
pdf.add_page()
pdf._watermark()

pdf.section("PATIENT DEMOGRAPHICS & REPORT DETAILS")
pdf.set_font("Helvetica", "", 9)
# Two-column key-value grid
left_kv = [
    ("Patient Name", patient["name"]),
    ("Patient ID", patient["patient_id"]),
    ("Age / Sex", f"{patient['age']} Years / {patient['sex']}"),
    ("Date of Birth", patient["dob"]),
    ("Life Stage", patient["life_stage"]),
]
right_kv = [
    ("Report Type", report_meta["report_type"]),
    ("Accession No.", report_meta["accession"]),
    ("Referring Physician", report_meta["referring"]),
    ("Report Status", report_meta["status"]),
    ("Laboratory", report_meta["lab"]),
]
for i in range(max(len(left_kv), len(right_kv))):
    if i < len(left_kv):
        pdf.set_font("Helvetica", "B", 9); pdf.cell(35, 6, left_kv[i][0] + ":")
        pdf.set_font("Helvetica", "", 9);  pdf.cell(55, 6, left_kv[i][1])
    else:
        pdf.cell(90, 6, "")
    if i < len(right_kv):
        pdf.set_font("Helvetica", "B", 9); pdf.cell(38, 6, right_kv[i][0] + ":")
        pdf.set_font("Helvetica", "", 9);  pdf.cell(0, 6, right_kv[i][1],
                                                     new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.ln()

pdf.divider()

pdf.sub_section("Clinical Indication")
pdf.set_font("Helvetica", "", 9.5)
pdf.multi_cell(0, 5.5,
    "Patient presented for preventive cardiac evaluation due to "
    "intermittent fatigue on exertion, occasional jaw heaviness, "
    "and family history of cardiovascular disease (father - MI at "
    "age 62). Cardiac biomarker review, resting ECG, treadmill "
    "stress summary, and imaging support note requested.",
    new_x="LMARGIN", new_y="NEXT")
pdf.ln(2)

pdf.sub_section("Executive Summary")
bullets = [
    "Resting blood pressure is above the ideal preventive threshold.",
    "Total cholesterol is mildly elevated; LDL borderline high.",
    "Treadmill stress parameters show reduced reserve relative to "
    "age-adjusted expectation.",
    "Further clinician correlation is advised if symptoms persist "
    "despite non-alarming initial presentation.",
]
pdf.set_font("Helvetica", "", 9.5)
for b in bullets:
    pdf.cell(6, 5.5, "-")  # bullet char
    pdf.multi_cell(0, 5.5, b, new_x="LMARGIN", new_y="NEXT")
pdf.ln(1)

pdf.note_box(
    "Clinical Note: In postmenopausal women, atypical presentations "
    "(fatigue, jaw discomfort, exertional dyspnoea) are common and "
    "may be the only early indicators of ischaemic heart disease. "
    "Standard thresholds may under-detect risk in this cohort."
)

# ═══════════════════════════════════════════════════════════════════
# PAGE 3 — VITALS  &  BIOCHEMISTRY
# ═══════════════════════════════════════════════════════════════════
pdf.add_page()
pdf._watermark()

pdf.section("VITAL PARAMETERS & BASELINE CARDIAC PROFILE")
pdf.data_table(
    ["Parameter", "Result", "Unit", "Reference", "Status"],
    [
        ["Resting Blood Pressure", "128", "mmHg", "< 120", "Above optimal"],
        ["Resting Pulse Rate",     "78",  "bpm",  "60-100", "Normal"],
        ["Body Mass Index (BMI)",  "27.4","kg/m2","18.5-24.9","Overweight"],
        ["SpO2 (Pulse Ox)",       "98",  "%",    "> 95",  "Normal"],
        ["Waist Circumference",    "88",  "cm",   "< 80 (F)", "Above threshold"],
        ["Respiratory Rate",       "16",  "/min", "12-20", "Normal"],
    ],
    col_widths=[52, 18, 18, 28, 40],
    flag_col=4,
)

pdf.section("BIOCHEMISTRY & LIPID PROFILE")
pdf.data_table(
    ["Test", "Result", "Unit", "Reference Range", "Interpretation"],
    [
        ["Total Cholesterol",         "210",  "mg/dL", "< 200",       "Mildly elevated"],
        ["HDL Cholesterol",           "46",   "mg/dL", "> 50 (F)",    "Acceptable"],
        ["LDL Cholesterol (Calc.)",   "136",  "mg/dL", "< 130",       "Borderline high"],
        ["VLDL Cholesterol",          "30.8", "mg/dL", "< 30",        "Normal"],
        ["Triglycerides",             "154",  "mg/dL", "< 150",       "Borderline high"],
        ["Non-HDL Cholesterol",       "164",  "mg/dL", "< 130",       "Elevated"],
        ["Total Chol / HDL Ratio",    "4.6",  "",      "< 4.5",       "Borderline high"],
        ["LDL / HDL Ratio",           "2.96", "",      "< 3.0",       "Normal"],
        ["Fasting Blood Sugar",       "< 120","mg/dL", "< 126",       "Normal"],
        ["HbA1c",                     "5.8",  "%",     "< 5.7",       "Pre-diabetic range"],
        ["hs-CRP",                    "2.4",  "mg/L",  "< 1.0 low risk", "Moderate risk"],
        ["Serum Creatinine",          "0.9",  "mg/dL", "0.6-1.1",     "Normal"],
        ["TSH",                       "3.8",  "mIU/L", "0.4-4.0",     "Normal"],
    ],
    col_widths=[48, 16, 16, 36, 40],
    flag_col=4,
)

pdf.note_box(
    "Method: Cholesterol measured by enzymatic colorimetric assay "
    "(Roche Cobas c702). HbA1c by HPLC (Bio-Rad D-100). "
    "hs-CRP by immunoturbidimetry."
)

# ═══════════════════════════════════════════════════════════════════
# PAGE 4 — ECG  &  TREADMILL STRESS TEST
# ═══════════════════════════════════════════════════════════════════
pdf.add_page()
pdf._watermark()

pdf.section("RESTING ELECTROCARDIOGRAM (ECG)")
pdf.set_font("Helvetica", "", 9.5)
pdf.kv("Heart Rate", "78 bpm")
pdf.kv("Rhythm", "Normal sinus rhythm")
pdf.kv("PR Interval", "164 ms (normal)")
pdf.kv("QRS Duration", "88 ms (normal)")
pdf.kv("QTc Interval", "412 ms (normal)")
pdf.kv("Axis", "Normal axis")
pdf.kv("ST-T Changes", "None at rest")
pdf.ln(2)
pdf.note_box(
    "Interpretation: Sinus rhythm maintained at a rate of 78 bpm. "
    "No acute ST-T wave abnormality observed at rest. P-wave "
    "morphology is normal. No bundle-branch block or chamber "
    "enlargement pattern seen. Correlate clinically with stress "
    "response findings."
)

pdf.divider()

pdf.section("TREADMILL STRESS TEST (TMT)")
pdf.set_font("Helvetica", "B", 9)
pdf.set_text_color(*DKBLUE)
pdf.cell(0, 6, "Protocol: Bruce  |  Duration: 6 min 42 sec  |  "
         "Exercise Capacity: Moderately reduced for age",
         new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(*BLACK)
pdf.ln(1)

pdf.data_table(
    ["Parameter", "Result", "Unit", "Expected / Threshold", "Comment"],
    [
        ["Max Heart Rate Achieved", "145", "bpm", "165 (age-predicted)", "87.9% of predicted"],
        ["Target HR (85%)",         "140", "bpm", "140",                 "Achieved"],
        ["ST Depression (Oldpeak)", "1.2", "mm",  "< 1.0",              "Mild depression"],
        ["ST Segment Slope",        "Flat","",    "Upsloping normal",    "Requires correlation"],
        ["Exercise Induced Angina", "No",  "",    "",                    "No chest pain"],
        ["Duke Treadmill Score",    "+2",  "",    "> +5 low risk",       "Intermediate"],
        ["Rate-Pressure Product",   "18850","",   "> 25000 adequate",    "Reduced"],
        ["Recovery ST (3 min)",     "0.4", "mm",  "< 0.5",              "Normal recovery"],
        ["BP at Peak Exercise",     "168/88","mmHg","< 200/100",        "Normal response"],
        ["Test Termination",        "Fatigue","",  "",                   "Patient-requested"],
    ],
    col_widths=[44, 16, 12, 42, 42],
    flag_col=4,
)

pdf.note_box(
    "Observations: No classical crushing chest pain reported during "
    "exercise. Patient described generalized tiredness and mild jaw "
    "discomfort at peak exercise (Stage III). Recovery was uneventful; "
    "ST segment returned to baseline within 3 minutes. Clinical "
    "correlation is advised given the atypical symptom presentation "
    "in a postmenopausal female patient."
)

# ═══════════════════════════════════════════════════════════════════
# PAGE 5 — IMAGING  &  SYMPTOM INTAKE
# ═══════════════════════════════════════════════════════════════════
pdf.add_page()
pdf._watermark()

pdf.section("IMAGING & SUPPORTIVE CARDIAC RISK INDICATORS")
pdf.data_table(
    ["Investigation", "Finding", "Category / Value", "Comment"],
    [
        ["Coronary Fluoroscopy",   "No vessel calcification seen",
         "Zero vessels coloured", "Non-invasive summary only"],
        ["Thallium Scan Pattern",  "Fixed perfusion defect noted",
         "Fixed Defect",          "Correlate with cardiology review"],
        ["Chest Pain Type (Hx)",   "Atypical angina",
         "Type 2",                "Patient history form entry"],
        ["2D Echo (LV EF%)",       "58%",
         "Normal (> 55%)",        "Preserved systolic function"],
        ["LV Wall Motion",        "Normal",
         "No regional abnormality","Global kinesis normal"],
    ],
    col_widths=[40, 50, 42, 48],
    flag_col=None,
)

pdf.divider()

pdf.section("PATIENT SYMPTOM INTAKE SHEET")
pdf.set_font("Helvetica", "", 9.5)
symptoms = [
    ("Duration of Complaints",    "2-3 months"),
    ("Primary Symptom",           "Reduced exercise tolerance"),
    ("Secondary Symptoms",        "Intermittent fatigue on stairs, "
                                  "occasional jaw tightness"),
    ("Chest Pain",                "No severe chest pain reported"),
    ("Syncope / Pre-syncope",     "None"),
    ("Pedal Oedema",              "None documented"),
    ("Palpitations",              "Occasional, non-sustained"),
    ("Orthopnoea / PND",          "None"),
    ("Family History",            "Father - MI at age 62"),
    ("Smoking Status",            "Non-smoker"),
    ("Alcohol Intake",            "Occasional social use"),
    ("Current Medications",       "Tab. Ecosprin 75 mg OD (self-started)"),
]
for k, v in symptoms:
    pdf.kv(k, v)
pdf.ln(2)
pdf.note_box(
    "Assessment Note: This combination of mild lipid elevation, "
    "exertional fatigue, atypical symptoms, and stress-test changes "
    "should be assessed in the context of sex-specific cardiovascular "
    "presentation. Normal resting ECG does not exclude ischaemic risk "
    "in symptomatic patients."
)

# ═══════════════════════════════════════════════════════════════════
# PAGE 6 — CONSOLIDATED IMPRESSION  &  SIGN-OFF
# ═══════════════════════════════════════════════════════════════════
pdf.add_page()
pdf._watermark()

pdf.section("CONSOLIDATED IMPRESSION")
pdf.sub_section("Key Values for Clinical Correlation")
pdf.data_table(
    ["Biomarker / Parameter", "Observed Value", "Flag"],
    [
        ["Resting Blood Pressure",      "128 mmHg",          "Above optimal"],
        ["Total Cholesterol",           "210 mg/dL",         "Mildly elevated"],
        ["LDL Cholesterol",             "136 mg/dL",         "Borderline high"],
        ["HbA1c",                       "5.8 %",             "Pre-diabetic"],
        ["hs-CRP",                      "2.4 mg/L",          "Moderate risk"],
        ["Fasting Blood Sugar",         "< 120 mg/dL",       "Normal"],
        ["Rest ECG",                    "Normal",            "Normal"],
        ["Max Heart Rate Achieved",     "145 bpm (87.9%)",   "Near threshold"],
        ["ST Depression / Oldpeak",     "1.2 mm",            "Mild"],
        ["Exercise Induced Angina",     "No",                "Normal"],
        ["ST Slope",                    "Flat",              "Requires correlation"],
        ["Vessels (Fluoroscopy)",       "Zero",              "Normal"],
        ["Thallium Pattern",            "Fixed Defect",      "Abnormal"],
        ["Chest Pain Type",             "Atypical angina",   "Type 2"],
    ],
    col_widths=[60, 50, 46],
    flag_col=2,
)

pdf.divider()

pdf.sub_section("Clinical Recommendations")
pdf.set_font("Helvetica", "", 9.5)
recs = [
    "Review lipid abnormalities and exercise response with a "
    "consulting physician at the earliest.",
    "If fatigue, jaw discomfort, breathlessness, or other atypical "
    "symptoms persist, obtain dedicated cardiology consultation.",
    "Correlate findings with sex-specific cardiac risk interpretation "
    "- standard risk calculators may underestimate risk in "
    "postmenopausal women.",
    "Lifestyle modification: dietary changes (low saturated fat, "
    "increased fibre), structured aerobic exercise 150 min/week, "
    "weight management.",
    "Consider repeat lipid panel, HbA1c, and hs-CRP in 3 months "
    "with physician-guided pharmacotherapy review.",
    "Tobacco avoidance and blood-pressure monitoring at home are "
    "recommended.",
]
for i, r in enumerate(recs, 1):
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(8, 5.5, f"{i}.")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.multi_cell(0, 5.5, r, new_x="LMARGIN", new_y="NEXT")
pdf.ln(3)

# ── Disclaimer box ─────────────────────────────────────────────
pdf.set_fill_color(255, 248, 230)
pdf.set_draw_color(200, 160, 60)
pdf.rect(10, pdf.get_y(), 190, 22, "D")
pdf.set_fill_color(255, 248, 230)
pdf.rect(10, pdf.get_y(), 190, 22, "F")
pdf.set_font("Helvetica", "BI", 8)
pdf.set_text_color(120, 80, 0)
pdf.set_xy(14, pdf.get_y() + 2)
pdf.multi_cell(182, 4,
    "DISCLAIMER: This report is generated as part of a comprehensive "
    "cardiac screening programme and is intended for physician review "
    "in conjunction with clinical findings, patient history, and "
    "additional diagnostic evaluation. It should not be used as the "
    "sole basis for diagnosis or treatment. Results may vary with "
    "methodology and clinical context.", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(*BLACK)
pdf.ln(6)

# ── Signature block ────────────────────────────────────────────
pdf.divider()
pdf.set_font("Helvetica", "", 9)
# Left signatory
pdf.cell(90, 5, "Verified By:", new_x="RIGHT")
pdf.cell(90, 5, "Authorized Signatory:", new_x="LMARGIN", new_y="NEXT")
pdf.ln(8)
pdf.set_font("Helvetica", "B", 9)
pdf.cell(90, 5, "Dr. Meera Subramanian, MD (Pathology)", new_x="RIGHT")
pdf.cell(90, 5, "Dr. Rajesh K. Iyer, DM (Cardiology)", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 8)
pdf.set_text_color(*GREY)
pdf.cell(90, 5, "Consultant Pathologist  |  Reg. No. KMC-48231",
         new_x="RIGHT")
pdf.cell(90, 5, "Sr. Consultant Cardiologist  |  Reg. No. KMC-31045",
         new_x="LMARGIN", new_y="NEXT")
pdf.cell(90, 5, "Apollo Diagnostics, South Extension", new_x="RIGHT")
pdf.cell(90, 5, "Apollo Hospitals, Jubilee Hills", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_text_color(*BLACK)
pdf.set_font("Courier", "B", 10)
pdf.cell(0, 6, f"|||  {report_meta['barcode']}  |||", align="C",
         new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 7)
pdf.set_text_color(*GREY)
pdf.cell(0, 4, "Scan barcode to verify report authenticity at "
         "verify.apollodiagnostics.in", align="C",
         new_x="LMARGIN", new_y="NEXT")
pdf.cell(0, 4, "--- End of Report ---", align="C")

# ═══════════════════════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════════════════════
out = os.path.join(os.path.dirname(__file__) or ".", "ananya_cardiac_report.pdf")
pdf.output(out)
print(f"PDF generated: {out}")
