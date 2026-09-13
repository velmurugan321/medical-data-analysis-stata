*******************************************************
* Medical Data Analysis using Stata
* File: run_all.do
* Purpose: Run complete analysis workflow
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load project configuration
*------------------------------------------------------*

do "config.do"

*------------------------------------------------------*
* 2. Data Management
*------------------------------------------------------*

do "01_Data_Management/data_cleaning.do"
do "01_Data_Management/variable_creation.do"
do "01_Data_Management/missing_data.do"

*------------------------------------------------------*
* 3. Descriptive Analysis
*------------------------------------------------------*

do "02_Descriptive_Analysis/demographics.do"
do "02_Descriptive_Analysis/table1.do"

*------------------------------------------------------*
* 4. Association Analysis
*------------------------------------------------------*

do "03_Association_Analysis/categorical_association.do"
do "03_Association_Analysis/continuous_association.do"

*------------------------------------------------------*
* 5. Regression Analysis
*------------------------------------------------------*

do "04_Regression/poisson_regression.do"
do "04_Regression/risk_ratio_analysis.do"

*------------------------------------------------------*
* 6. Diagnostic Analysis
*------------------------------------------------------*

do "05_Diagnostic_Analysis/diagnostic_accuracy.do"
do "05_Diagnostic_Analysis/roc_auc.do"

*------------------------------------------------------*
* 7. Visualization
*------------------------------------------------------*

do "06_Visualization/graphs.do"
do "06_Visualization/roc_graph.do"

*******************************************************
* End of complete analysis workflow
*******************************************************
