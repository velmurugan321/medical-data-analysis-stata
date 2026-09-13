# Medical Data Analysis using Stata

A reproducible framework for clinical and medical research data analysis using Stata.

## Project Overview

This repository contains reusable Stata scripts for data management, descriptive analysis, association analysis, regression modelling, diagnostic accuracy analysis, and data visualization.

The framework is designed for medical and public health research projects.

## Analysis Workflow

```text
Data
  ↓
Data Management
  ↓
Descriptive Analysis
  ↓
Association Analysis
  ↓
Regression Analysis
  ↓
Diagnostic Analysis
  ↓
Visualization
  ↓
Final Results
Statistical Methods
The repository includes examples for:
Descriptive statistics
Frequency and percentage
Mean, standard deviation and median
Interquartile range
Chi-square test
Fisher's exact test
t-test
Mann-Whitney U test
ANOVA
Kruskal-Wallis test
Correlation analysis
Poisson regression with robust variance
Crude Risk Ratio (cRR)
Adjusted Risk Ratio (aRR)
Diagnostic accuracy
Sensitivity
Specificity
Positive Predictive Value
Negative Predictive Value
Positive Likelihood Ratio
Negative Likelihood Ratio
ROC curve
Area Under the Curve (AUC)
Reproducibility
The run_all.do file provides a single workflow for running the analysis scripts in sequence.
Before using the scripts:
Update the dataset path.
Verify variable names.
Check variable coding.
Define appropriate reference categories.
Review missing data.
Run the analysis.
Validate the results before reporting.
Data Privacy
No patient-identifiable or confidential medical data should be uploaded to this public repository.
Raw and analysis datasets should remain in a secure local or institutional environment.
Common medical data file formats are excluded using .gitignore.
Software
Stata
GitHub
Intended Use
This repository is intended for medical, clinical, epidemiological, and public health research analysis.
The scripts are templates and should be adapted and validated for each individual study.
Author
Velmurugan
License
This project is licensed under the MIT License.



**GitHub repository-யை உங்கள் actual Stata medical research workflow-க்கு ready செய்வது — `config.do` file மூலம் dataset path, output path, project settings ஒரே இடத்தில் manage செய்வது.**
