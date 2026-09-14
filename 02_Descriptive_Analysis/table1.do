*******************************************************
* Medical Data Analysis using Stata
* File: table1.do
* Purpose: Reproducible Table 1 template
* Notes: Replace variable names in the USER SETTINGS section.
*******************************************************

version 15.0
clear all
set more off

*------------------------------------------------------*
* USER SETTINGS
*------------------------------------------------------*
* use "data/cleaned_dataset.dta", clear
local continuous age bmi
local categorical sex age_group bmi_group diabetes hypertension smoking residence outcome

*------------------------------------------------------*
* 1. Data checks
*------------------------------------------------------*
count
assert _N > 0

* Inspect all candidate variables before analysis.
foreach v of local continuous {
    capture confirm variable `v'
    if _rc == 0 {
        quietly count if !missing(`v')
        di as text "`v': non-missing N = " r(N)
        quietly summarize `v'
        di as result "  mean=" %9.3f r(mean) " SD=" %9.3f r(sd) " min=" %9.3f r(min) " max=" %9.3f r(max)
    }
    else di as error "Variable not found: `v'"
}

*------------------------------------------------------*
* 2. Continuous variables: mean (SD) and median (IQR)
*------------------------------------------------------*
foreach v of local continuous {
    capture confirm variable `v'
    if _rc == 0 {
        di as text "--------------------------------------------------"
        di as text "`v'"
        quietly summarize `v', detail
        di as result "Mean (SD): " %9.2f r(mean) " (" %9.2f r(sd) ")"
        di as result "Median (IQR): " %9.2f r(p50) " (" %9.2f r(p25) " - " %9.2f r(p75) ")"
        di as result "Range: " %9.2f r(min) " - " %9.2f r(max)
    }
}

*------------------------------------------------------*
* 3. Categorical variables: n (%)
*------------------------------------------------------*
foreach v of local categorical {
    capture confirm variable `v'
    if _rc == 0 {
        di as text "--------------------------------------------------"
        di as text "`v'"
        tabulate `v', missing
    }
}

*------------------------------------------------------*
* 4. Optional stratified Table 1
*------------------------------------------------------*
* Define a grouping variable below when needed.
* local group outcome
*
* foreach v of local continuous {
*     capture confirm variable `v'
*     if _rc == 0 summarize `v' if !missing(`v'), detail
* }
*
* foreach v of local categorical {
*     capture confirm variable `v'
*     if _rc == 0 tabulate `v' `group', row missing
* }

*------------------------------------------------------*
* 5. Recommended reporting format
*------------------------------------------------------*
* Continuous: mean (SD) OR median (IQR), chosen according to
* distribution and analysis plan.
* Categorical: n (%), with denominator stated when missingness exists.
* Do not silently recode missing values as valid categories.

*******************************************************
* End of file
*******************************************************
