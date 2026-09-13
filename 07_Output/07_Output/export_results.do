*******************************************************
* Medical Data Analysis using Stata
* File: export_results.do
* Purpose: Export analysis results
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load cleaned dataset
*------------------------------------------------------*

* use "data/cleaned_dataset.dta", clear

*------------------------------------------------------*
* 2. Create output folder
*------------------------------------------------------*

capture mkdir "07_Output"

*------------------------------------------------------*
* 3. Start log file
*------------------------------------------------------*

capture log close
log using "07_Output/analysis_results.log", replace text

*------------------------------------------------------*
* 4. Descriptive statistics
*------------------------------------------------------*

* summarize age bmi, detail

* tab sex, missing
* tab age_group, missing
* tab bmi_group, missing

*------------------------------------------------------*
* 5. Association analysis
*------------------------------------------------------*

* tab sex outcome, chi2
* tab age_group outcome, chi2
* tab bmi_group outcome, chi2

*------------------------------------------------------*
* 6. Regression analysis
*------------------------------------------------------*

* poisson outcome i.sex i.age_group i.bmi_group, ///
*     vce(robust) irr

*------------------------------------------------------*
* 7. Diagnostic accuracy
*------------------------------------------------------*

* diagt index_test reference_standard

*------------------------------------------------------*
* 8. Close log
*------------------------------------------------------*

log close

*******************************************************
* End of file
*******************************************************
