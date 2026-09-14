*******************************************************
* Medical Data Analysis using Stata
* File: poisson_regression.do
* Purpose: Crude and adjusted Risk Ratios
*******************************************************

clear all
set more off

*======================================================*
* 1. LOAD DATA
*======================================================*
* use "data/cleaned_dataset.dta", clear

*======================================================*
* 2. OUTCOME CHECKS
*======================================================*
* Outcome should be binary and coded 0/1.
* tab outcome, missing
* assert inlist(outcome,0,1) if !missing(outcome)

*======================================================*
* 3. CRUDE RISK RATIO
*======================================================*
* Robust Poisson regression gives RR estimates for
* binary outcomes with robust variance.
*
* poisson outcome i.sex, vce(robust) irr
* poisson outcome i.age_group, vce(robust) irr
* poisson outcome i.bmi_group, vce(robust) irr

*======================================================*
* 4. ADJUSTED MODEL
*======================================================*
* Set reference categories explicitly with ib#.
*
* poisson outcome ib1.sex ib1.age_group ib1.bmi_group ///
*     i.smoking i.diabetes i.hypertension, ///
*     vce(robust) irr

*======================================================*
* 5. MODEL DIAGNOSTIC / CONVERGENCE
*======================================================*
* estimates store adjusted_model
* estat vce
* estimates table adjusted_model, b(%9.3f) se(%9.3f) p(%9.4f)

*======================================================*
* 6. REPORTING
*======================================================*
* Report: RR, 95% CI and p-value.
* Clearly state reference category for every categorical
* predictor. Check sparse cells and separation before
* interpreting estimates.

* For cohort studies, robust Poisson RR is generally
* preferred when the outcome is binary and risk ratios
* are the desired measure. Do not label IRR as RR.

*******************************************************
* End of file
*******************************************************
