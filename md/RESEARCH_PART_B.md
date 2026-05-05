# Research Part B + F — ML Model & Dataset Analysis Results

> Auto-generated analysis of the UCI Heart Disease dataset for HeartLens.

---

## Executive Summary

### Data Quality Critical Finding

The `HeartDiseaseTrain-Test.csv` dataset contains **723 duplicate rows out of 1025 total** (70.5%). Only **302 unique patient records** exist. All analysis below uses the deduplicated dataset to prevent data leakage and inflated metrics. The existing production model in `ml_engine.py` trains on the full 1025 rows (including duplicates), which means its reported performance is artificially inflated.

### B1 — Gender Bias in Model Performance

The **female-only model outperforms** both the mixed-sex and male-only models across all metrics (AUC: 0.937 vs 0.906 vs 0.886), suggesting women's cardiac presentations follow a distinct, learnable pattern that a dedicated model captures better.

When the mixed-sex model is tested via holdout split, its **AUC drops from 0.889 on males to 0.831 on females** — a 0.058 gap in discriminative ability. This means the mixed model is less reliable at distinguishing disease from non-disease in female patients.

### B2 — Features That Matter Differently by Sex

The most important features for predicting heart disease differ substantially between sexes:

- **`thalassemia`**: Jumps from #7 in males to **#1 in females** (importance: 0.085 → 0.155)
- **`oldpeak` (ST depression)**: #4 in males → **#2 in females** (+0.046 importance), contrary to the claim that ST depression is less useful in women
- **`vessels_colored_by_flourosopy`**: #3 in males → **#10 in females** (-0.069), the largest drop — fluoroscopy is far less informative for female diagnosis
- **`Max_heart_rate`**: **#1 in males** → #6 in females — the single most important male predictor is only moderately important for women

Atypical chest pain types predict disease at **89–97% rates in women** vs 63–78% in men, confirming that "atypical" presentations are actually typical for women.

### B3 — Microvascular Disease Signal

In the dataset, 76.4% of female disease patients and 81.5% of male disease patients had 0 vessels colored by fluoroscopy. However, the dataset's disease definition (>50% diameter stenosis) **by definition excludes INOCA/MINOCA** — conditions that disproportionately affect women. Literature shows INOCA affects up to 50% of women undergoing angiography (Bairey Merz et al., JACC 2017) and MINOCA accounts for 10–25% of MI in women vs 5–10% in men (Tamis-Holland et al., Circulation 2019).

### B4 — Dataset Is Structurally Biased Against Women

- **Sex ratio**: 68% male / 32% female (2.15:1)
- **Disease rate**: 75% for females vs 44.7% for males (selection bias — women in this 1988 dataset were likely referred only when disease was obvious)
- **Missing sex-specific features**: No hormone status, pregnancy history, preeclampsia, PCOS, or autoimmune markers
- **Outcome definition excludes microvascular disease**, which disproportionately affects women
- **Data from 1988**: Cleveland Clinic, Hungarian Institute of Cardiology, University Hospital Zurich, and VA Long Beach

### F1 — Sex Statistically Predicts Disease Outcome

Chi-square test: **χ² = 23.08, p < 0.000002**. Female sex is associated with disease with an **odds ratio of 3.72** (95% CI: 2.17–6.36). Point-biserial correlation: r = 0.284 (p < 0.000001). The relationship is highly statistically significant.

### F2 — Women With Disease Have Different Biomarker Profiles

Comparing diseased females to diseased males:
- **Cholesterol**: Women significantly higher — mean 257 vs 232 mg/dL (p = 0.005). Supports female-specific cholesterol thresholds in `biomarkers.py`.
- **Max heart rate**: Women significantly lower — mean 154 vs 162 bpm (p = 0.01). Supports using Gulati's formula over the generic 220-age.
- **Resting BP**: No significant difference (p = 0.72) between diseased men and women.
- **Oldpeak**: No significant difference (p = 0.63) between diseased men and women.

### Recommended Actions for the Codebase

