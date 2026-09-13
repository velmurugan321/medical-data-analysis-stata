# Stata Coding Standards

## 1. General Rules

- Use `clear all` at the beginning of analysis scripts.
- Use `set more off`.
- Use clear and descriptive variable names.
- Add comments to explain important analysis steps.
- Keep one major analysis task per `.do` file.
- Do not store patient-identifiable information in the repository.

## 2. Variable Naming

Use lowercase variable names whenever possible.

Examples:

- `age`
- `sex`
- `bmi`
- `outcome`
- `age_group`
- `bmi_group`

Avoid unclear names such as:

- `x1`
- `var1`
- `abc`

## 3. Variable Creation

Always check the original variable before creating a new variable.

Example:

```stata
tab age, missing
summarize age, detail
