*******************************************************
* TB Lymphadenitis Analysis
* File: analysis.do
* Purpose: Master analysis workflow
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Project configuration
*------------------------------------------------------*

do "config.do"

*------------------------------------------------------*
* 2. Load study dataset
*------------------------------------------------------*

* IMPORTANT:
* Replace with the actual secure local dataset path.
*
* use "C:/Secure_Data/TB_Lymphadenitis/cleaned_data.dta", clear

*------------------------------------------------------*
* 3. Initial data checks
*------------------------------------------------------*

describe
count
misstable summarize

*------------------------------------------------------*
* 4. Descriptive analysis
*------------------------------------------------------*

* Example:
* tab sex, missing
* summarize age, detail

*------------------------------------------------------*
* 5. Diagnostic accuracy
*------------------------------------------------------*

* Example:
* tab index_test reference_standard, missing

* diagt index_test reference_standard

*------------------------------------------------------*
* 6. Regression analysis
*------------------------------------------------------*

* Example:
* poisson outcome i.sex i.age_group, ///
*     vce(robust) irr

*------------------------------------------------------*
* 7. ROC / AUC
*------------------------------------------------------*

* Example:
* roctab reference_standard test_value, graph

*******************************************************
* End of analysis
*******************************************************
