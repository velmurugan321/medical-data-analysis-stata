*******************************************************
* Medical Data Analysis using Stata
* File: variable_creation.do
* Purpose: Reproducible derived-variable templates
*******************************************************

version 15.0
set more off

*------------------------------------------------------*
* Age categories — example only; adapt to protocol
*------------------------------------------------------*
* gen age_cat = .
* replace age_cat = 1 if age < 20 & !missing(age)
* replace age_cat = 2 if inrange(age,20,30)
* replace age_cat = 3 if age > 30 & !missing(age)
* label define agecat 1 "<20" 2 "20-30" 3 ">30", replace
* label values age_cat agecat
* tab age_cat, missing

*------------------------------------------------------*
* BMI categories — example only; adapt to protocol
*------------------------------------------------------*
* gen bmi_cat = .
* replace bmi_cat = 1 if bmi < 20 & !missing(bmi)
* replace bmi_cat = 2 if inrange(bmi,20,30)
* replace bmi_cat = 3 if bmi > 30 & !missing(bmi)
* label define bmcat 1 "<20" 2 "20-30" 3 ">30", replace
* label values bmi_cat bmcat
* tab bmi_cat, missing

*------------------------------------------------------*
* General rules
*------------------------------------------------------*
* 1. Preserve the original variable.
* 2. Do not recode special missing codes as valid values.
* 3. Define cut-points explicitly and check boundary values.
* 4. Apply value labels.
* 5. tabulate the new variable before analysis.
