*******************************************************
* Medical Data Analysis using Stata
* File: graphs.do
* Purpose: Reproducible visualization and graph export
*******************************************************

clear all
set more off
version 15.0

local datafile "data/cleaned_dataset.dta"
local outdir "07_Output/graphs"

capture confirm file "`datafile'"
if _rc {
    di as error "Data file not found: `datafile'"
    exit 601
}
use "`datafile'", clear
capture mkdir "07_Output"
capture mkdir "`outdir'"

* Configure variables before running.
local catvar "sex"
local outcome "outcome"
local cont1 "age"
local cont2 "bmi"

*======================================================*
* 1. CATEGORICAL BAR CHART
*======================================================*
capture confirm variable `catvar'
if !_rc {
    graph bar (count), over(`catvar') title("Distribution of `catvar'")
    graph export "`outdir'/bar_`catvar'.png", replace width(1800)
}

*======================================================*
* 2. OUTCOME BY GROUP
*======================================================*
capture confirm variable `catvar'
capture confirm variable `outcome'
if !_rc {
    graph bar (count), over(`outcome') over(`catvar') title("Outcome by `catvar'")
    graph export "`outdir'/outcome_by_`catvar'.png", replace width(1800)
}

*======================================================*
* 3. HISTOGRAMS
*======================================================*
foreach v in `cont1' `cont2' {
    capture confirm variable `v'
    if !_rc {
        histogram `v', frequency title("Distribution of `v'")
        graph export "`outdir'/hist_`v'.png", replace width(1800)
    }
}

*======================================================*
* 4. BOXPLOTS
*======================================================*
capture confirm variable `outcome'
if !_rc {
    foreach v in `cont1' `cont2' {
        capture confirm variable `v'
        if !_rc {
            graph box `v', over(`outcome') title("`v' by outcome")
            graph export "`outdir'/box_`v'_by_outcome.png", replace width(1800)
        }
    }
}

*======================================================*
* 5. SCATTER + FITTED LINE
*======================================================*
capture confirm variable `cont1'
capture confirm variable `cont2'
if !_rc {
    twoway (scatter `cont2' `cont1') (lfit `cont2' `cont1'), ///
        title("`cont2' versus `cont1'")
    graph export "`outdir'/scatter_`cont2'_vs_`cont1'.png", replace width(1800)
}

*******************************************************
* End of file
*******************************************************
