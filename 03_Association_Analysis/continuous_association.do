*******************************************************
* Medical Data Analysis using Stata
* File: continuous_association.do
* Purpose: Reproducible continuous-variable analysis
*******************************************************

clear all
set more off

*======================================================*
* 1. LOAD DATA
*======================================================*
* use "data/cleaned_dataset.dta", clear

*======================================================*
* 2. DESCRIPTIVE STATISTICS
*======================================================*
* summarize age bmi, detail

*======================================================*
* 3. TWO-GROUP COMPARISON
*======================================================*
* Parametric: t test
* ttest age, by(outcome)
* ttest bmi, by(outcome)

* Non-parametric: Mann-Whitney/Wilcoxon rank-sum
* ranksum age, by(outcome)
* ranksum bmi, by(outcome)

*======================================================*
* 4. THREE OR MORE GROUPS
*======================================================*
* One-way ANOVA
* oneway age age_group, tabulate

* Kruskal-Wallis test
* kwallis bmi, by(age_group)

*======================================================*
* 5. CORRELATION
*======================================================*
* Pearson
* pwcorr age bmi, sig obs

* Spearman
* spearman age bmi

*======================================================*
* 6. BASIC ASSUMPTION CHECKS
*======================================================*
* Histogram / normality assessment
* histogram age, normal
* qnorm age
* swilk age

*======================================================*
* 7. REPORTING RULE
*======================================================*
* Approximately symmetric continuous data: mean (SD)
* Skewed continuous data: median (IQR)
* Always report N and missing observations.
* Do not choose tests solely from p-values; consider
* distribution, study design and clinical context.

*******************************************************
* End of file
*******************************************************
