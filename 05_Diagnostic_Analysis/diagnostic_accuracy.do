*******************************************************
* Medical Data Analysis using Stata
* File: diagnostic_accuracy.do
* Purpose: Diagnostic accuracy with 2x2 table metrics
*******************************************************

clear all
set more off

*======================================================*
* 1. LOAD DATA
*======================================================*
* use "data/cleaned_dataset.dta", clear

*======================================================*
* 2. DEFINE VARIABLES
*======================================================*
* reference_standard: 0 = disease negative, 1 = disease positive
* index_test:          0 = test negative,   1 = test positive
*
* Confirm coding before analysis:
* tab reference_standard, missing
* tab index_test, missing
* tab reference_standard index_test, missing

*======================================================*
* 3. DIAGNOSTIC ACCURACY
*======================================================*
* Recommended user-written command, if installed:
* ssc install diagt
* diagt index_test reference_standard

*======================================================*
* 4. CORE FORMULAS
*======================================================*
* TP = index test + / reference standard +
* TN = index test - / reference standard -
* FP = index test + / reference standard -
* FN = index test - / reference standard +
*
* Sensitivity = TP / (TP + FN)
* Specificity = TN / (TN + FP)
* PPV         = TP / (TP + FP)
* NPV         = TN / (TN + FN)
* Accuracy    = (TP + TN) / N
* PLR         = Sensitivity / (1 - Specificity)
* NLR         = (1 - Sensitivity) / Specificity

*======================================================*
* 5. EXACT CONFIDENCE INTERVALS
*======================================================*
* Use a validated diagnostic command/package for exact
* or binomial confidence intervals rather than manually
* calculating intervals from rounded percentages.

*======================================================*
* 6. REPORTING CHECKLIST
*======================================================*
* Report 2x2 counts first, followed by:
* Sensitivity (95% CI)
* Specificity (95% CI)
* PPV (95% CI)
* NPV (95% CI)
* Accuracy (95% CI)
* Positive likelihood ratio (95% CI, when available)
* Negative likelihood ratio (95% CI, when available)
*
* State the reference standard and index-test definitions.
* Do not compare diagnostic tests using overlapping CIs alone.

*******************************************************
* End of file
*******************************************************
