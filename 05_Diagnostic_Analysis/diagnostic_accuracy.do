*******************************************************
* Medical Data Analysis using Stata
* File: diagnostic_accuracy.do
* Purpose: Diagnostic accuracy analysis
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load dataset
*------------------------------------------------------*

* use "data/cleaned_dataset.dta", clear

*------------------------------------------------------*
* 2. Check reference standard and index test
*------------------------------------------------------*

* tab reference_standard index_test, missing

*------------------------------------------------------*
* 3. Diagnostic accuracy
*------------------------------------------------------*

* Install diagt if not already installed
* ssc install diagt

* Example:
* diagt index_test reference_standard

*------------------------------------------------------*
* 4. Sensitivity and specificity
*------------------------------------------------------*

* Sensitivity:
* True positive / All disease positive

* Specificity:
* True negative / All disease negative

*------------------------------------------------------*
* 5. Predictive values
*------------------------------------------------------*

* PPV:
* True positive / All test positive

* NPV:
* True negative / All test negative

*------------------------------------------------------*
* 6. Likelihood ratios
*------------------------------------------------------*

* PLR = Sensitivity / (1 - Specificity)
* NLR = (1 - Sensitivity) / Specificity

*------------------------------------------------------*
* 7. Accuracy
*------------------------------------------------------*

* Accuracy = (TP + TN) / Total

*******************************************************
* End of file
*******************************************************
