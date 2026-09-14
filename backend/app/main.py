from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
import io
import pandas as pd

app = FastAPI(title="Medical Data Analysis API", version="0.1.0")

ALLOWED_SUFFIXES = {".csv", ".xlsx", ".xls", ".dta", ".tsv"}


def load_dataframe(filename: str, content: bytes) -> pd.DataFrame:
    name = filename.lower()
    suffix = next((s for s in ALLOWED_SUFFIXES if name.endswith(s)), None)
    if suffix is None:
        raise HTTPException(400, "Unsupported file type. Use CSV, XLSX, XLS, DTA or TSV.")
    try:
        if suffix == ".csv":
            return pd.read_csv(io.BytesIO(content))
        if suffix == ".tsv":
            return pd.read_csv(io.BytesIO(content), sep="\t")
        if suffix in {".xlsx", ".xls"}:
            return pd.read_excel(io.BytesIO(content))
        return pd.read_stata(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(422, f"Unable to read dataset: {exc}") from exc


def variable_metadata(df: pd.DataFrame) -> list[dict]:
    rows = []
    for col in df.columns:
        s = df[col]
        numeric = pd.api.types.is_numeric_dtype(s)
        rows.append({
            "name": str(col),
            "type": "numeric" if numeric else "categorical",
            "storage_type": str(s.dtype),
            "n": int(s.notna().sum()),
            "missing": int(s.isna().sum()),
            "unique": int(s.nunique(dropna=True)),
            "min": float(s.min()) if numeric and s.notna().any() else None,
            "max": float(s.max()) if numeric and s.notna().any() else None,
        })
    return rows


@app.get("/health")
def health():
    return {"status": "ok", "service": "medical-data-analysis-api"}


@app.post("/api/v1/data/inspect")
async def inspect_data(file: UploadFile = File(...)):
    content = await file.read()
    df = load_dataframe(file.filename or "upload.csv", content)
    return {
        "filename": file.filename,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "variables": variable_metadata(df),
    }


class PoissonRequest(BaseModel):
    outcome: str
    predictors: list[str] = Field(default_factory=list)
    reference_categories: dict[str, str | int | float] = Field(default_factory=dict)


@app.post("/api/v1/analysis/poisson")
def poisson_placeholder(request: PoissonRequest):
    return {
        "status": "validation_ready",
        "method": "robust_poisson_rr",
        "outcome": request.outcome,
        "predictors": request.predictors,
        "reference_categories": request.reference_categories,
        "message": "Statistical execution will be enabled after dataset/session binding and validated model checks."
    }
