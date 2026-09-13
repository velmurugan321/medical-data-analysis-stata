*******************************************************
* Medical Data Analysis using Stata
* File: demographics.do
* Purpose: Descriptive analysis of study population
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load cleaned dataset
*------------------------------------------------------*

* use "data/cleaned_dataset.dta", clear

*------------------------------------------------------*
* 2. Number of observations
*------------------------------------------------------*

count

*------------------------------------------------------*
* 3. Demographic variables
*------------------------------------------------------*

* Sex
* tab sex, missing

* Age
* summarize age, detail

* Age categories
* tab age_group, missing

*------------------------------------------------------*
* 4. Clinical variables
*------------------------------------------------------*

* BMI
* summarize bmi, detail

* BMI categories
* tab bmi_group, missing

* Outcome
* tab outcome, missing

*------------------------------------------------------*
* 5. Other categorical variables
*------------------------------------------------------*

* tab residence, missing
* tab smoking, missing
* tab diabetes, missing
* tab hypertension, missing

*******************************************************
* End of file
*******************************************************
