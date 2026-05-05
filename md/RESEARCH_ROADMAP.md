# HeartLens — Research Tasks for the Team
## What We Need Validated to Back Every Claim in This Application

> **How to use this document**: Each task below is tied to a specific thing our app already does (or claims). Your research output will be plugged directly into the codebase. For every task, I've listed **exactly what the app currently says**, **where in the code it lives**, and **what we need from you** so we can say "this is backed by research."

---

## PART A — Biomarker Thresholds (HerInsight Module)
**Code file**: `biomarkers.py` → `BIOMARKERS` and `EXTENDED_BIOMARKERS` dicts
**What it does**: Shows each biomarker on a dual male/female scale and flags a "diagnostic gap" when a patient's value falls in different zones on the two scales.

---

### Task A1 — Resting Blood Pressure Thresholds
**What the app currently uses**:
| Zone | Male | Female |
|------|------|--------|
| Optimal | < 120 | < 115 |
| Normal | 120–130 | 115–125 |
| Borderline | 130–140 | 125–132 |
| High | ≥ 140 | ≥ 132 |

**Current citation in code**: "Women's Heart Alliance; SPRINT trial subgroup data"
**Current gap claim**: "Women develop cardiovascular events at lower absolute BP values than men. A reading of 128 mmHg appears Normal on male-calibrated tools but Borderline on female-specific scales."

**What we need from the research team**:
1. Find the exact SPRINT trial subgroup analysis that shows sex-specific BP outcomes. Provide the paper title, authors, journal, year, and the specific table/figure with the female BP thresholds.
2. Validate or correct the female thresholds above. Is 125 mmHg the right "concern" cutoff for women? If not, what should it be?
3. Find 2–3 additional peer-reviewed papers supporting lower BP intervention thresholds in women.
4. Quantify: at what BP value does female CVD risk equal male CVD risk at 130 mmHg?

**Deliverable format**: A short summary paragraph + a table of recommended thresholds with citations + list of paper references (DOI links).

---

### Task A2 — Total Cholesterol Thresholds
**What the app currently uses**:
| Zone | Male | Female |
|------|------|--------|
| Optimal | < 200 | < 190 |
| Borderline | 200–240 | 190–220 |
| High | ≥ 240 | ≥ 220 |

**Current citation**: "Framingham risk sex adjustment; post-menopausal LDL rise documented earlier"
**Current gap claim**: "Post-menopausal women experience a sharp LDL rise. Women with confirmed heart disease averaged higher cholesterol at diagnosis than men at the same disease stage."

**What we need**:
1. Find the Framingham Heart Study data showing sex-specific cholesterol risk curves. Exact paper + figure.
2. Validate 190 mg/dL as the female concern threshold. What does the literature actually support?
3. Quantify the post-menopausal LDL shift — by how many mg/dL does LDL typically rise, and over what timeframe after menopause?
4. Find data on cholesterol levels at diagnosis: do women with confirmed CVD really have higher cholesterol at diagnosis than men at the same disease stage?

**Deliverable format**: Summary paragraph + corrected thresholds if needed + references.

---

### Task A3 — ST Depression (Oldpeak) Thresholds
**What the app currently uses**:
| Zone | Male | Female |
|------|------|--------|
| Normal | < 1.0 | < 1.5 |
| Moderate | 1.0–2.0 | 1.5–2.5 |
| Significant | ≥ 2.0 | ≥ 2.5 |

**Current citation**: "WISE study; Gulati et al., JAMA 2005"
**Current gap claim**: "ST depression has lower specificity in women. The male 1.0 mm threshold can generate false positives in female patients."

