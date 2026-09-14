*******************************************************
* Medical Data Analysis using Stata
* File: categorical_association.do
* Purpose: Association between categorical variables
*******************************************************

version 15.0
clear all
set more off

*------------------------------------------------------*
* USER SETTINGS
*------------------------------------------------------*
* use "data/cleaned_dataset.dta", clear
local outcome outcome
local predictors sex age_group bmi_group smoking diabetes hypertension

*------------------------------------------------------*
* 1. Basic validation
*------------------------------------------------------*
count
assert _N > 0
capture confirm variable `outcome'
if _rc {
    di as error "Outcome variable `outcome' not found. Edit USER SETTINGS."
    exit 111
}

*------------------------------------------------------*
* 2. Cross-tabulation and Pearson chi-square
*------------------------------------------------------*
foreach x of local predictors {
    capture confirm variable `x'
    if _rc == 0 {
        di as text "=================================================="
        di as text "Predictor: `x' | Outcome: `outcome'"
        tabulate `x' `outcome', row column missing
        tabulate `x' `outcome', chi2
    }
    else di as error "Variable not found: `x'"
}

*------------------------------------------------------*
* 3. Fisher's exact test for small 2x2 tables
*------------------------------------------------------*
* Run exact tests only when the table is 2x2.
* Example:
* tabulate smoking outcome, exact

*------------------------------------------------------*
* 4. Trend test for ordered categorical predictors
*------------------------------------------------------*
* If categories have a meaningful order and are coded numerically:
* nptrend outcome, by(age_group)

*------------------------------------------------------*
* 5. Interpretation safeguards
*------------------------------------------------------*
* - Report counts and percentages, not p-values alone.
* - Use Fisher's exact test when sparse 2x2 cells make chi-square
*   assumptions unreliable.
* - Do not treat an arbitrary numeric coding as an ordinal scale.
* - Statistical significance does not establish causality.

*******************************************************
* End of file
*******************************************************
