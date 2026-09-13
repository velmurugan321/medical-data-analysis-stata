
*******************************************************
* Medical Data Analysis using Stata
* File: poisson_regression.do
* Purpose: Crude and adjusted Risk Ratio analysis
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load cleaned dataset
*------------------------------------------------------*

* use "data/cleaned_dataset.dta", clear

*------------------------------------------------------*
* 2. Check outcome variable
*------------------------------------------------------*

* tab outcome, missing

*------------------------------------------------------*
* 3. Crude Risk Ratio (cRR)
*------------------------------------------------------*

* Example:
* poisson outcome i.sex, vce(robust)

* Age group
* poisson outcome i.age_group, vce(robust)

* BMI group
* poisson outcome i.bmi_group, vce(robust)

*------------------------------------------------------*
* 4. Multiple-variable / adjusted model
*------------------------------------------------------*

* poisson outcome i.sex i.age_group i.bmi_group ///
*     i.smoking i.diabetes i.hypertension, vce(robust)

*------------------------------------------------------*
* 5. Display Incidence/Risk Ratios
*------------------------------------------------------*

* poisson outcome i.sex i.age_group i.bmi_group ///
*     i.smoking i.diabetes i.hypertension, ///
*     vce(robust) irr

*------------------------------------------------------*
* 6. Check model results
*------------------------------------------------------*

* estimates store adjusted_model

*******************************************************
* End of file
*******************************************************
