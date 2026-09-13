*******************************************************
* Medical Data Analysis using Stata
* File: missing_data.do
* Purpose: Missing data assessment
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load cleaned dataset
*------------------------------------------------------*

* use "data/cleaned_dataset.dta", clear

*------------------------------------------------------*
* 2. Overall missing data summary
*------------------------------------------------------*

misstable summarize

*------------------------------------------------------*
* 3. Missing data patterns
*------------------------------------------------------*

misstable patterns

*------------------------------------------------------*
* 4. Check important categorical variables
*------------------------------------------------------*

* tab sex, missing
* tab outcome, missing
* tab age_group, missing
* tab bmi_group, missing

*------------------------------------------------------*
* 5. Check important continuous variables
*------------------------------------------------------*

* summarize age bmi, detail

*------------------------------------------------------*
* 6. Check missing values for individual variables
*------------------------------------------------------*

* count if missing(age)
* count if missing(bmi)
* count if missing(outcome)

*******************************************************
* End of file
*******************************************************
