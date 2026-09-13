*******************************************************
* Medical Data Analysis Project
* File: analysis.do
* Purpose: Master analysis workflow
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load dataset
*------------------------------------------------------*

* use "path/to/your/secure_dataset.dta", clear

*------------------------------------------------------*
* 2. Data quality checks
*------------------------------------------------------*

describe
count
misstable summarize

*------------------------------------------------------*
* 3. Data management
*------------------------------------------------------*

* Data cleaning
* Variable creation
* Missing data assessment

*------------------------------------------------------*
* 4. Descriptive analysis
*------------------------------------------------------*

* summarize age, detail
* tab sex, missing
* tab outcome, missing

*------------------------------------------------------*
* 5. Association analysis
*------------------------------------------------------*

* tab exposure outcome, chi2

*------------------------------------------------------*
* 6. Regression analysis
*------------------------------------------------------*

* poisson outcome i.exposure, vce(robust) irr

*------------------------------------------------------*
* 7. Diagnostic analysis
*------------------------------------------------------*

* tab index_test reference_standard, missing

*------------------------------------------------------*
* 8. ROC / AUC
*------------------------------------------------------*

* roctab reference_standard test_value, graph

*------------------------------------------------------*
* 9. Final checks
*------------------------------------------------------*

* Check sample size
* Check missing values
* Check percentages
* Check confidence intervals
* Check p-values

*******************************************************
* End of analysis
*******************************************************
