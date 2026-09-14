*******************************************************
* Medical Data Analysis using Stata
* File: roc_graph.do
* Purpose: Reproducible ROC curve visualization
*******************************************************

clear all
set more off
version 15.0

* USER SETTINGS ---------------------------------------*
local datafile "data/cleaned_dataset.dta"
local reference "reference_standard"
local testvalue "test_value"
local outdir "07_Output"

capture confirm file "`datafile'"
if _rc {
    di as error "Dataset not found: `datafile'"
    exit 601
}
use "`datafile'", clear

capture confirm variable `reference'
if _rc exit 111
capture confirm variable `testvalue'
if _rc exit 111

capture mkdir "`outdir'"

* ROC curve with AUC and graph
roctab `reference' `testvalue', summary graph

* Export publication-ready image
capture graph export "`outdir'/roc_curve.png", replace width(1800)

* Multiple-test comparison template
* roccomp `reference' test1 test2, graph

*******************************************************
* End of file
*******************************************************