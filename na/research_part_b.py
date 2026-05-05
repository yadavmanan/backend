"""
Research Part B + F — ML Risk Model Analysis & Dataset Statistics
Covers tasks B1, B2, B3, B4, F1, F2 from RESEARCH_ROADMAP.md
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder

DATA_PATH = Path(__file__).resolve().parents[1] / ".." / "data" / "HeartDiseaseTrain-Test.csv"

CAT_COLS = [
    "sex",
    "chest_pain_type",
    "fasting_blood_sugar",
    "rest_ecg",
    "exercise_induced_angina",
    "slope",
    "vessels_colored_by_flourosopy",
    "thalassemia",
]

OUTPUT_PATH = Path(__file__).resolve().parent / ".." / "md" / "RESEARCH_PART_B.md"


def load_data():
    df = pd.read_csv(DATA_PATH)
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].astype(str).str.strip()
    return df


def encode_df(df):
    df_enc = df.copy()
    encoders = {}
    for col in CAT_COLS:
        le = LabelEncoder()
        df_enc[col] = le.fit_transform(df_enc[col].astype(str))
        encoders[col] = le
    return df_enc, encoders


def evaluate_model_cv(df, label, n_splits=5):
    """Train and evaluate a model using stratified k-fold cross-validation."""
    df_enc, _ = encode_df(df)
    X = df_enc.drop("target", axis=1)
    y = df_enc["target"]

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    metrics = {"accuracy": [], "precision": [], "recall": [], "f1": [], "auc": []}
    all_y_true = []
    all_y_pred = []

    for train_idx, test_idx in skf.split(X, y):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        metrics["accuracy"].append(accuracy_score(y_test, y_pred))
        metrics["precision"].append(precision_score(y_test, y_pred, zero_division=0))
        metrics["recall"].append(recall_score(y_test, y_pred, zero_division=0))
        metrics["f1"].append(f1_score(y_test, y_pred, zero_division=0))
        metrics["auc"].append(roc_auc_score(y_test, y_prob))

        all_y_true.extend(y_test.tolist())
        all_y_pred.extend(y_pred.tolist())

    avg = {k: np.mean(v) for k, v in metrics.items()}
    std = {k: np.std(v) for k, v in metrics.items()}
    cm = confusion_matrix(all_y_true, all_y_pred)
    return avg, std, cm


def evaluate_mixed_on_subset(df_all, subset_sex, label):
    """Train mixed model on 80% holdout, test on subset filtered by sex from the 20% test set."""
    from sklearn.model_selection import train_test_split

    df_enc, encoders = encode_df(df_all)
    X = df_enc.drop("target", axis=1)
    y = df_enc["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # Get the original sex column for the test set rows
    test_indices = X_test.index
    sex_col = df_all.loc[test_indices, "sex"]

    # Encode the sex value to match the encoded dataframe
    sex_encoded = encoders["sex"].transform([subset_sex])[0]
    mask = X_test["sex"] == sex_encoded

    X_sub = X_test[mask]
    y_sub = y_test[mask]

    if len(y_sub) == 0:
        return {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0, "auc": 0}, np.array([[0, 0], [0, 0]]), 0

    y_pred = model.predict(X_sub)
    y_prob = model.predict_proba(X_sub)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_sub, y_pred),
        "precision": precision_score(y_sub, y_pred, zero_division=0),
        "recall": recall_score(y_sub, y_pred, zero_division=0),
        "f1": f1_score(y_sub, y_pred, zero_division=0),
        "auc": roc_auc_score(y_sub, y_prob) if len(set(y_sub)) > 1 else float("nan"),
    }
    cm = confusion_matrix(y_sub, y_pred)
    return metrics, cm, len(y_sub)


def get_feature_importance_by_sex(df):
    """Train separate models for male/female and return feature importances."""
    results = {}
    for sex_val in ["Male", "Female"]:
        df_sex = df[df["sex"] == sex_val].copy()
        df_enc, _ = encode_df(df_sex)
        X = df_enc.drop("target", axis=1)
        y = df_enc["target"]

        model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
        model.fit(X, y)

        importance = sorted(
            zip(X.columns, model.feature_importances_),
            key=lambda x: x[1],
            reverse=True,
        )
        results[sex_val] = importance
    return results


def microvascular_analysis(df):
    """B3: Analyze vessels_colored_by_flourosopy = 0 in disease patients by sex."""
    disease_df = df[df["target"] == 1]

    # The column uses text values like "Zero", "One", etc.
    zero_labels = {"0", "Zero", "zero"}

    results = {}
    for sex_val in ["Male", "Female"]:
        sex_disease = disease_df[disease_df["sex"] == sex_val]
        zero_vessels = sex_disease[sex_disease["vessels_colored_by_flourosopy"].astype(str).isin(zero_labels)]
        total = len(sex_disease)
        zero_count = len(zero_vessels)
        pct = (zero_count / total * 100) if total > 0 else 0
        results[sex_val] = {"total_disease": total, "zero_vessels": zero_count, "percentage": pct}
    return results


def dataset_demographics(df):
    """B4: Full demographic breakdown."""
    total = len(df)
    sex_counts = df["sex"].value_counts()
    sex_target = df.groupby(["sex", "target"]).size().unstack(fill_value=0)

    age_stats = df.groupby("sex")["age"].describe()

    return {
        "total": total,
        "sex_counts": sex_counts,
        "sex_target": sex_target,
        "age_stats": age_stats,
        "male_pct": sex_counts.get("Male", 0) / total * 100,
        "female_pct": sex_counts.get("Female", 0) / total * 100,
        "male_disease_rate": sex_target.loc["Male", 1] / sex_counts["Male"] * 100 if "Male" in sex_target.index else 0,
        "female_disease_rate": sex_target.loc["Female", 1] / sex_counts["Female"] * 100 if "Female" in sex_target.index else 0,
    }


def chi_square_test(df):
    """F1: Chi-square test of independence: sex × target."""
    contingency = pd.crosstab(df["sex"], df["target"])
    chi2, p, dof, expected = stats.chi2_contingency(contingency)

    # Point-biserial correlation
    sex_numeric = (df["sex"] == "Female").astype(int)
    rpb, rpb_p = stats.pointbiserialr(sex_numeric, df["target"])

    # Odds ratio
    ct = contingency.values
    odds_ratio = (ct[0][1] * ct[1][0]) / (ct[0][0] * ct[1][1]) if ct[0][0] * ct[1][1] != 0 else float("inf")
    # 95% CI for odds ratio (log method)
    log_or = np.log(odds_ratio)
    se_log_or = np.sqrt(1 / ct[0][0] + 1 / ct[0][1] + 1 / ct[1][0] + 1 / ct[1][1])
    ci_lower = np.exp(log_or - 1.96 * se_log_or)
    ci_upper = np.exp(log_or + 1.96 * se_log_or)

    return {
        "contingency": contingency,
        "chi2": chi2,
        "p_value": p,
        "dof": dof,
        "expected": expected,
        "rpb": rpb,
        "rpb_p": rpb_p,
        "odds_ratio": odds_ratio,
        "or_ci_lower": ci_lower,
        "or_ci_upper": ci_upper,
    }


def distribution_analysis(df):
    """F2: Distribution analysis by sex for 4 key features."""
    features = ["resting_blood_pressure", "cholestoral", "Max_heart_rate", "oldpeak"]
    groups = {
        "Healthy Male": df[(df["sex"] == "Male") & (df["target"] == 0)],
        "Diseased Male": df[(df["sex"] == "Male") & (df["target"] == 1)],
        "Healthy Female": df[(df["sex"] == "Female") & (df["target"] == 0)],
        "Diseased Female": df[(df["sex"] == "Female") & (df["target"] == 1)],
    }

    results = {}
    for feat in features:
        feat_data = {}
        for grp_name, grp_df in groups.items():
            vals = grp_df[feat].dropna()
            feat_data[grp_name] = {
                "n": len(vals),
                "mean": vals.mean(),
                "median": vals.median(),
                "std": vals.std(),
            }
        # Statistical tests: diseased female vs diseased male
        dm = groups["Diseased Male"][feat].dropna()
        df_f = groups["Diseased Female"][feat].dropna()
        t_stat, t_p = stats.ttest_ind(dm, df_f, equal_var=False)
        u_stat, u_p = stats.mannwhitneyu(dm, df_f, alternative="two-sided")

        feat_data["tests"] = {
            "t_stat": t_stat, "t_p": t_p,
            "u_stat": u_stat, "u_p": u_p,
        }
        results[feat] = feat_data
    return results


def generate_report(df):
    """Generate the full Part B + F research report."""
    lines = []
    lines.append("# Research Part B + F — ML Model & Dataset Analysis Results\n")
    lines.append("> Auto-generated analysis of the UCI Heart Disease dataset for HeartLens.\n")
    lines.append("---\n")

    # Check for duplicates
    n_dupes = df.duplicated().sum()
    n_total = len(df)
    df_dedup = df.drop_duplicates().reset_index(drop=True)
    n_unique = len(df_dedup)

    lines.append("## Data Quality Note\n")
    lines.append(f"- **Total rows**: {n_total}")
    lines.append(f"- **Duplicate rows**: {n_dupes}")
    lines.append(f"- **Unique rows**: {n_unique}")
    lines.append(
        f"\n⚠️ The dataset contains **{n_dupes} duplicate rows** ({n_dupes/n_total*100:.1f}% of the data). "
        f"All model evaluations below use the **deduplicated dataset ({n_unique} unique rows)** "
        f"to avoid data leakage between train/test folds.\n"
    )

    # Use deduplicated data for all analysis
    df = df_dedup

    # =========================================================================
    # B1: Sex-Stratified Model Performance
    # =========================================================================
    lines.append("## B1 — Sex-Stratified Model Performance Comparison\n")

    df_male = df[df["sex"] == "Male"].copy()
    df_female = df[df["sex"] == "Female"].copy()

    print("Training mixed-sex model (5-fold CV)...")
    mixed_avg, mixed_std, mixed_cm = evaluate_model_cv(df, "Mixed")

    print("Training male-only model (5-fold CV)...")
    male_avg, male_std, male_cm = evaluate_model_cv(df_male, "Male-Only")

    print("Training female-only model (5-fold CV)...")
    female_avg, female_std, female_cm = evaluate_model_cv(df_female, "Female-Only")

    print("Testing mixed model on female-only data (holdout split)...")
    mixed_on_female, mixed_on_female_cm, n_test_f = evaluate_mixed_on_subset(df, "Female", "Mixed→Female")

    print("Testing mixed model on male-only data (holdout split)...")
    mixed_on_male, mixed_on_male_cm, n_test_m = evaluate_mixed_on_subset(df, "Male", "Mixed→Male")

    lines.append("### Cross-Validated Performance (5-Fold Stratified CV)\n")
    lines.append("| Metric | Mixed-Sex Model | Male-Only Model | Female-Only Model |")
    lines.append("|--------|----------------|-----------------|-------------------|")
    for m in ["accuracy", "precision", "recall", "f1", "auc"]:
        lines.append(
            f"| {m.upper()} | {mixed_avg[m]:.4f} ± {mixed_std[m]:.4f} "
            f"| {male_avg[m]:.4f} ± {male_std[m]:.4f} "
            f"| {female_avg[m]:.4f} ± {female_std[m]:.4f} |"
        )
    lines.append("")

    lines.append("### Mixed Model Tested on Sex-Specific Subsets (80/20 Holdout Split)\n")
    lines.append("This trains a mixed-sex model on 80% of the data and evaluates it separately on male vs female patients from the 20% holdout test set.\n")
    lines.append(f"- Male test samples: {n_test_m}")
    lines.append(f"- Female test samples: {n_test_f}\n")
    lines.append("| Metric | Mixed→Male | Mixed→Female |")
    lines.append("|--------|-----------|-------------|")
    for m in ["accuracy", "precision", "recall", "f1", "auc"]:
        lines.append(f"| {m.upper()} | {mixed_on_male[m]:.4f} | {mixed_on_female[m]:.4f} |")
    lines.append("")

    lines.append("### Confusion Matrices\n")
    for label, cm in [
        ("Mixed-Sex (all CV folds)", mixed_cm),
        ("Male-Only (all CV folds)", male_cm),
        ("Female-Only (all CV folds)", female_cm),
        ("Mixed Model → Female Subset", mixed_on_female_cm),
        ("Mixed Model → Male Subset", mixed_on_male_cm),
    ]:
        lines.append(f"**{label}**:\n")
        lines.append("| | Predicted 0 | Predicted 1 |")
        lines.append("|---|------------|------------|")
        lines.append(f"| Actual 0 | {cm[0][0]} | {cm[0][1]} |")
        lines.append(f"| Actual 1 | {cm[1][0]} | {cm[1][1]} |")
        lines.append("")

    lines.append("### Summary\n")
    perf_drop = mixed_on_male["accuracy"] - mixed_on_female["accuracy"]
    lines.append(
        f"The mixed-sex model shows an accuracy gap of **{perf_drop:.4f}** "
        f"({mixed_on_male['accuracy']:.4f} on males vs {mixed_on_female['accuracy']:.4f} on females) "
        f"when tested on sex-specific subsets. "
    )
    if mixed_on_female["recall"] < mixed_on_male["recall"]:
        recall_gap = mixed_on_male["recall"] - mixed_on_female["recall"]
        lines.append(
            f"Critically, **recall drops by {recall_gap:.4f}** for female patients, "
            f"meaning the mixed model misses more true positive cases in women. "
        )
    if mixed_on_female["auc"] < mixed_on_male["auc"]:
        auc_gap = mixed_on_male["auc"] - mixed_on_female["auc"]
        lines.append(
            f"AUC is **{auc_gap:.4f} lower** for females, indicating reduced discriminative ability. "
        )
    lines.append(
        f"\nThe female-only model achieves an AUC of {female_avg['auc']:.4f} "
        f"compared to {mixed_avg['auc']:.4f} for the mixed model and "
        f"{male_avg['auc']:.4f} for the male-only model. "
        f"The female-only model is trained on only {len(df_female)} samples vs "
        f"{len(df_male)} for the male-only model, which limits its statistical power.\n"
    )

    lines.append("---\n")

    # =========================================================================
    # B2: Feature Importance by Sex
    # =========================================================================
    lines.append("## B2 — Feature Importance Differences by Sex\n")
    print("Computing sex-stratified feature importances...")
    fi = get_feature_importance_by_sex(df)

    lines.append("### Male Feature Importance Ranking\n")
    lines.append("| Rank | Feature | Importance |")
    lines.append("|------|---------|-----------|")
    for i, (feat, imp) in enumerate(fi["Male"], 1):
        lines.append(f"| {i} | {feat} | {imp:.4f} |")
    lines.append("")

    lines.append("### Female Feature Importance Ranking\n")
    lines.append("| Rank | Feature | Importance |")
    lines.append("|------|---------|-----------|")
    for i, (feat, imp) in enumerate(fi["Female"], 1):
        lines.append(f"| {i} | {feat} | {imp:.4f} |")
    lines.append("")

    # Side-by-side comparison for the 4 key features
    key_features = ["chest_pain_type", "vessels_colored_by_flourosopy", "oldpeak", "cholestoral", "resting_blood_pressure"]
    male_dict = dict(fi["Male"])
    female_dict = dict(fi["Female"])

    lines.append("### Key Feature Comparison (Male vs Female)\n")
    lines.append("| Feature | Male Importance | Male Rank | Female Importance | Female Rank | Difference |")
    lines.append("|---------|----------------|-----------|-------------------|-------------|------------|")

    male_ranked = {feat: rank for rank, (feat, _) in enumerate(fi["Male"], 1)}
    female_ranked = {feat: rank for rank, (feat, _) in enumerate(fi["Female"], 1)}

    for feat in key_features:
        m_imp = male_dict.get(feat, 0)
        f_imp = female_dict.get(feat, 0)
        m_rank = male_ranked.get(feat, "N/A")
        f_rank = female_ranked.get(feat, "N/A")
        diff = f_imp - m_imp
        lines.append(f"| {feat} | {m_imp:.4f} | #{m_rank} | {f_imp:.4f} | #{f_rank} | {diff:+.4f} |")
    lines.append("")

    lines.append("### Analysis of Key Features\n")

    # chest_pain_type analysis
    lines.append("**chest_pain_type**:")
    for sex_val in ["Male", "Female"]:
        sex_df = df[df["sex"] == sex_val]
        ct = pd.crosstab(sex_df["chest_pain_type"], sex_df["target"])
        lines.append(f"\n*{sex_val} chest pain type vs target:*\n")
        lines.append("| Chest Pain Type | No Disease | Disease | Disease Rate |")
        lines.append("|----------------|-----------|---------|-------------|")
        for cpt in ct.index:
            no_d = ct.loc[cpt, 0] if 0 in ct.columns else 0
            d = ct.loc[cpt, 1] if 1 in ct.columns else 0
            rate = d / (no_d + d) * 100 if (no_d + d) > 0 else 0
            lines.append(f"| {cpt} | {no_d} | {d} | {rate:.1f}% |")
    lines.append("")

    # vessels analysis
    lines.append("**vessels_colored_by_flourosopy**:")
    for sex_val in ["Male", "Female"]:
        sex_df = df[df["sex"] == sex_val]
        ct = pd.crosstab(sex_df["vessels_colored_by_flourosopy"], sex_df["target"])
        lines.append(f"\n*{sex_val} vessels vs target:*\n")
        lines.append("| Vessels | No Disease | Disease | Disease Rate |")
        lines.append("|---------|-----------|---------|-------------|")
        for v in sorted(ct.index, key=str):
            no_d = ct.loc[v, 0] if 0 in ct.columns else 0
            d = ct.loc[v, 1] if 1 in ct.columns else 0
            rate = d / (no_d + d) * 100 if (no_d + d) > 0 else 0
            lines.append(f"| {v} | {no_d} | {d} | {rate:.1f}% |")
    lines.append("")

    # oldpeak analysis
    lines.append("**oldpeak (ST depression)**:\n")
    lines.append("| Group | Mean | Median | Std |")
    lines.append("|-------|------|--------|-----|")
    for sex_val in ["Male", "Female"]:
        for target_val, target_label in [(0, "Healthy"), (1, "Disease")]:
            vals = df[(df["sex"] == sex_val) & (df["target"] == target_val)]["oldpeak"]
            lines.append(f"| {sex_val} {target_label} | {vals.mean():.3f} | {vals.median():.3f} | {vals.std():.3f} |")
    lines.append("")

    # cholesterol analysis
    lines.append("**cholestoral**:\n")
    lines.append("| Group | Mean | Median | Std |")
    lines.append("|-------|------|--------|-----|")
    for sex_val in ["Male", "Female"]:
        for target_val, target_label in [(0, "Healthy"), (1, "Disease")]:
            vals = df[(df["sex"] == sex_val) & (df["target"] == target_val)]["cholestoral"]
            lines.append(f"| {sex_val} {target_label} | {vals.mean():.2f} | {vals.median():.2f} | {vals.std():.2f} |")
    lines.append("")

    # resting_blood_pressure analysis
    lines.append("**resting_blood_pressure**:\n")
    lines.append("| Group | Mean | Median | Std |")
    lines.append("|-------|------|--------|-----|")
    for sex_val in ["Male", "Female"]:
        for target_val, target_label in [(0, "Healthy"), (1, "Disease")]:
            vals = df[(df["sex"] == sex_val) & (df["target"] == target_val)]["resting_blood_pressure"]
            lines.append(f"| {sex_val} {target_label} | {vals.mean():.2f} | {vals.median():.2f} | {vals.std():.2f} |")
    lines.append("")

    lines.append("---\n")

    # =========================================================================
    # B3: Microvascular Disease Signal
    # =========================================================================
    lines.append("## B3 — Microvascular Disease Signal in the Data\n")
    print("Analyzing microvascular disease signal...")
    mv = microvascular_analysis(df)

    lines.append("### Vessels = 0 in Disease Patients (target=1)\n")
    lines.append("| Sex | Total Disease Patients | Vessels=0 Count | Vessels=0 Percentage |")
    lines.append("|-----|----------------------|-----------------|---------------------|")
    for sex_val in ["Male", "Female"]:
        d = mv[sex_val]
        lines.append(f"| {sex_val} | {d['total_disease']} | {d['zero_vessels']} | {d['percentage']:.1f}% |")
    lines.append("")

    pct_diff = mv["Female"]["percentage"] - mv["Male"]["percentage"]
    lines.append(
        f"**{mv['Female']['percentage']:.1f}%** of female heart disease patients have 0 vessels colored by fluoroscopy, "
        f"compared to **{mv['Male']['percentage']:.1f}%** of male heart disease patients "
        f"(a difference of {pct_diff:+.1f} percentage points).\n"
    )

    if mv["Female"]["percentage"] > mv["Male"]["percentage"]:
        lines.append(
            "This supports the hypothesis that women with heart disease are more likely to have "
            "non-obstructive coronary artery disease (INOCA/MINOCA), where major epicardial vessels "
            "appear clear but microvascular dysfunction is present.\n"
        )

    lines.append("### Literature Context\n")
    lines.append(
        "- **INOCA (Ischemia with No Obstructive Coronary Arteries)**: Affects up to 50% of women undergoing "
        "coronary angiography for suspected ischemia (Bairey Merz et al., JACC 2017).\n"
        "- **MINOCA (Myocardial Infarction with No Obstructive Coronary Arteries)**: Accounts for 5–6% of all MI, "
        "but is disproportionately more common in women — up to 10–25% of women with MI vs 5–10% of men "
        "(Tamis-Holland et al., Circulation 2019).\n"
        "- **WISE Study (Women's Ischemia Syndrome Evaluation)**: Demonstrated that women with signs and symptoms "
        "of ischemia frequently have coronary microvascular dysfunction rather than obstructive CAD "
        "(Pepine et al., JACC 2015).\n"
    )
    lines.append(
        "**Recommended diagnostic pathway** when a woman has cardiac symptoms but 0 blocked vessels:\n"
        "1. Coronary reactivity testing (CRT) to assess endothelial and non-endothelial microvascular function.\n"
        "2. Cardiac MRI with stress perfusion to detect subendocardial ischemia.\n"
        "3. PET myocardial perfusion imaging to quantify coronary flow reserve (CFR < 2.0 suggests microvascular dysfunction).\n"
        "4. Invasive coronary function testing with acetylcholine and adenosine provocation.\n"
    )

    lines.append("---\n")

    # =========================================================================
    # B4: Dataset Limitations and Bias
    # =========================================================================
    lines.append("## B4 — UCI Dataset Limitations and Bias Assessment\n")
    print("Analyzing dataset demographics...")
    demo = dataset_demographics(df)

    lines.append("### Demographic Breakdown\n")
    lines.append(f"- **Total samples**: {demo['total']}")
    lines.append(f"- **Male**: {demo['sex_counts']['Male']} ({demo['male_pct']:.1f}%)")
    lines.append(f"- **Female**: {demo['sex_counts']['Female']} ({demo['female_pct']:.1f}%)")
    lines.append(f"- **Male:Female ratio**: {demo['sex_counts']['Male'] / demo['sex_counts']['Female']:.2f}:1")
    lines.append(f"- **Male disease rate**: {demo['male_disease_rate']:.1f}%")
    lines.append(f"- **Female disease rate**: {demo['female_disease_rate']:.1f}%\n")

    lines.append("### Age Distribution by Sex\n")
    lines.append("| Sex | Count | Mean Age | Std | Min | Max |")
    lines.append("|-----|-------|----------|-----|-----|-----|")
    for sex_val in ["Male", "Female"]:
        s = demo["age_stats"].loc[sex_val]
        lines.append(f"| {sex_val} | {s['count']:.0f} | {s['mean']:.1f} | {s['std']:.1f} | {s['min']:.0f} | {s['max']:.0f} |")
    lines.append("")

    lines.append("### Sex × Target Crosstab\n")
    lines.append("| Sex | No Disease (0) | Disease (1) | Disease Rate |")
    lines.append("|-----|---------------|-------------|-------------|")
    for sex_val in ["Male", "Female"]:
        no_d = demo["sex_target"].loc[sex_val, 0]
        d = demo["sex_target"].loc[sex_val, 1]
        rate = d / (no_d + d) * 100
        lines.append(f"| {sex_val} | {no_d} | {d} | {rate:.1f}% |")
    lines.append("")

    lines.append("### Known Limitations\n")
    lines.append(
        "1. **Sex imbalance**: The dataset is ~{:.0f}% male and ~{:.0f}% female ({:.1f}:1 ratio). "
        "This under-representation of women means any model trained on this data will have "
        "learned predominantly from male cardiac presentations.\n".format(
            demo["male_pct"], demo["female_pct"],
            demo["sex_counts"]["Male"] / demo["sex_counts"]["Female"],
        )
    )
    lines.append(
        "2. **Age range**: The UCI dataset covers ages ~29–77 but may not adequately represent "
        "younger women with pregnancy-related or autoimmune-related cardiac disease.\n"
    )
    lines.append(
        "3. **Feature set**: The 13 features are classic cardiac risk factors but miss sex-specific "
        "markers like hormone status, pregnancy history, preeclampsia history, PCOS, and autoimmune "
        "conditions — all of which are significant female cardiac risk factors.\n"
    )
    lines.append(
        "4. **Symptom encoding**: The `chest_pain_type` feature uses traditional categories that may "
        "not capture the atypical presentations more common in women (jaw pain, back pain, fatigue, nausea).\n"
    )
    lines.append(
        "5. **Outcome definition**: The binary target (disease/no-disease) is based on >50% diameter stenosis "
        "in major coronary arteries, which by definition excludes microvascular disease (INOCA/MINOCA) — "
        "a condition disproportionately affecting women.\n"
    )
    lines.append(
        "6. **Data origin**: The original data comes from the Cleveland Clinic, Hungarian Institute of "
        "Cardiology, University Hospital Zurich, and VA Long Beach (1988). Clinical practices and "
        "patient demographics have changed significantly since then.\n"
    )

    lines.append("### Recommended Alternative/Supplementary Datasets\n")
    lines.append(
        "1. **UK Biobank** (ukbiobank.ac.uk): ~500,000 participants aged 40–69 with extensive "
        "cardiovascular phenotyping, ~55% female. Includes imaging, genetics, and longitudinal follow-up.\n"
    )
    lines.append(
        "2. **MESA (Multi-Ethnic Study of Atherosclerosis)** (mesa-nhlbi.org): ~6,800 participants, "
        "~53% female, multi-ethnic (White, Black, Hispanic, Chinese-American). Includes subclinical "
        "atherosclerosis measures and cardiac MRI.\n"
    )
    lines.append(
        "3. **WISE Dataset (Women's Ischemia Syndrome Evaluation)**: NHLBI-sponsored study specifically "
        "designed to study ischemic heart disease in women, with focus on microvascular disease. "
        "Available through BioLINCC (biolincc.nhlbi.nih.gov).\n"
    )

    lines.append("---\n")

    # =========================================================================
    # F1: Chi-Square Test
    # =========================================================================
    lines.append("## F1 — Chi-Square Test: Sex vs Heart Disease Outcome\n")
    print("Running statistical tests...")
    chi_res = chi_square_test(df)

    lines.append("### Contingency Table\n")
    lines.append("| Sex | No Disease (0) | Disease (1) |")
    lines.append("|-----|---------------|-------------|")
    for sex_val in chi_res["contingency"].index:
        lines.append(f"| {sex_val} | {chi_res['contingency'].loc[sex_val, 0]} | {chi_res['contingency'].loc[sex_val, 1]} |")
    lines.append("")

    lines.append("### Test Results\n")
    lines.append("| Test | Statistic | P-value | Interpretation |")
    lines.append("|------|-----------|---------|----------------|")
    chi_sig = "Significant (p < 0.05)" if chi_res["p_value"] < 0.05 else "Not significant"
    rpb_sig = "Significant (p < 0.05)" if chi_res["rpb_p"] < 0.05 else "Not significant"
    lines.append(f"| Chi-Square | χ² = {chi_res['chi2']:.4f} | p = {chi_res['p_value']:.6f} | {chi_sig} |")
    lines.append(f"| Point-Biserial r | r = {chi_res['rpb']:.4f} | p = {chi_res['rpb_p']:.6f} | {rpb_sig} |")
    lines.append(
        f"| Odds Ratio | OR = {chi_res['odds_ratio']:.4f} | 95% CI [{chi_res['or_ci_lower']:.4f}, {chi_res['or_ci_upper']:.4f}] | "
        f"{'Female sex associated with disease' if chi_res['odds_ratio'] > 1 else 'Male sex associated with disease'} |"
    )
    lines.append("")

    lines.append(f"- **Degrees of freedom**: {chi_res['dof']}")
    if chi_res["p_value"] < 0.001:
        lines.append(f"- The relationship between sex and heart disease outcome is **highly statistically significant** (p < 0.001).")
    elif chi_res["p_value"] < 0.05:
        lines.append(f"- The relationship between sex and heart disease outcome is **statistically significant** (p < 0.05).")
    else:
        lines.append(f"- The relationship between sex and heart disease outcome is **not statistically significant** (p = {chi_res['p_value']:.4f}).")
    lines.append("")

    lines.append("---\n")

    # =========================================================================
    # F2: Distribution Analysis
    # =========================================================================
    lines.append("## F2 — Distribution Analysis by Sex\n")
    print("Running distribution analysis...")
    dist = distribution_analysis(df)

    for feat, data in dist.items():
        lines.append(f"### {feat}\n")
        lines.append("| Group | N | Mean | Median | Std Dev |")
        lines.append("|-------|---|------|--------|---------|")
        for grp in ["Healthy Male", "Diseased Male", "Healthy Female", "Diseased Female"]:
            d = data[grp]
            lines.append(f"| {grp} | {d['n']} | {d['mean']:.2f} | {d['median']:.2f} | {d['std']:.2f} |")
        lines.append("")
        tests = data["tests"]
        t_sig = "Yes" if tests["t_p"] < 0.05 else "No"
        u_sig = "Yes" if tests["u_p"] < 0.05 else "No"
        lines.append(f"**Diseased Female vs Diseased Male comparison:**")
        lines.append(f"- Welch's t-test: t = {tests['t_stat']:.4f}, p = {tests['t_p']:.6f} (Significant: {t_sig})")
        lines.append(f"- Mann-Whitney U: U = {tests['u_stat']:.1f}, p = {tests['u_p']:.6f} (Significant: {u_sig})")
        lines.append("")

    lines.append("### Summary of Distribution Findings\n")
    sig_features = []
    nonsig_features = []
    for feat, data in dist.items():
        if data["tests"]["t_p"] < 0.05:
            sig_features.append(feat)
        else:
            nonsig_features.append(feat)

    if sig_features:
        lines.append(f"**Significantly different** between diseased males and diseased females: {', '.join(sig_features)}\n")
    if nonsig_features:
        lines.append(f"**Not significantly different**: {', '.join(nonsig_features)}\n")

    lines.append(
        "These results indicate whether women with heart disease present with different biomarker "
        "profiles than men with heart disease, which has direct implications for sex-specific "
        "diagnostic thresholds.\n"
    )

    return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 60)
    print("HeartLens Research Part B + F — Full Analysis")
    print("=" * 60)
    df = load_data()
    print(f"Dataset loaded: {len(df)} rows, {df.shape[1]} columns")
    print(f"Male: {len(df[df['sex']=='Male'])}, Female: {len(df[df['sex']=='Female'])}")
    print()

    report = generate_report(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print(f"\nReport written to: {OUTPUT_PATH.resolve()}")
    print("Done!")
