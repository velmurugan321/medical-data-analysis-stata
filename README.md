# Medical Data Analysis — Stata

A reproducible medical research analysis framework for Stata. The repository is organised from **data management → descriptive analysis → association → regression → diagnostic analysis → visualisation → outputs**.

## What this repository provides

- Reusable Stata `.do` files for common medical research analyses
- Explicit data-quality and variable-coding checks
- Descriptive and comparative statistical workflows
- Robust Poisson regression for risk ratios where appropriate
- Diagnostic accuracy and ROC/AUC workflows
- Reproducible visualisation and output export
- A project template for starting new studies

> **Important:** Statistical method selection must follow the study design, outcome type, sampling strategy and analysis plan. The scripts are templates and should be reviewed before publication.

## Repository workflow

```text
01_Data_Management
        ↓
02_Descriptive_Analysis
        ↓
03_Association_Analysis
        ↓
04_Regression
        ↓
05_Diagnostic_Analysis
        ↓
06_Visualization
        ↓
07_Output
```

### 01 — Data Management

Data inspection, missingness, cleaning and derived-variable creation.

### 02 — Descriptive Analysis

Frequency/percentage for categorical variables and mean/SD or median/IQR for continuous variables.

### 03 — Association Analysis

Chi-square, Fisher's exact, t-test, ANOVA, Mann–Whitney and Kruskal–Wallis as appropriate.

### 04 — Regression

Crude and adjusted risk ratios using Poisson regression with robust variance when appropriate. Reference categories must always be explicitly verified.

### 05 — Diagnostic Analysis

Sensitivity, specificity, PPV, NPV, positive/negative likelihood ratios, accuracy, ROC curve and AUC.

### 06 — Visualization

Study-appropriate graphs, diagnostic plots and publication-oriented figures.

### 07 — Output

Final tables, figures and exported analysis results.

## Data protection

Do **not** commit patient-level, identifiable, confidential or restricted medical data to this public repository. Keep raw datasets outside GitHub and commit only de-identified examples, analysis code and documentation.

## Quality-control checklist

Before accepting a result:

1. Confirm the dataset and analysis population.
2. Check observations, variables and duplicates.
3. Review missing and impossible values.
4. Verify variable coding and labels.
5. Verify reference categories.
6. Match the statistical method to the study design.
7. Check confidence intervals and p-values.
8. Compare output with an independent calculation or Stata command where feasible.
9. Review tables/figures against the analysis dataset.
10. Document exclusions, assumptions and sensitivity analyses.

## Project template

`PROJECT_TEMPLATE/` contains a clean structure for new studies. Copy the template into a separate project rather than putting patient data into this repository.

## Current scope

This repository is the **Stata analysis engine and reproducibility layer**. A future web interface can sit on top of these validated workflows, but browser-side summaries should not be presented as publication-grade statistical inference without validation against Stata/R.

## Licence

See `LICENSE`.
