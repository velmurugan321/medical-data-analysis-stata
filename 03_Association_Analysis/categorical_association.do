*******************************************************
* Medical Data Analysis using Stata
* File: categorical_association.do
* Purpose: Association between categorical variables
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load cleaned dataset
*------------------------------------------------------*

* use "data/cleaned_dataset.dta", clear

*------------------------------------------------------*
* 2. Two-way tables
*------------------------------------------------------*

* Sex and outcome
* tab sex outcome, row column

* Age group and outcome
* tab age_group outcome, row column

* BMI group and outcome
* tab bmi_group outcome, row column

* Smoking and outcome
* tab smoking outcome, row column

* Diabetes and outcome
* tab diabetes outcome, row column

* Hypertension and outcome
* tab hypertension outcome, row column

*------------------------------------------------------*
* 3. Chi-square test
*------------------------------------------------------*

* tab sex outcome, chi2
* tab age_group outcome, chi2
* tab bmi_group outcome, chi2
* tab smoking outcome, chi2
* tab diabetes outcome, chi2
* tab hypertension outcome, chi2

*------------------------------------------------------*
* 4. Fisher's exact test
*------------------------------------------------------*

* Use Fisher's exact test when expected cell counts
* are small.

* tab sex outcome, exact
* tab smoking outcome, exact

*******************************************************
* End of file
*******************************************************
