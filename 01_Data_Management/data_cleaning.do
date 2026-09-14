*******************************************************
* Medical Data Analysis using Stata
* File: data_cleaning.do
* Purpose: Reproducible data-quality checks
*******************************************************

version 15.0
clear all
set more off
set varabbrev off

*------------------------------------------------------*
* 1. Load data
*------------------------------------------------------*
* Replace with the actual project-specific path.
* use "data/raw_dataset.dta", clear

*------------------------------------------------------*
* 2. First-pass dataset audit
*------------------------------------------------------*
describe
count
codebook

* Variable-level missingness
misstable summarize

*------------------------------------------------------*
* 3. Duplicate check
*------------------------------------------------------*
* Replace patient_id with the unique study identifier.
* isid patient_id
* duplicates report patient_id
* duplicates tag patient_id, gen(dup_id)

*------------------------------------------------------*
* 4. Categorical-variable checks
*------------------------------------------------------*
* Review distributions and missing categories.
* tab sex, missing
* tab outcome, missing
* tab exposure, missing

*------------------------------------------------------*
* 5. Continuous-variable checks
*------------------------------------------------------*
* summarize age bmi, detail
* histogram age, normal
* histogram bmi, normal

*------------------------------------------------------*
* 6. Range / plausibility checks
*------------------------------------------------------*
* Uncomment and adapt to the study protocol.
* assert inrange(age,0,120) if !missing(age)
* assert bmi > 0 & bmi < 80 if !missing(bmi)

*------------------------------------------------------*
* 7. Explicit missing-value handling
*------------------------------------------------------*
* Never silently convert special codes into valid observations.
* Example:
* replace age = . if age==999
* label define yesno 0 "No" 1 "Yes", replace
* label values exposure yesno

*------------------------------------------------------*
* 8. Save cleaned dataset
*------------------------------------------------------*
* save "data/cleaned_dataset.dta", replace

*******************************************************
* End of file
*******************************************************
