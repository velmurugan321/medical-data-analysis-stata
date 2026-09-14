*******************************************************
* Medical Data Analysis using Stata
* File: export_results.do
* Purpose: Centralized reproducible results export
*******************************************************

clear all
set more off
version 15.0

local datafile "data/cleaned_dataset.dta"
local outdir "07_Output"
local logfile "`outdir'/analysis_results.log"

capture confirm file "`datafile'"
if _rc {
    di as error "Data file not found: `datafile'"
    exit 601
}
use "`datafile'", clear
capture mkdir "`outdir'"

capture log close results_log
log using "`logfile'", replace text name(results_log)

*======================================================*
* 1. DATA QUALITY SUMMARY
*======================================================*
di as text "=============================================="
di as text "MEDICAL DATA ANALYSIS - RESULTS EXPORT"
di as text "=============================================="
count
di as text "Observations: " r(N)

* Configure variables below as needed.
local continuous "age bmi"
local categorical "sex outcome age_group bmi_group"

*======================================================*
* 2. DESCRIPTIVE OUTPUT
*======================================================*
di as text ""
di as text "--- Continuous variables ---"
foreach v of local continuous {
    capture confirm variable `v'
    if !_rc {
        quietly summarize `v', detail
        di as text "`v': N=" r(N) " Mean=" %9.3f r(mean) ///
            " SD=" %9.3f r(sd) " Median=" %9.3f r(p50) ///
            " IQR=" %9.3f (r(p75)-r(p25))
    }
}

di as text ""
di as text "--- Categorical variables ---"
foreach v of local categorical {
    capture confirm variable `v'
    if !_rc {
        di as text "Variable: `v'"
        tab `v', missing
    }
}

*======================================================*
* 3. ASSOCIATION OUTPUT
*======================================================*
* For binary outcomes, review each categorical predictor.
capture confirm variable outcome
if !_rc {
    foreach v of local categorical {
        if "`v'" != "outcome" {
            capture confirm variable `v'
            if !_rc {
                di as text ""
                di as text "Association: `v' x outcome"
                tab `v' outcome, row chi2
            }
        }
    }
}

*======================================================*
* 4. REGRESSION TEMPLATE
*======================================================*
* Stata 15-compatible robust Poisson model.
* Replace predictors with the validated analysis set.
* poisson outcome i.sex i.age_group i.bmi_group, vce(robust) irr

*======================================================*
* 5. DIAGNOSTIC TEMPLATE
*======================================================*
* Replace with the actual binary index/reference variables.
* diagt index_test reference_standard

*======================================================*
* 6. EXPORT / AUDIT NOTES
*======================================================*
di as text ""
di as text "Results log saved to: `logfile'"
di as text "Review missingness, coding, reference categories,"
di as text "sparse cells, model convergence and diagnostic CI method"
di as text "before using results in a manuscript."

log close results_log

*******************************************************
* End of file
*******************************************************