1. **Deduplicate the training data** in `ml_engine.py` — the current model is trained on 70.5% duplicate data.
2. **Consider training sex-stratified models** — the female-only model outperforms the mixed model for women.
3. **Re-weight feature importance display** by sex when showing results to clinicians.
4. **Add a dataset limitations disclaimer** in the app's research panel.
5. **Explore supplementary datasets**: UK Biobank, MESA, and WISE for better female representation.

---

## Data Quality Note

- **Total rows**: 1025
- **Duplicate rows**: 723
- **Unique rows**: 302

⚠️ The dataset contains **723 duplicate rows** (70.5% of the data). All model evaluations below use the **deduplicated dataset (302 unique rows)** to avoid data leakage between train/test folds.

## B1 — Sex-Stratified Model Performance Comparison

### Cross-Validated Performance (5-Fold Stratified CV)

| Metric | Mixed-Sex Model | Male-Only Model | Female-Only Model |
|--------|----------------|-----------------|-------------------|
| ACCURACY | 0.8247 ± 0.0331 | 0.8204 ± 0.0475 | 0.9053 ± 0.0516 |
| PRECISION | 0.8352 ± 0.0548 | 0.7858 ± 0.0876 | 0.9162 ± 0.0714 |
| RECALL | 0.8536 ± 0.0728 | 0.8374 ± 0.0316 | 0.9714 ± 0.0571 |
| F1 | 0.8403 ± 0.0317 | 0.8078 ± 0.0454 | 0.9394 ± 0.0325 |
| AUC | 0.9061 ± 0.0157 | 0.8859 ± 0.0413 | 0.9367 ± 0.0521 |

### Mixed Model Tested on Sex-Specific Subsets (80/20 Holdout Split)

This trains a mixed-sex model on 80% of the data and evaluates it separately on male vs female patients from the 20% holdout test set.

- Male test samples: 43
- Female test samples: 18

| Metric | Mixed→Male | Mixed→Female |
|--------|-----------|-------------|
| ACCURACY | 0.8140 | 0.8333 |
| PRECISION | 0.8000 | 0.9167 |
| RECALL | 0.8000 | 0.8462 |
| F1 | 0.8000 | 0.8800 |
| AUC | 0.8891 | 0.8308 |

### Confusion Matrices

**Mixed-Sex (all CV folds)**:

| | Predicted 0 | Predicted 1 |
|---|------------|------------|
| Actual 0 | 109 | 29 |
| Actual 1 | 24 | 140 |

**Male-Only (all CV folds)**:

| | Predicted 0 | Predicted 1 |
|---|------------|------------|
| Actual 0 | 92 | 22 |
| Actual 1 | 15 | 77 |

**Female-Only (all CV folds)**:

| | Predicted 0 | Predicted 1 |
|---|------------|------------|
| Actual 0 | 17 | 7 |
| Actual 1 | 2 | 70 |

**Mixed Model → Female Subset**:

| | Predicted 0 | Predicted 1 |
|---|------------|------------|
| Actual 0 | 4 | 1 |
| Actual 1 | 2 | 11 |

**Mixed Model → Male Subset**:

| | Predicted 0 | Predicted 1 |
|---|------------|------------|
| Actual 0 | 19 | 4 |
| Actual 1 | 4 | 16 |

### Summary

The mixed-sex model shows an accuracy gap of **-0.0194** (0.8140 on males vs 0.8333 on females) when tested on sex-specific subsets. 
AUC is **0.0584 lower** for females, indicating reduced discriminative ability. 

The female-only model achieves an AUC of 0.9367 compared to 0.9061 for the mixed model and 0.8859 for the male-only model. The female-only model is trained on only 96 samples vs 206 for the male-only model, which limits its statistical power.

---

## B2 — Feature Importance Differences by Sex

### Male Feature Importance Ranking

| Rank | Feature | Importance |
|------|---------|-----------|
| 1 | Max_heart_rate | 0.1596 |
| 2 | chest_pain_type | 0.1300 |
| 3 | vessels_colored_by_flourosopy | 0.1225 |
| 4 | oldpeak | 0.1074 |
| 5 | cholestoral | 0.0989 |
| 6 | age | 0.0961 |
| 7 | thalassemia | 0.0847 |
| 8 | resting_blood_pressure | 0.0767 |
| 9 | slope | 0.0472 |
| 10 | exercise_induced_angina | 0.0432 |
| 11 | rest_ecg | 0.0213 |
| 12 | fasting_blood_sugar | 0.0125 |
| 13 | sex | 0.0000 |

