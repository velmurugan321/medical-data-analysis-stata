# Data

This folder is reserved for study datasets used in Stata analysis.

## Data workflow

1. Raw data
2. Cleaned data
3. Analysis dataset

## Important privacy rule

Patient-level, identifiable, confidential, or sensitive medical data must NOT be uploaded to this public GitHub repository.

Examples of files that should not be uploaded:

- `.dta`
- `.xlsx`
- `.csv`
- `.sav`
- `.sas7bdat`

These file types are excluded through the repository `.gitignore`.

## Recommended local data structure

```text
data/
├── raw/
├── cleaned/
└── analysis/
