*******************************************************
* Medical Data Analysis using Stata
* File: roc_auc.do
* Purpose: ROC Curve and Area Under the Curve
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load dataset
*------------------------------------------------------*

* use "data/cleaned_dataset.dta", clear

*------------------------------------------------------*
* 2. Check reference standard
*------------------------------------------------------*

* tab reference_standard, missing

*------------------------------------------------------*
* 3. ROC curve for continuous diagnostic test
*------------------------------------------------------*

* Replace test_value with your diagnostic test variable
* Replace reference_standard with disease status

* roctab reference_standard test_value

*------------------------------------------------------*
* 4. Display ROC curve
*------------------------------------------------------*

* roctab reference_standard test_value, graph

*------------------------------------------------------*
* 5. ROC curve with confidence interval
*------------------------------------------------------*

* roctab reference_standard test_value, graph summary

*------------------------------------------------------*
* 6. Compare two diagnostic tests
*------------------------------------------------------*

* roctab reference_standard test1
* roctab reference_standard test2

*******************************************************
* Interpretation
*******************************************************

* AUC close to 1.0  = excellent discrimination
* AUC around 0.5    = no better than chance
* Higher AUC        = better diagnostic discrimination

*******************************************************
* End of file
*******************************************************
