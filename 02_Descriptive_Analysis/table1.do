*******************************************************
* Medical Data Analysis using Stata
* File: table1.do
* Purpose: Create Table 1 - Baseline Characteristics
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load cleaned dataset
*------------------------------------------------------*

* use "data/cleaned_dataset.dta", clear

*------------------------------------------------------*
* 2. Sample size
*------------------------------------------------------*

count

*------------------------------------------------------*
* 3. Continuous variables
*------------------------------------------------------*

* Mean and SD
* summarize age
* summarize bmi

* Median and IQR
* summarize age, detail
* summarize bmi, detail

*------------------------------------------------------*
* 4. Categorical variables
*------------------------------------------------------*

* Sex
* tab sex, missing

* Age group
* tab age_group, missing

* BMI group
* tab bmi_group, missing

* Outcome
* tab outcome, missing

*------------------------------------------------------*
* 5. Other clinical variables
*------------------------------------------------------*

* tab diabetes, missing
* tab hypertension, missing
* tab smoking, missing
* tab residence, missing

*******************************************************
* Example Table 1 structure
*******************************************************

* Variable              Overall (N=)
* -----------------------------------------------------
* Age, mean (SD)
* Age, median (IQR)
* Sex, n (%)
*   Male
*   Female
* BMI, mean (SD)
* BMI group, n (%)
*   <20
*   20-30
*   >30
* Diabetes, n (%)
* Hypertension, n (%)
* Smoking, n (%)
* -----------------------------------------------------

*******************************************************
* End of file
*******************************************************
