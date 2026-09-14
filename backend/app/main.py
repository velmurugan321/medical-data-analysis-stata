from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import io
import json
import numpy as np
import pandas as pd
from .analysis_engine import (
    descriptive, categorical_association, diagnostic_accuracy, roc_auc,
    robust_poisson, logistic_regression, table_one, data_quality,
)
from .openeepi_engine import screening as openeepi_screening

app = FastAPI(title="Medical Data Analysis API", version="0.5.0")
ALLOWED_SUFFIXES = {".csv", ".xlsx", ".xls", ".dta", ".tsv"}
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

def load_dataframe(filename: str, content: bytes) -> pd.DataFrame:
    name = filename.lower(); suffix = next((s for s in ALLOWED_SUFFIXES if name.endswith(s)), None)
    if suffix is None: raise HTTPException(400, "Unsupported file type. Use CSV, XLSX, XLS, DTA or TSV.")
    try:
        if suffix == ".csv": return pd.read_csv(io.BytesIO(content))
        if suffix == ".tsv": return pd.read_csv(io.BytesIO(content), sep="\t")
        if suffix in {".xlsx", ".xls"}: return pd.read_excel(io.BytesIO(content))
        return pd.read_stata(io.BytesIO(content))
    except Exception as exc: raise HTTPException(422, f"Unable to read dataset: {exc}") from exc

def variable_metadata(df):
    rows=[]
    for col in df.columns:
        s=df[col]; numeric=pd.api.types.is_numeric_dtype(s)
        rows.append({"name":str(col),"type":"numeric" if numeric else "categorical","storage_type":str(s.dtype),"n":int(s.notna().sum()),"missing":int(s.isna().sum()),"unique":int(s.nunique(dropna=True)),"min":float(s.min()) if numeric and s.notna().any() else None,"max":float(s.max()) if numeric and s.notna().any() else None})
    return rows

@app.get("/health")
def health(): return {"status":"ok","service":"medical-data-analysis-api","version":app.version}

@app.post("/api/v1/data/inspect")
async def inspect_data(file: UploadFile=File(...)):
    df=load_dataframe(file.filename or "upload.csv",await file.read()); return {"filename":file.filename,"rows":int(df.shape[0]),"columns":int(df.shape[1]),"variables":variable_metadata(df)}

@app.post("/api/v1/analysis/descriptive")
async def descriptive_endpoint(file:UploadFile=File(...),variables:str=""):
    df=load_dataframe(file.filename or "upload.csv",await file.read()); selected=[x.strip() for x in variables.split(",") if x.strip()]
    if not selected: raise HTTPException(422,"Select at least one variable")
    try:return {"method":"descriptive","results":descriptive(df,selected)}
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc

@app.post("/api/v1/analysis/association")
async def association_endpoint(file:UploadFile=File(...),variable:str="",outcome:str=""):
    df=load_dataframe(file.filename or "upload.csv",await file.read())
    try:return {"method":"chi_square_fisher","results":categorical_association(df,variable,outcome)}
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc

@app.post("/api/v1/analysis/diagnostic")
async def diagnostic_endpoint(file:UploadFile=File(...),index_test:str="",reference_standard:str=""):
    df=load_dataframe(file.filename or "upload.csv",await file.read())
    try:return {"method":"diagnostic_accuracy","results":diagnostic_accuracy(df,index_test,reference_standard)}
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc

@app.post("/api/v1/analysis/roc")
async def roc_endpoint(file:UploadFile=File(...),test:str="",outcome:str=""):
    df=load_dataframe(file.filename or "upload.csv",await file.read())
    try:return {"method":"roc_auc","results":roc_auc(df,test,outcome)}
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc

@app.post("/api/v1/openeepi/screening")
async def openeepi_screening_endpoint(config:str=Form(...)):
    try:
        cfg=json.loads(config); result=openeepi_screening(cfg["tp"],cfg["fp"],cfg["fn"],cfg["tn"])
        return {"method":"OpenEpi screening","results":result}
    except KeyError as exc: raise HTTPException(422,f"Missing screening cell: {exc.args[0]}") from exc
    except (ValueError,TypeError,json.JSONDecodeError) as exc: raise HTTPException(422,str(exc)) from exc

@app.post("/api/v1/analysis/poisson")
async def poisson_endpoint(file:UploadFile=File(...),config:str=Form(...)):
    try:
        cfg=json.loads(config); df=load_dataframe(file.filename or "upload.csv",await file.read())
        return {"method":"robust_poisson_rr","results":robust_poisson(df,cfg["outcome"],cfg.get("predictors",[]),cfg.get("categorical_predictors",[]),cfg.get("reference_categories",{}))}
    except KeyError as exc:raise HTTPException(422,f"Missing Poisson configuration field: {exc.args[0]}") from exc
    except (ValueError,np.linalg.LinAlgError,json.JSONDecodeError) as exc:raise HTTPException(422,str(exc)) from exc

@app.post("/api/v1/analysis/logistic")
async def logistic_endpoint(file:UploadFile=File(...),config:str=Form(...)):
    try:
        cfg=json.loads(config); df=load_dataframe(file.filename or "upload.csv",await file.read())
        return {"method":"logistic_regression","results":logistic_regression(df,cfg["outcome"],cfg.get("predictors",[]),cfg.get("categorical_predictors",[]),cfg.get("reference_categories",{}))}
    except KeyError as exc:raise HTTPException(422,f"Missing logistic configuration field: {exc.args[0]}") from exc
    except (ValueError,np.linalg.LinAlgError,json.JSONDecodeError) as exc:raise HTTPException(422,str(exc)) from exc

@app.post("/api/v1/analysis/table-one")
async def table_one_endpoint(file:UploadFile=File(...),variables:str="",group:str=""):
    df=load_dataframe(file.filename or "upload.csv",await file.read()); selected=[x.strip() for x in variables.split(",") if x.strip()]
    if not selected: raise HTTPException(422,"Select at least one variable")
    try:return {"method":"table_one","results":table_one(df,selected,group.strip() or None)}
    except ValueError as exc:raise HTTPException(422,str(exc)) from exc

@app.post("/api/v1/data/quality")
async def quality_endpoint(file:UploadFile=File(...)):
    df=load_dataframe(file.filename or "upload.csv",await file.read()); return {"method":"data_quality","results":data_quality(df)}
