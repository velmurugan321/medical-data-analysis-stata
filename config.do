*******************************************************
* Medical Data Analysis using Stata
* File: config.do
* Purpose: Central project configuration
*******************************************************

clear all
set more off

*------------------------------------------------------*
* Project information
*------------------------------------------------------*

global PROJECT_NAME "Medical Data Analysis"
global AUTHOR "Velmurugan"

*------------------------------------------------------*
* Folder paths
*------------------------------------------------------*

global DATA_DIR   "data"
global OUTPUT_DIR "07_Output"
global GRAPH_DIR  "06_Visualization"

*------------------------------------------------------*
* Dataset
*------------------------------------------------------*

* Dataset path will be added later
* global DATASET "$DATA_DIR/cleaned_dataset.dta"

*------------------------------------------------------*
* Output files
*------------------------------------------------------*

global LOGFILE "$OUTPUT_DIR/analysis_results.log"

*******************************************************
* End of configuration
*******************************************************