**What we need**:
1. Pull the exact findings from Gulati et al., JAMA 2005 — what did the paper actually say about female ST depression thresholds?
2. Pull the WISE (Women's Ischemia Syndrome Evaluation) study findings on ST depression specificity in women.
3. Validate: is 1.5 mm the right female "concern" cutoff, or did the papers suggest a different number?
4. What is the sensitivity/specificity of the 1.0 mm threshold in women vs men?

**Deliverable format**: Exact numbers from the papers + validated or corrected thresholds + DOI links.

---

### Task A4 — HDL Cholesterol Thresholds
**What the app currently uses**: Male risk < 40 mg/dL, Female risk < 50 mg/dL
**Current citation**: "AHA/ACC guidelines; higher protective threshold for women"
**Current gap claim**: "Women naturally have higher HDL levels. A value considered acceptable for men may indicate insufficient cardioprotection in women."

**What we need**:
1. Confirm the AHA/ACC guideline citation that specifically states HDL < 50 as a risk factor in women (vs < 40 in men). Provide the guideline document name and year.
2. What is the average HDL difference between healthy men and healthy women?
3. Any data on HDL as an independent CVD predictor stratified by sex?

**Deliverable format**: Guideline citation + supporting data + references.

---

### Task A5 — LDL Cholesterol Thresholds
**What the app currently uses**: Female "Borderline High" starts at 120 mg/dL (vs 130 for male)
**Current citation**: "Framingham data — postmenopausal women experience rapid LDL rise; earlier intervention threshold recommended"

**What we need**:
1. Find the Framingham or equivalent data justifying earlier LDL intervention in women.
2. Is 120 mg/dL a validated female-specific borderline threshold, or is this an assumption?
3. What does the ACC/AHA lipid guideline say about sex-specific LDL targets?

**Deliverable format**: Validated thresholds + literature references.

---

### Task A6 — Triglycerides Sex-Specific Risk
**What the app currently uses**: Female "Borderline High" at 150–175 (vs 150–200 for male)
**Current citation**: "Mora et al., Circulation 2008"
**Current gap claim**: "Triglyceride elevation is a stronger independent risk factor for CVD in women than men."

**What we need**:
1. Pull the exact findings from Mora et al., Circulation 2008 — relative risk ratios by sex.
2. Does the paper support a lower female threshold (175 vs 200)? Or is it about relative risk, not absolute threshold?
3. Any additional studies confirming triglycerides as a stronger female CVD predictor?

**Deliverable format**: Exact data from the paper + whether our threshold adjustment is justified + references.

---

### Task A7 — HbA1c and Sex-Specific Cardiovascular Impact
**What the app currently uses**: Same thresholds for both sexes (Normal < 5.7, Pre-diabetic 5.7–6.5, Diabetic ≥ 6.5)
**Current citation**: "Peters et al., Diabetologia 2014 — diabetes confers 2–3x higher relative cardiovascular risk in women vs men"

**What we need**:
1. Pull exact data from Peters et al., Diabetologia 2014 — what was the relative risk ratio? Was it 2x or 3x?
2. Should we apply a risk multiplier in the app when a female patient has HbA1c ≥ 5.7? If so, what multiplier?
3. Any data on pre-diabetes (5.7–6.4) conferring higher relative CVD risk in women?

**Deliverable format**: Exact risk ratios from the paper + recommendation on whether/how to integrate a sex-specific risk multiplier + references.

---

### Task A8 — hs-CRP (High-Sensitivity C-Reactive Protein) Thresholds
**What the app currently uses**: Female "High Risk" starts at ≥ 2.0 mg/L (vs ≥ 3.0 for male)
**Current citation**: "JUPITER trial; Ridker et al."
**Current gap claim**: "Inflammatory markers like hs-CRP are more predictive of cardiac events in women."

**What we need**:
1. Pull JUPITER trial data on hs-CRP as a CVD predictor stratified by sex. Exact hazard ratios.
2. Is 2.0 mg/L a validated female "high risk" threshold, or should it be something else?
3. Did Ridker et al. specifically recommend different hs-CRP cutoffs by sex?

**Deliverable format**: Exact findings + validated thresholds + DOI links.

---

### Task A9 — Waist Circumference Thresholds
**What the app currently uses**: Male normal < 94 cm, Female normal < 80 cm (IDF/WHO)
**Current gap claim**: "A measurement of 88 cm is 'normal' for men but 'high risk' for women."

**What we need**:
1. Confirm the IDF and WHO source documents for these sex-specific thresholds.
2. Is waist circumference a better CVD predictor than BMI specifically in women? Find the comparative data.
3. Any data on waist-to-hip ratio vs waist circumference alone for female cardiac risk?

**Deliverable format**: Source document citations + comparative predictive data + references.

---

### Task A10 — BMI Limitations and Body Composition
**Current gap claim in code**: "BMI does not account for sex-specific body fat distribution. Central adiposity (waist circumference) is a better cardiac predictor in women."

**What we need**:
1. Find studies comparing BMI vs waist circumference as CVD predictors in women specifically.
2. At what BMI do women and men have equivalent cardiovascular risk? (i.e., is risk-equivalent BMI lower in women?)
3. Should we add a "BMI is less reliable for women" warning in the app? What evidence supports this?

**Deliverable format**: Summary of evidence + references.

---

## PART B — ML Risk Model (HerRisk Module)
**Code file**: `ml_engine.py`
**What it does**: Trains a Random Forest (200 estimators) on the UCI Heart Disease dataset (`HeartDiseaseTrain-Test.csv`). Predicts cardiac risk as a percentage. Shows feature importance and distribution plots by sex.

---

### Task B1 — Sex-Stratified Model Performance Comparison
**What the app currently does**: Trains ONE model on all patients (male + female combined).

**What we need**:
1. Using the same `HeartDiseaseTrain-Test.csv` file, train three models:
   - Mixed-sex model (current approach)
   - Male-only model (trained and tested on males only)
   - Female-only model (trained and tested on females only)
2. Report accuracy, precision, recall, F1 score, and AUC for each.
3. Test the mixed-sex model on female-only test data — does performance drop?
4. Report the **exact numbers** so we can display them in the app as evidence of gender bias.

**Deliverable format**: Table of metrics for all three models + confusion matrices + a paragraph summarizing the gender bias finding.

---

### Task B2 — Feature Importance Differences by Sex
**What the app currently does**: Shows a single feature importance chart from the mixed model.

**What we need**:
1. Generate feature importance rankings separately for male and female subsets.
2. Which features are more important for predicting heart disease in women vs men?
3. Specifically examine:
   - `chest_pain_type`: Do atypical pain types predict disease more in women?
   - `vessels_colored_by_flourosopy`: Do women with disease show 0 blocked vessels more often?
   - `oldpeak`: Is ST depression less predictive in women?
   - `cholestoral` and `resting_blood_pressure`: Are these higher in women at the same disease stage?
4. Provide the exact importance scores so we can show a side-by-side male vs female feature importance chart.

**Deliverable format**: Two ranked feature importance lists (male/female) + specific findings for the 4 features above + raw scores.

---

### Task B3 — Microvascular Disease Signal in the Data
**What the app currently claims** (in `get_women_advisory`): "If fluoroscopy shows zero blocked vessels but symptoms persist, evaluate for microvascular disease (INOCA or MINOCA)."

**What we need**:
1. In the UCI dataset, how many female patients with heart disease (target=1) have `vessels_colored_by_flourosopy = 0`? What percentage?
2. Same question for male patients — what's the comparison?
3. Find 2–3 papers on INOCA/MINOCA prevalence in women vs men.
4. What is the recommended diagnostic pathway when a woman has cardiac symptoms but 0 blocked vessels?

**Deliverable format**: Dataset statistics + literature review + clinical pathway recommendation + references.

---

### Task B4 — UCI Dataset Limitations and Bias Assessment
**What we need**:
1. What is the male-to-female ratio in `HeartDiseaseTrain-Test.csv`?
2. Is the dataset representative of real-world cardiac patient demographics?
3. What are the known limitations of the UCI Heart Disease dataset for sex-stratified analysis?
4. Recommend 2–3 alternative or supplementary datasets that have better female representation.

**Deliverable format**: Dataset demographic breakdown + limitation summary + alternative dataset recommendations with links.

---

## PART C — Max Heart Rate Formula
**Code file**: `biomarkers.py` → `analyze_reference_ranges()` and `get_women_advisory()`
**What the app currently uses**:
- Male predicted max HR: `220 - age`
- Female predicted max HR: `206 - (0.88 × age)` (Gulati's formula)
- Stress test "adequate" threshold: 85% of predicted max

---

### Task C1 — Gulati's Formula Validation
**What we need**:
1. Pull the original Gulati paper — full citation, journal, year, sample size, population demographics.
2. What was the prediction accuracy of Gulati's formula vs 220-age in women?
3. Has the formula been externally validated? By whom? With what results?
4. Are there newer/better female-specific max HR formulas published since Gulati?
5. Is 85% of predicted max the right "adequate" threshold for women, or should it be different?

**Deliverable format**: Full paper citation + validation data + recommendation on whether to keep/update the formula + references.

---

## PART D — Voice Screening Symptom Categories (HerSymptoms Module)
**Code file**: `voice_prompts.py` → `SYMPTOM_CATEGORIES` list
**What it does**: An AI voice agent calls the patient and screens for 12 symptom categories. The app then structures findings into a report with severity ratings and red flags.

---

### Task D1 — Atypical Symptom Prevalence in Women
**The 12 symptom categories currently screened**:
1. Atypical pain (jaw, neck, throat, shoulder, upper back, arm)
2. Chest discomfort described as pressure/heaviness/fullness (not "pain")
3. Breathlessness / air hunger
4. GI symptoms (nausea, indigestion, bloating, upper abdominal pain)
5. Neurological (dizziness, presyncope, confusion)
6. Sudden fatigue / exercise intolerance
7. Autonomic (cold sweats, palpitations, anxiety, unexplained weakness)
8. Fluid/circulation (leg/ankle/feet swelling)
9. Warning symptoms in days/weeks before current concern
10. Sleep-related (waking breathless, symptoms worse at night)
11. Hormonal/life-stage interactions
12. Exertion-related triggers and recovery

**What we need FOR EACH of the 12 categories**:
1. What percentage of women with confirmed cardiac events presented with this symptom?
2. What percentage of men with confirmed cardiac events presented with this symptom?
3. How often is this symptom present in women WITHOUT chest pain?
4. What is the sensitivity and specificity of this symptom for cardiac disease in women?
5. Provide 1–2 key paper references per category.

**Deliverable format**: A table with 12 rows (one per category) and columns for: female prevalence %, male prevalence %, female-without-chest-pain %, sensitivity, specificity, key reference.

---

### Task D2 — "Sent Home" Symptom Patterns
**What we need**:
1. Literature on women presenting to the ED with cardiac events who were initially discharged ("sent home").
2. What symptom combinations most commonly led to missed diagnoses in women?
3. What is the rate of initial misdiagnosis in women vs men presenting with acute coronary syndrome?
4. Average delay (in hours) between first presentation and correct cardiac diagnosis, stratified by sex.

**Deliverable format**: Statistics on misdiagnosis rates + common missed symptom patterns + time-to-diagnosis delay data + references.

---

### Task D3 — Life Stage Impact on Symptom Presentation
**What we need**:
1. How do cardiac symptoms differ in pre-menopausal vs post-menopausal women?
2. Pregnancy-related cardiac risk: what symptoms should be screened during/after pregnancy?
3. Perimenopause: which cardiac symptoms overlap with menopausal symptoms (and get dismissed)?
4. Should the voice screening questions change based on life stage? Specific recommendations.

**Deliverable format**: Life-stage-stratified symptom guidance + references.

---

## PART E — Women's Advisory Messages
**Code file**: `biomarkers.py` → `get_women_advisory()` function
**What the app currently displays to female patients**:
1. "Atypical symptoms such as jaw pain, back pain, fatigue, nausea, or breathlessness can be cardiac warning signs even without chest pain."
2. Stress-test context using Gulati's formula.
3. "If fluoroscopy shows zero blocked vessels but symptoms persist, evaluate for microvascular disease (INOCA or MINOCA)."
4. "Blood pressure and cholesterol thresholds are often based on male-dominant trial data, so earlier action at lower values may be warranted."
5. Max heart rate interpretation advice.

---

### Task E1 — Validate Each Advisory Statement
**What we need**: For each of the 5 advisory statements above, provide:
1. The specific peer-reviewed evidence supporting the claim.
2. Whether the statement is accurate as written, or needs rewording.
3. A citation we can display alongside the advisory (author, journal, year).

**Deliverable format**: 5 validated statements, each with a citation + any recommended rewording.

---

## PART F — Dataset and Training Data Evidence
**Data file**: `data/HeartDiseaseTrain-Test.csv` (UCI Heart Disease dataset)

---

### Task F1 — Chi-Square Test: Sex vs Heart Disease Outcome
**What the app implicitly claims**: Sex statistically affects heart disease outcomes in the UCI dataset.

**What we need**:
1. Run a Chi-Square test of independence: sex × target (heart disease yes/no).
2. Report the chi-square statistic, p-value, and degrees of freedom.
3. Run additional statistical tests: point-biserial correlation, odds ratio with 95% CI.
4. Is the relationship between sex and heart disease outcome statistically significant?

**Deliverable format**: Test results table + interpretation paragraph.

---

### Task F2 — Distribution Analysis by Sex
**What the app currently shows**: Histograms of resting BP, cholesterol, max HR, and oldpeak, split by healthy/disease, filtered by patient sex.

**What we need**:
1. For each of the 4 features (resting_blood_pressure, cholestoral, Max_heart_rate, oldpeak), compute:
   - Mean, median, std dev for healthy males, diseased males, healthy females, diseased females.
   - Statistical test (t-test or Mann-Whitney) comparing diseased females vs diseased males.
2. Are the distributions significantly different between sexes? At what confidence level?
3. Do women with heart disease show different biomarker profiles than men with heart disease?

**Deliverable format**: Statistics table (4 features × 4 groups) + significance test results + summary.

---

## Summary — Deliverable Checklist

| Task | Module It Backs | Priority | Deliverable |
|------|----------------|----------|-------------|
| A1 | Blood Pressure thresholds | HIGH | Validated thresholds + 3 citations |
| A2 | Cholesterol thresholds | HIGH | Validated thresholds + Framingham data |
| A3 | ST Depression thresholds | HIGH | WISE/Gulati exact data + validated cutoff |
| A4 | HDL thresholds | MEDIUM | AHA/ACC guideline citation |
| A5 | LDL thresholds | MEDIUM | Validated female-specific threshold |
| A6 | Triglycerides risk | MEDIUM | Mora et al. exact findings |
| A7 | HbA1c risk multiplier | MEDIUM | Peters et al. exact risk ratios |
| A8 | hs-CRP thresholds | MEDIUM | JUPITER trial sex-stratified data |
| A9 | Waist circumference | LOW | IDF/WHO source docs |
| A10 | BMI limitations | LOW | Comparative predictor data |
| B1 | ML model gender bias | HIGH | 3-model performance comparison |
| B2 | Feature importance by sex | HIGH | Sex-stratified importance rankings |
| B3 | Microvascular disease | HIGH | Dataset stats + INOCA/MINOCA literature |
| B4 | Dataset limitations | MEDIUM | Demographic breakdown + alternatives |
| C1 | Max HR formula | HIGH | Gulati validation + alternatives |
| D1 | 12 symptom categories | HIGH | Prevalence table per category per sex |
| D2 | Missed diagnosis patterns | HIGH | ED misdiagnosis rates + symptom combos |
| D3 | Life stage symptoms | MEDIUM | Stage-stratified symptom guidance |
| E1 | Advisory statements | MEDIUM | 5 validated claims with citations |
| F1 | Sex vs outcome stats | HIGH | Chi-square + odds ratio results |
| F2 | Distribution analysis | MEDIUM | 4-feature × 4-group statistics |

---

## What Happens After You Complete These Tasks

Once you deliver the research findings:
1. **Thresholds (A1–A10)**: We update the exact zone numbers in `biomarkers.py` and add proper citations.
2. **ML results (B1–B4, F1–F2)**: We add a "Research Findings" panel in the app showing the gender bias evidence, and potentially train sex-stratified models.
3. **Max HR (C1)**: We validate or replace Gulati's formula in the code.
4. **Symptoms (D1–D3)**: We add severity weights and prevalence data to the voice screening module.
5. **Advisory (E1)**: We attach citations to every advisory message shown to patients.

The goal: every number, threshold, and claim in HeartLens can point to a specific paper.