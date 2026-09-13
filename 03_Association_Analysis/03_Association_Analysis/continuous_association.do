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
* 3. Compare continuous variable between 2 groups
*------------------------------------------------------*

* Example: Age by outcome
* ttest age, by(outcome)

* Example: BMI by outcome
* ttest bmi, by(outcome)

*------------------------------------------------------*
* 4. Non-parametric comparison
*------------------------------------------------------*

* Mann-Whitney U test
* ranksum age, by(outcome)
* ranksum bmi, by(outcome)

*------------------------------------------------------*
* 5. Compare continuous variable across 3 or more groups
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
