*******************************************************
* Medical Data Analysis using Stata
* File: risk_ratio_analysis.do
* Purpose: Crude and Adjusted Risk Ratios
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load cleaned dataset
*------------------------------------------------------*

* use "data/cleaned_dataset.dta", clear

*------------------------------------------------------*
* 2. Check outcome
*------------------------------------------------------*

* tab outcome, missing

*------------------------------------------------------*
* 3. Set reference categories
*------------------------------------------------------*

* Example:
* Sex: Male = reference
* Age: <20 = reference
* BMI: <20 = reference

*------------------------------------------------------*
* 4. Crude Risk Ratios
*------------------------------------------------------*

* poisson outcome ib1.sex, vce(robust) irr

* poisson outcome ib1.age_group, vce(robust) irr

* poisson outcome ib1.bmi_group, vce(robust) irr

*------------------------------------------------------*
* 5. Adjusted Risk Ratio
*------------------------------------------------------*

* poisson outcome ib1.sex ///
*     ib1.age_group ///
*     ib1.bmi_group ///
*     i.smoking ///
*     i.diabetes ///
*     i.hypertension, ///
*     vce(robust) irr

*------------------------------------------------------*
* 6. Store model
*------------------------------------------------------*

* estimates store adjusted_model

*******************************************************
* End of file
*******************************************************
