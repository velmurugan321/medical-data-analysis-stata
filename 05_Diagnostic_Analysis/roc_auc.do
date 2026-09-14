*******************************************************
* Medical Data Analysis using Stata
* File: roc_auc.do
* Purpose: ROC curve and area under the curve
*******************************************************

clear all
set more off

*======================================================*
* 1. LOAD DATA
*======================================================*
* use "data/cleaned_dataset.dta", clear

*======================================================*
* 2. VERIFY REFERENCE STANDARD
*======================================================*
* reference_standard should be coded 0/1.
* tab reference_standard, missing

*======================================================*
* 3. CONTINUOUS TEST / PREDICTOR
*======================================================*
* Replace test_value with the continuous diagnostic
* measurement and reference_standard with disease status.
*
* roctab reference_standard test_value
* roctab reference_standard test_value, graph summary

*======================================================*
* 4. ROC CURVE
*======================================================*
* roctab reference_standard test_value, graph

* AUC interpretation must be considered with the clinical
* purpose of the test, spectrum of disease and study design.
* AUC = 0.5 indicates no discrimination in the observed data;
* values closer to 1 indicate stronger discrimination.

*======================================================*
* 5. COMPARE TWO TESTS
*======================================================*
* roctab reference_standard test1
* roctab reference_standard test2
*
* For formal comparison of correlated ROC curves, use an
* appropriate paired ROC comparison method and ensure both
* tests are measured on the same participants.

*======================================================*
* 6. REPORTING
*======================================================*
* Report AUC with 95% CI and sample size.
* If a cut-off is selected, report sensitivity and specificity
* at the clinically justified threshold rather than selecting
* a cut-off solely to maximize the observed sample result.

*******************************************************
* End of file
*******************************************************
