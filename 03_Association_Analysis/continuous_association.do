*******************************************************
* Medical Data Analysis using Stata
* File: continuous_association.do
* Purpose: Analysis of continuous variables
*******************************************************

clear all
set more off

*------------------------------------------------------*
* 1. Load cleaned dataset
*------------------------------------------------------*

* use "data/cleaned_dataset.dta", clear

*------------------------------------------------------*
* 2. Descriptive statistics
*------------------------------------------------------*

* summarize age, detail
* summarize bmi, detail

*------------------------------------------------------*
* 3. Compare continuous variables between 2 groups
*------------------------------------------------------*

* ttest age, by(outcome)
* ttest bmi, by(outcome)

*------------------------------------------------------*
* 4. Non-parametric test
*------------------------------------------------------*

* Mann-Whitney U test
* ranksum age, by(outcome)
* ranksum bmi, by(outcome)

*------------------------------------------------------*
* 5. Compare across 3 or more groups
*------------------------------------------------------*

* One-way ANOVA
* oneway age age_group

*------------------------------------------------------*
* 6. Kruskal-Wallis test
*------------------------------------------------------*

* kwallis bmi, by(age_group)

*------------------------------------------------------*
* 7. Correlation
*------------------------------------------------------*

* Pearson correlation
* pwcorr age bmi, sig

* Spearman correlation
* spearman age bmi

*******************************************************
* End of file
*******************************************************