### Female Feature Importance Ranking

| Rank | Feature | Importance |
|------|---------|-----------|
| 1 | thalassemia | 0.1550 |
| 2 | oldpeak | 0.1532 |
| 3 | age | 0.0998 |
| 4 | resting_blood_pressure | 0.0984 |
| 5 | chest_pain_type | 0.0980 |
| 6 | Max_heart_rate | 0.0850 |
| 7 | exercise_induced_angina | 0.0821 |
| 8 | slope | 0.0720 |
| 9 | cholestoral | 0.0673 |
| 10 | vessels_colored_by_flourosopy | 0.0531 |
| 11 | rest_ecg | 0.0227 |
| 12 | fasting_blood_sugar | 0.0133 |
| 13 | sex | 0.0000 |

### Key Feature Comparison (Male vs Female)

| Feature | Male Importance | Male Rank | Female Importance | Female Rank | Difference |
|---------|----------------|-----------|-------------------|-------------|------------|
| chest_pain_type | 0.1300 | #2 | 0.0980 | #5 | -0.0320 |
| vessels_colored_by_flourosopy | 0.1225 | #3 | 0.0531 | #10 | -0.0694 |
| oldpeak | 0.1074 | #4 | 0.1532 | #2 | +0.0457 |
| cholestoral | 0.0989 | #5 | 0.0673 | #9 | -0.0316 |
| resting_blood_pressure | 0.0767 | #8 | 0.0984 | #4 | +0.0218 |

### Analysis of Key Features

**chest_pain_type**:

*Male chest pain type vs target:*

| Chest Pain Type | No Disease | Disease | Disease Rate |
|----------------|-----------|---------|-------------|
| Asymptomatic | 7 | 12 | 63.2% |
| Atypical angina | 7 | 25 | 78.1% |
| Non-anginal pain | 17 | 34 | 66.7% |
| Typical angina | 83 | 21 | 20.2% |

*Female chest pain type vs target:*

| Chest Pain Type | No Disease | Disease | Disease Rate |
|----------------|-----------|---------|-------------|
| Asymptomatic | 0 | 4 | 100.0% |
| Atypical angina | 2 | 16 | 88.9% |
| Non-anginal pain | 1 | 34 | 97.1% |
| Typical angina | 21 | 18 | 46.2% |

**vessels_colored_by_flourosopy**:

*Male vessels vs target:*

| Vessels | No Disease | Disease | Disease Rate |
|---------|-----------|---------|-------------|
| Four | 1 | 3 | 75.0% |
| One | 41 | 9 | 18.0% |
| Three | 13 | 3 | 18.8% |
| Two | 23 | 2 | 8.0% |
| Zero | 36 | 75 | 67.6% |

*Female vessels vs target:*

| Vessels | No Disease | Disease | Disease Rate |
|---------|-----------|---------|-------------|
| One | 3 | 12 | 80.0% |
| Three | 4 | 0 | 0.0% |
| Two | 8 | 5 | 38.5% |
| Zero | 9 | 55 | 85.9% |

**oldpeak (ST depression)**:

| Group | Mean | Median | Std |
|-------|------|--------|-----|
| Male Healthy | 1.532 | 1.400 | 1.227 |
| Male Disease | 0.612 | 0.150 | 0.875 |
| Female Healthy | 1.842 | 1.600 | 1.608 |
| Female Disease | 0.554 | 0.250 | 0.648 |

**cholestoral**:

| Group | Mean | Median | Std |
|-------|------|--------|-----|
| Male Healthy | 246.06 | 247.50 | 45.44 |
| Male Disease | 231.60 | 229.50 | 37.64 |
| Female Healthy | 274.96 | 265.50 | 60.86 |
| Female Disease | 256.75 | 249.00 | 66.22 |

**resting_blood_pressure**:

| Group | Mean | Median | Std |
|-------|------|--------|-----|
| Male Healthy | 131.93 | 130.00 | 17.22 |
| Male Disease | 129.65 | 130.00 | 16.02 |
| Female Healthy | 146.12 | 140.00 | 21.44 |
| Female Disease | 128.74 | 130.00 | 16.54 |

