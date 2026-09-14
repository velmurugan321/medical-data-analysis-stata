*******************************************************
* Medical Data Analysis using Stata
* File: diagnostic_accuracy.do
* Purpose: Reproducible diagnostic accuracy analysis
*******************************************************

clear all
set more off
version 15.0

*======================================================*
* 1. CONFIGURATION
*======================================================*
local datafile "data/cleaned_dataset.dta"
local reference "reference_standard"
local index "index_test"
local outdir "07_Output"

capture confirm file "`datafile'"
if _rc {
    di as error "Data file not found: `datafile'"
    exit 601
}
use "`datafile'", clear

capture confirm variable `reference'
if _rc {
    di as error "Reference-standard variable not found: `reference'"
    exit 111
}
capture confirm variable `index'
if _rc {
    di as error "Index-test variable not found: `index'"
    exit 111
}

* Expected binary coding: 0 = negative, 1 = positive
tab `reference', missing
tab `index', missing
assert inlist(`reference',0,1) if !missing(`reference')
assert inlist(`index',0,1) if !missing(`index')

*======================================================*
* 2. 2x2 TABLE
*======================================================*
tab `index' `reference', missing

quietly count if !missing(`reference',`index')
local N = r(N)
quietly count if `index'==1 & `reference'==1
local TP = r(N)
quietly count if `index'==0 & `reference'==0
local TN = r(N)
quietly count if `index'==1 & `reference'==0
local FP = r(N)
quietly count if `index'==0 & `reference'==1
local FN = r(N)

assert `TP' + `TN' + `FP' + `FN' == `N'

di as text ""
di as text "2x2 diagnostic table"
di as text "TP=`TP'  TN=`TN'  FP=`FP'  FN=`FN'  N=`N'"

*======================================================*
* 3. POINT ESTIMATES
*======================================================*
local sens = cond((`TP'+`FN')>0, `TP'/(`TP'+`FN'), .)
local spec = cond((`TN'+`FP')>0, `TN'/(`TN'+`FP'), .)
local ppv  = cond((`TP'+`FP')>0, `TP'/(`TP'+`FP'), .)
local npv  = cond((`TN'+`FN')>0, `TN'/(`TN'+`FN'), .)
local acc  = cond(`N'>0, (`TP'+`TN')/`N', .)
local plr  = cond((1-`spec')>0, `sens'/(1-`spec'), .)
local nlr  = cond(`spec'>0, (1-`sens')/`spec', .)

di as result "Sensitivity = " %6.3f `sens'
di as result "Specificity = " %6.3f `spec'
di as result "PPV         = " %6.3f `ppv'
di as result "NPV         = " %6.3f `npv'
di as result "Accuracy    = " %6.3f `acc'
di as result "PLR         = " %6.3f `plr'
di as result "NLR         = " %6.3f `nlr'

*======================================================*
* 4. VALIDATED CI WORKFLOW
*======================================================*
* For publication-grade 95% CIs, use a validated diagnostic
* package such as diagt after installing it from SSC:
*     ssc install diagt
*     diagt `index' `reference'
*
* This workflow intentionally does not construct CIs from
* rounded percentages. Confirm the CI method before reporting.

*======================================================*
* 5. OPTIONAL OUTPUT LOG
*======================================================*
capture mkdir "`outdir'"
capture log close diagnostic_log
capture log using "`outdir'/diagnostic_accuracy.log", replace text name(diagnostic_log)
di as text "Diagnostic accuracy analysis"
di as text "Reference: `reference' | Index: `index' | N=`N'"
di as text "TP=`TP' TN=`TN' FP=`FP' FN=`FN'"
di as text "Sensitivity=" %6.3f `sens'
di as text "Specificity=" %6.3f `spec'
di as text "PPV=" %6.3f `ppv'
di as text "NPV=" %6.3f `npv'
di as text "Accuracy=" %6.3f `acc'
di as text "PLR=" %6.3f `plr'
di as text "NLR=" %6.3f `nlr'
capture log close diagnostic_log

*******************************************************
* End of file
*******************************************************
