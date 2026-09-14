*******************************************************
* Medical Data Analysis using Stata
* File: export_results.do
* Canonical output-export entry point
*******************************************************

* The maintained implementation currently lives in
* 07_Output/07_Output/export_results.do.
* Keep this file as the stable entry point while the
* repository structure is being consolidated.

capture noisily do "07_Output/07_Output/export_results.do"
if _rc {
    di as error "Unable to run the maintained export workflow."
    exit _rc
}

*******************************************************
* End of file
*******************************************************