---

## B3 — Microvascular Disease Signal in the Data

### Vessels = 0 in Disease Patients (target=1)

| Sex | Total Disease Patients | Vessels=0 Count | Vessels=0 Percentage |
|-----|----------------------|-----------------|---------------------|
| Male | 92 | 75 | 81.5% |
| Female | 72 | 55 | 76.4% |

**76.4%** of female heart disease patients have 0 vessels colored by fluoroscopy, compared to **81.5%** of male heart disease patients (a difference of -5.1 percentage points).

### Literature Context

- **INOCA (Ischemia with No Obstructive Coronary Arteries)**: Affects up to 50% of women undergoing coronary angiography for suspected ischemia (Bairey Merz et al., JACC 2017).
- **MINOCA (Myocardial Infarction with No Obstructive Coronary Arteries)**: Accounts for 5–6% of all MI, but is disproportionately more common in women — up to 10–25% of women with MI vs 5–10% of men (Tamis-Holland et al., Circulation 2019).
- **WISE Study (Women's Ischemia Syndrome Evaluation)**: Demonstrated that women with signs and symptoms of ischemia frequently have coronary microvascular dysfunction rather than obstructive CAD (Pepine et al., JACC 2015).

**Recommended diagnostic pathway** when a woman has cardiac symptoms but 0 blocked vessels:
1. Coronary reactivity testing (CRT) to assess endothelial and non-endothelial microvascular function.
2. Cardiac MRI with stress perfusion to detect subendocardial ischemia.
3. PET myocardial perfusion imaging to quantify coronary flow reserve (CFR < 2.0 suggests microvascular dysfunction).
4. Invasive coronary function testing with acetylcholine and adenosine provocation.

---

## B4 — UCI Dataset Limitations and Bias Assessment

### Demographic Breakdown

- **Total samples**: 302
- **Male**: 206 (68.2%)
- **Female**: 96 (31.8%)
- **Male:Female ratio**: 2.15:1
- **Male disease rate**: 44.7%
- **Female disease rate**: 75.0%

### Age Distribution by Sex

| Sex | Count | Mean Age | Std | Min | Max |
|-----|-------|----------|-----|-----|-----|
| Male | 206 | 53.8 | 8.8 | 29 | 77 |
| Female | 96 | 55.7 | 9.4 | 34 | 76 |

### Sex × Target Crosstab

| Sex | No Disease (0) | Disease (1) | Disease Rate |
|-----|---------------|-------------|-------------|
| Male | 114 | 92 | 44.7% |
| Female | 24 | 72 | 75.0% |

### Known Limitations

1. **Sex imbalance**: The dataset is ~68% male and ~32% female (2.1:1 ratio). This under-representation of women means any model trained on this data will have learned predominantly from male cardiac presentations.

2. **Age range**: The UCI dataset covers ages ~29–77 but may not adequately represent younger women with pregnancy-related or autoimmune-related cardiac disease.

3. **Feature set**: The 13 features are classic cardiac risk factors but miss sex-specific markers like hormone status, pregnancy history, preeclampsia history, PCOS, and autoimmune conditions — all of which are significant female cardiac risk factors.

4. **Symptom encoding**: The `chest_pain_type` feature uses traditional categories that may not capture the atypical presentations more common in women (jaw pain, back pain, fatigue, nausea).

5. **Outcome definition**: The binary target (disease/no-disease) is based on >50% diameter stenosis in major coronary arteries, which by definition excludes microvascular disease (INOCA/MINOCA) — a condition disproportionately affecting women.

6. **Data origin**: The original data comes from the Cleveland Clinic, Hungarian Institute of Cardiology, University Hospital Zurich, and VA Long Beach (1988). Clinical practices and patient demographics have changed significantly since then.

### Recommended Alternative/Supplementary Datasets

1. **UK Biobank** (ukbiobank.ac.uk): ~500,000 participants aged 40–69 with extensive cardiovascular phenotyping, ~55% female. Includes imaging, genetics, and longitudinal follow-up.

2. **MESA (Multi-Ethnic Study of Atherosclerosis)** (mesa-nhlbi.org): ~6,800 participants, ~53% female, multi-ethnic (White, Black, Hispanic, Chinese-American). Includes subclinical atherosclerosis measures and cardiac MRI.

3. **WISE Dataset (Women's Ischemia Syndrome Evaluation)**: NHLBI-sponsored study specifically designed to study ischemic heart disease in women, with focus on microvascular disease. Available through BioLINCC (biolincc.nhlbi.nih.gov).

---

## F1 — Chi-Square Test: Sex vs Heart Disease Outcome

### Contingency Table

| Sex | No Disease (0) | Disease (1) |
|-----|---------------|-------------|
| Female | 24 | 72 |
| Male | 114 | 92 |

### Test Results

| Test | Statistic | P-value | Interpretation |
|------|-----------|---------|----------------|
| Chi-Square | χ² = 23.0839 | p = 0.000002 | Significant (p < 0.05) |
| Point-Biserial r | r = 0.2836 | p = 0.000001 | Significant (p < 0.05) |
| Odds Ratio | OR = 3.7174 | 95% CI [2.1718, 6.3630] | Female sex associated with disease |

- **Degrees of freedom**: 1
- The relationship between sex and heart disease outcome is **highly statistically significant** (p < 0.001).

---

## F2 — Distribution Analysis by Sex

### resting_blood_pressure

| Group | N | Mean | Median | Std Dev |
|-------|---|------|--------|---------|
| Healthy Male | 114 | 131.93 | 130.00 | 17.22 |
| Diseased Male | 92 | 129.65 | 130.00 | 16.02 |
| Healthy Female | 24 | 146.12 | 140.00 | 21.44 |
| Diseased Female | 72 | 128.74 | 130.00 | 16.54 |

**Diseased Female vs Diseased Male comparison:**
- Welch's t-test: t = 0.3569, p = 0.721656 (Significant: No)
- Mann-Whitney U: U = 3363.5, p = 0.865319 (Significant: No)

### cholestoral

| Group | N | Mean | Median | Std Dev |
|-------|---|------|--------|---------|
| Healthy Male | 114 | 246.06 | 247.50 | 45.44 |
| Diseased Male | 92 | 231.60 | 229.50 | 37.64 |
| Healthy Female | 24 | 274.96 | 265.50 | 60.86 |
| Diseased Female | 72 | 256.75 | 249.00 | 66.22 |

**Diseased Female vs Diseased Male comparison:**
- Welch's t-test: t = -2.8795, p = 0.004818 (Significant: Yes)
- Mann-Whitney U: U = 2552.5, p = 0.011898 (Significant: Yes)

### Max_heart_rate

| Group | N | Mean | Median | Std Dev |
|-------|---|------|--------|---------|
| Healthy Male | 114 | 138.40 | 141.00 | 23.08 |
| Diseased Male | 92 | 161.78 | 163.00 | 18.56 |
| Healthy Female | 24 | 142.42 | 145.50 | 20.26 |
| Diseased Female | 72 | 154.03 | 159.00 | 19.25 |

**Diseased Female vs Diseased Male comparison:**
- Welch's t-test: t = 2.6007, p = 0.010234 (Significant: Yes)
- Mann-Whitney U: U = 4043.5, p = 0.015397 (Significant: Yes)

### oldpeak

| Group | N | Mean | Median | Std Dev |
|-------|---|------|--------|---------|
| Healthy Male | 114 | 1.53 | 1.40 | 1.23 |
| Diseased Male | 92 | 0.61 | 0.15 | 0.88 |
| Healthy Female | 24 | 1.84 | 1.60 | 1.61 |
| Diseased Female | 72 | 0.55 | 0.25 | 0.65 |

**Diseased Female vs Diseased Male comparison:**
- Welch's t-test: t = 0.4858, p = 0.627776 (Significant: No)
- Mann-Whitney U: U = 3220.5, p = 0.752063 (Significant: No)

### Summary of Distribution Findings

**Significantly different** between diseased males and diseased females: cholestoral, Max_heart_rate

**Not significantly different**: resting_blood_pressure, oldpeak

These results indicate whether women with heart disease present with different biomarker profiles than men with heart disease, which has direct implications for sex-specific diagnostic thresholds.
