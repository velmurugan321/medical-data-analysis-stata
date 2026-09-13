*******************************************************
* Medical Data Analysis using Stata
* File: roc_graph.do
* Purpose: ROC curve visualization
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load cleaned dataset
*------------------------------------------------------*

* use "data/cleaned_dataset.dta", clear

*------------------------------------------------------*
* 2. Generate ROC curve
*------------------------------------------------------*

* Replace these variable names with actual variables

* roctab reference_standard test_value, graph

*------------------------------------------------------*
* 3. Save ROC graph
*------------------------------------------------------*

* graph export "07_Output/roc_curve.png", replace

*------------------------------------------------------*
* 4. Compare multiple diagnostic tests
*------------------------------------------------------*

* roccomp reference_standard test1 test2, graph

*******************************************************
* End of file
*******************************************************
