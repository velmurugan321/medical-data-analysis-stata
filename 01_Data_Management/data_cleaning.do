*******************************************************
* Medical Data Analysis using Stata
* File: data_cleaning.do
* Purpose: Basic data cleaning and quality checks
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load dataset
*------------------------------------------------------*

* Replace with your actual dataset path
* use "data/your_dataset.dta", clear

*------------------------------------------------------*
* 2. Inspect dataset
*------------------------------------------------------*

describe
codebook

*------------------------------------------------------*
* 3. Check number of observations
*------------------------------------------------------*

count

*------------------------------------------------------*
* 4. Check duplicate patient IDs
*------------------------------------------------------*

* Replace patient_id with your actual ID variable
* duplicates report patient_id
* duplicates list patient_id

*------------------------------------------------------*
* 5. Check missing values
*------------------------------------------------------*

misstable summarize

*------------------------------------------------------*
* 6. Check categorical variables
*------------------------------------------------------*

* tab sex, missing
* tab outcome, missing
* tab age_group, missing

*------------------------------------------------------*
* 7. Check continuous variables
*------------------------------------------------------*

* summarize age, detail
* summarize bmi, detail

*------------------------------------------------------*
* 8. Check impossible or unusual values
*------------------------------------------------------*

* assert age >= 0 & age <= 120
* assert bmi > 0 & bmi < 80

*------------------------------------------------------*
* 9. Save cleaned dataset
*------------------------------------------------------*

* save "data/cleaned_dataset.dta", replace

*******************************************************
* End of file
*******************************************************
