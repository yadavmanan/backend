# Risk Assessment Flow

This document explains how risk assessment currently works in the application, and how the biomarker system is structured and planned.

## 1. High-Level Design

The risk assessment is split into two separate layers:

1. ML prediction layer
   - Produces the main cardiac risk score.
   - Uses a trained Random Forest model.
   - Depends on a fixed set of structured input fields.

2. Biomarker interpretation layer
   - Does not directly generate the risk score.
   - Interprets each biomarker using reference zones.
   - Compares male and female thresholds.
   - Highlights diagnostic gaps and sex-specific risk differences.

This separation is important:
- the ML model answers: `How risky does this patient look overall based on the trained dataset?`
- the biomarker layer answers: `Which individual measurements are concerning, and where do sex-specific interpretations differ?`

## 2. Main Backend Flow

The main risk assembly happens in:
- [backend/app.py](/c:/Users/Z0052TRF/Desktop/close/backend/app.py)
- [backend/ml_engine.py](/c:/Users/Z0052TRF/Desktop/close/backend/ml_engine.py)
- [backend/biomarkers.py](/c:/Users/Z0052TRF/Desktop/close/backend/biomarkers.py)

The backend route for assessment is:
- `POST /api/risk/calculate`

That route validates the payload using `HeartAssessmentRequest`, then calls `_build_analysis_payload()`.

`_build_analysis_payload()` combines three outputs:
1. `predict_risk(...)`
2. `analyze_reference_ranges(...)`
3. `get_distribution_data(...)`

For female patients it also adds:
- `get_women_advisory(...)`

The final response returned to the frontend contains:
- `risk_score`
- `risk_level`
- `risk_color`
- `feature_importance`
- `reference_ranges`
- `distribution_data`
- `women_advisory`
- `gap_count`
- `total_biomarkers`

## 3. ML Risk Score: How It Works

The ML model is implemented in [backend/ml_engine.py](/c:/Users/Z0052TRF/Desktop/close/backend/ml_engine.py).

### 3.1 Training Data

The model is trained from:
- `backend/data/HeartDiseaseTrain-Test.csv`

This dataset contains a `target` column:
- `0` = no disease
- `1` = disease

The rest of the columns are used as model features.

### 3.2 Feature Preparation

The model uses both numeric and categorical inputs.

Categorical fields are listed in `CAT_COLS`:
- `sex`
- `chest_pain_type`
- `fasting_blood_sugar`
- `rest_ecg`
- `exercise_induced_angina`
- `slope`
- `vessels_colored_by_flourosopy`
- `thalassemia`

These are encoded using `LabelEncoder`.

Numeric fields are passed through directly from the dataset and request payload.

### 3.3 Model Type

The model is:
- `RandomForestClassifier`

Current configuration:
- `n_estimators=200`
- `random_state=42`
- `n_jobs=-1`

The model is trained once when the backend starts.

### 3.4 Inference

When a patient payload is submitted:
1. categorical values are encoded
2. a one-row DataFrame is created
3. the DataFrame is aligned to the training feature order
4. `predict_proba()` is used to get disease probability

That probability is converted into:
- `risk_score` = percentage from 0 to 100

### 3.5 Risk Buckets

The score is then mapped into a display bucket:
- below `30` → `Low Risk`
- `30` to below `60` → `Moderate Risk`
- `60` and above → `High Risk`

Colors currently used:
- low risk: green
- moderate risk: orange
- high risk: red

### 3.6 Feature Importance

The backend also returns sorted feature importance values from the Random Forest model.

This allows the frontend to show:
- which inputs influenced the model most
- how the patient risk profile is being driven by the trained dataset

Important note:
- feature importance here is model-level importance from the trained forest, not patient-specific local explanation like SHAP

## 4. Biomarker Interpretation: How It Works

The biomarker logic is implemented in [backend/biomarkers.py](/c:/Users/Z0052TRF/Desktop/close/backend/biomarkers.py).

This layer is rule-based, not ML-based.

Each biomarker definition contains:
- `label`
- `unit`
- `chart_range`
- `male_zones`
- `female_zones`
- `male_cite`
- `female_cite`
- `gap`

This design makes each biomarker more than a raw value. It becomes a structured clinical interpretation object.

## 5. Current Biomarker Groups

The biomarker system is currently planned in two groups.

### 5.1 Core biomarkers

These are always part of the main reference-range analysis:
- `resting_blood_pressure`
- `cholestoral`
- `oldpeak`
- `Max_heart_rate`

These are treated as the core cardiac interpretation set because they are already central to the trained risk pipeline and available in the base assessment flow.

### 5.2 Extended biomarkers

These are optional and only analyzed when values are present:
- `hdl`
- `ldl`
- `triglycerides`
- `hba1c`
- `hs_crp`
- `bmi`
- `waist_circumference`
- `resting_pulse_rate`

These are already implemented as `EXTENDED_BIOMARKERS`.

If a field is missing in the patient payload, it is skipped and not included in the biomarker output.

## 6. How Each Biomarker Is Classified

For each biomarker, the backend uses zone-based classification.

Example structure:
- lower bound
- upper bound
- status label
- display color

A helper function called `classify()` checks the patient value against the configured zones.

The same patient value is classified twice:
1. once against `male_zones`
2. once against `female_zones`

The result object stores both interpretations.

