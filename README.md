## Analysis Workflow

The recommended workflow for a new medical research dataset is:

### Step 1 — Data Management

- Import the dataset
- Check observations and variables
- Check duplicates
- Assess missing data
- Identify invalid values

Script:

`01_Data_Management/`

### Step 2 — Variable Creation

Create and verify required analysis variables.

Examples:

- Age categories
- BMI categories
- Exposure variables
- Outcome variables

### Step 3 — Descriptive Analysis

Describe the study population using:

- Frequency
- Percentage
- Mean
- Standard deviation
- Median
- Interquartile range

Scripts:

`02_Descriptive_Analysis/`

### Step 4 — Association Analysis

Assess relationships between exposure and outcome variables.

Methods may include:

- Chi-square test
- Fisher's exact test
- t-test
- Mann-Whitney U test
- ANOVA
- Kruskal-Wallis test

Scripts:

`03_Association_Analysis/`

### Step 5 — Regression Analysis

Depending on the study design and outcome:

- Crude Risk Ratio
- Adjusted Risk Ratio
- Poisson regression with robust variance

Scripts:

`04_Regression/`

### Step 6 — Diagnostic Analysis

For diagnostic studies:

- Sensitivity
- Specificity
- PPV
- NPV
- PLR
- NLR
- Accuracy
- ROC curve
- AUC

Scripts:

`05_Diagnostic_Analysis/`

### Step 7 — Visualization

Prepare appropriate figures and graphs.

Scripts:

`06_Visualization/`

### Step 8 — Final Outputs

Store final tables, figures, and analysis documentation in:

`07_Output/`

## Quality Control

Before reporting results:

1. Verify the analysis dataset.
2. Check sample size.
3. Check missing data.
4. Verify variable coding.
5. Verify reference categories.
6. Check statistical calculations.
7. Cross-check tables and figures.
8. Review all results before publication.

## Data Protection

This repository is intended for analysis code and documentation.

Patient-level or confidential medical data must remain outside the public repository.
