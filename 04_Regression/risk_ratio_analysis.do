*******************************************************
* Medical Data Analysis using Stata
* File: risk_ratio_analysis.do
* Purpose: Standardized RR workflow and references
*******************************************************

clear all
set more off

*======================================================*
* 1. LOAD DATA
*======================================================*
* use "data/cleaned_dataset.dta", clear

*======================================================*
* 2. VERIFY VARIABLES
*======================================================*
* tab outcome, missing
* tab sex, missing
* tab age_group, missing
* tab bmi_group, missing

*======================================================*
* 3. REFERENCE CATEGORIES
*======================================================*
* Example coding below assumes category 1 is the desired
* reference. Change ib1 to the correct category number.
*
* sex: Male = reference
* age_group: <20 = reference
* bmi_group: <20 = reference

*======================================================*
* 4. CRUDE RR
*======================================================*
* poisson outcome ib1.sex, vce(robust) irr
* poisson outcome ib1.age_group, vce(robust) irr
* poisson outcome ib1.bmi_group, vce(robust) irr

*======================================================*
* 5. ADJUSTED RR
*======================================================*
* poisson outcome ib1.sex ib1.age_group ib1.bmi_group ///
*     i.smoking i.diabetes i.hypertension, ///
*     vce(robust) irr

*======================================================*
* 6. SAVE MODEL FOR REPORTING
*======================================================*
* estimates store adjusted_model

*======================================================*
* 7. QUALITY CHECKS
*======================================================*
* Check sparse categories before modelling.
* tab outcome sex, missing
* tab outcome age_group, missing
* tab outcome bmi_group, missing
*
* Confirm that the adjusted model uses clinically and
* epidemiologically justified covariates. Avoid automatic
* variable selection based only on univariable p-values.

*******************************************************
* End of file
*******************************************************