Example output per biomarker includes:
- `male_status`
- `male_color`
- `female_status`
- `female_color`
- `gap`
- `gap_explanation`

A gap is flagged when:
- the male and female interpretation labels are different

This is the main mechanism the app uses to show that a biomarker may look acceptable under generic or male-calibrated interpretation, but concerning under female-specific interpretation.

## 7. Why Max Heart Rate Is Handled Differently

`Max_heart_rate` is not classified with static zones like the other biomarkers.

Instead, it uses predicted exercise targets based on age.

Current formulas:
- male predicted max HR = `220 - age`
- female predicted max HR = `206 - (0.88 × age)`

Then the backend computes the 85% stress-test threshold for each.

Status assignment:
- if observed max heart rate is greater than or equal to the 85% threshold → `Adequate`
- otherwise → `Inadequate`

This means max heart rate is planned as a sex-specific stress-test adequacy check rather than a fixed threshold biomarker.

## 8. Women-Specific Advisory Layer

If the patient sex is `Female`, the backend adds a women-specific advisory list.

This is generated by `get_women_advisory()`.

Current advisory content includes:
- atypical symptoms may still be cardiac
- Gulati-based max heart rate context
- possibility of microvascular disease even when large-vessel findings look normal
- earlier action may be needed at lower blood pressure and cholesterol values
- heart rate should be interpreted with ECG and symptom context

This is not part of the ML score itself.
It is an interpretation and guidance layer built on top of the result.

## 9. Distribution Data for Charts

The backend also prepares chart data using `get_distribution_data()`.

This compares healthy vs disease values from the training dataset for the selected sex.

Currently chart distributions are returned for:
- `resting_blood_pressure`
- `cholestoral`
- `Max_heart_rate`
- `oldpeak`

This is used to support visual comparison in the frontend.

So the current design has three analytical outputs working together:
- ML risk score
- biomarker rule interpretation
- dataset comparison visualization

## 10. How the Biomarker System Is Planned Structurally

The biomarker system is designed to be extensible.

A new biomarker can be added by defining:
- label and unit
- chart range
- male and female zone thresholds
- supporting citations
- diagnostic gap explanation

Then the analysis layer can include it automatically if the patient payload contains that field.

This means the planning model is:
1. define the biomarker metadata
2. define sex-specific zones
3. provide evidence text and explanation
4. pass the patient value into `analyze_reference_ranges()`
5. render the output in the frontend

That structure is already visible in `EXTENDED_BIOMARKERS`.

## 11. What Is Planned vs What Is Already Active

### Already active

Risk assessment currently uses:
- Random Forest risk scoring
- core biomarker analysis
- extended biomarker analysis when values exist
- female-specific interpretation zones
- diagnostic gap detection
- women-specific advisory text
- sex-specific max-heart-rate target logic

### Planned by current structure

The code structure supports adding more biomarkers in the same pattern, especially:
- inflammatory markers
- renal markers
- endocrine markers
- menopause-relevant metabolic markers
- symptom-linked biomarkers for female cardiac under-detection

The current architecture suggests the intended roadmap is not to overload the ML model immediately, but to expand interpretation depth through the biomarker rules layer.

That is a good separation because:
- ML features require retraining and dataset support
- biomarker rules can be expanded faster and more safely
- sex-specific reasoning can evolve without destabilizing the model

## 12. Current Strength of the Design

The current design has a clear and useful split:

1. The ML model gives a single operational risk estimate.
2. The biomarker layer explains where that risk may be hiding or underestimated.
3. The female-specific threshold logic addresses the exact problem the product is trying to solve: under-recognition of cardiovascular risk in women.

In practical terms, the system is not just asking:
- `Is this patient high risk?`

It is also asking:
- `Would this patient be interpreted differently if sex-specific thresholds were respected?`

That second question is the key planning idea behind the biomarker layer.

## 13. Current Limitations

A few implementation limits are worth noting.

1. The ML model is still only as good as the training CSV and its feature set.
2. Extended biomarkers currently enrich interpretation, but they do not directly change the ML score unless they are included in the training features.
3. Feature importance is global model importance, not patient-level explanation.
4. Some extended fields are interpreted clinically but may not yet be fully surfaced everywhere in the frontend.
5. Sex-specific thresholds are manually encoded rules, so they depend on the quality of the configured ranges and citations.

## 14. Practical End-to-End Summary

Today, risk assessment works like this:
1. The frontend sends a structured patient payload.
2. The backend runs the Random Forest model to estimate disease probability.
3. That probability becomes a risk score and bucket.
4. The backend separately interprets biomarkers using male and female threshold zones.
5. Any mismatch between male and female interpretation is flagged as a diagnostic gap.
6. If the patient is female, additional women-specific advisory text is added.
7. The frontend receives a combined result containing score, explanations, and biomarker evidence.

## 15. Main Files Involved

- [backend/app.py](/c:/Users/Z0052TRF/Desktop/close/backend/app.py)
- [backend/ml_engine.py](/c:/Users/Z0052TRF/Desktop/close/backend/ml_engine.py)
- [backend/biomarkers.py](/c:/Users/Z0052TRF/Desktop/close/backend/biomarkers.py)
- [backend/data/HeartDiseaseTrain-Test.csv](/c:/Users/Z0052TRF/Desktop/close/backend/data/HeartDiseaseTrain-Test.csv)
