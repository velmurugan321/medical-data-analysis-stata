*******************************************************
* Medical Data Analysis using Stata
* File: poisson_regression.do
* Purpose: Reusable crude and adjusted Risk Ratio workflow
*******************************************************

clear all
set more off
version 15.0

* USER SETTINGS ---------------------------------------*
local datafile "data/cleaned_dataset.dta"
local outcome "outcome"
local predictors "sex age_group bmi_group smoking diabetes hypertension"

capture confirm file "`datafile'"
if _rc {
    di as error "Dataset not found: `datafile'"
    exit 601
}
use "`datafile'", clear

capture confirm variable `outcome'
if _rc {
    di as error "Outcome variable not found: `outcome'"
    exit 111
}

tab `outcome', missing
assert inlist(`outcome',0,1) if !missing(`outcome')

* CRUDE MODELS ----------------------------------------*
foreach x of local predictors {
    capture confirm variable `x'
    if !_rc {
        di as text "=================================================="
        di as text "Crude model: `x'"
        poisson `outcome' i.`x', vce(robust) irr
    }
}

* ADJUSTED MODEL --------------------------------------*
local modelvars
foreach x of local predictors {
    capture confirm variable `x'
    if !_rc local modelvars `modelvars' i.`x'
}

if "`modelvars'" != "" {
    di as text "=================================================="
    di as text "Adjusted Poisson regression"
    poisson `outcome' `modelvars', vce(robust) irr
    estimates store poisson_adjusted
}

* REPORTING NOTE --------------------------------------*
* Report RR, 95% CI and p-value. State reference
* categories explicitly. Review sparse cells and model
* convergence before interpreting unstable estimates.

*******************************************************
* End of file
*******************************************************