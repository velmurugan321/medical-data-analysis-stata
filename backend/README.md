# Medical Data Analysis Backend

Production architecture foundation for the medical statistical analysis platform.

## Planned stack
- Python 3.11+
- FastAPI
- pandas / NumPy
- SciPy / statsmodels
- openpyxl / pyarrow where required

## API flow
1. Upload CSV/XLSX/DTA/TSV.
2. Validate file and schema.
3. Generate variable metadata.
4. Run data-quality checks.
5. Execute validated statistical modules.
6. Return structured results for the frontend.
7. Export tables and graphs.

## Statistical rule
The frontend must never calculate statistical results. All calculations, validation and confidence intervals belong in the backend analysis engine.
