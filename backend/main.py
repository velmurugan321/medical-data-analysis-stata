from __future__ import annotations

import os
import tempfile
from typing import Any

import pandas as pd
import pyreadstat
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Medical Data Analysis Stata Engine", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    if pd.isna(value):
        return None
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "status": "online",
        "service": "Medical Data Analysis Stata Engine",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "stata_read": "/stata/read",
        },
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/stata/read")
async def read_stata(file: UploadFile = File(...)) -> dict[str, Any]:
    name = file.filename or "dataset.dta"
    if not name.lower().endswith(".dta"):
        raise HTTPException(status_code=400, detail="Only Stata .dta files are accepted by this endpoint.")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".dta") as tmp:
        tmp.write(data)
        temp_path = tmp.name

    try:
        df, meta = pyreadstat.read_dta(temp_path, apply_value_formats=False)
        columns = []
        for col in df.columns:
            variable_label = meta.column_names_to_labels.get(col, "")
            format_value = meta.original_variable_types.get(col, "")
            value_label_name = meta.variable_to_label.get(col, "")
            value_labels = meta.variable_value_labels.get(value_label_name, {}) if value_label_name else {}
            values = df[col]
            non_missing = values.dropna()
            columns.append(
                {
                    "name": col,
                    "label": variable_label,
                    "stataFormat": format_value,
                    "valueLabel": value_label_name,
                    "valueLabels": {str(k): str(v) for k, v in value_labels.items()},
                    "type": str(values.dtype),
                    "missing": int(values.isna().sum()),
                    "unique": int(non_missing.nunique(dropna=True)),
                }
            )

        records = [
            {str(k): _json_value(v) for k, v in row.items()}
            for row in df.to_dict(orient="records")
        ]
        return {
            "fileName": name,
            "rows": len(df),
            "variables": len(df.columns),
            "columns": columns,
            "data": records,
            "stata": {
                "fileLabel": meta.file_label or "",
                "fileFormat": getattr(meta, "file_format", None),
                "notes": getattr(meta, "notes", []) or [],
            },
        }
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Unable to read Stata dataset: {exc}") from exc
    finally:
        try:
            os.remove(temp_path)
        except OSError:
            pass
