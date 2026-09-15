import io
import json
import threading
import time
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from . import dummy_table_fill as dummy_engine
from .dummy_table_fill import fill_dummy_table
from .dummy_docx import docx_dummy_to_xlsx
from .data_intelligence import profile_multiple_workbooks, validate_variable_confirmations
from .workflow_engine import read_dataset, data_quality_plus, diagnostic_validated, roc_validated
from .analysis_engine import robust_poisson, logistic_regression

router = APIRouter(prefix="/api/v1/jobs", tags=["analysis-progress"])
_jobs = {}
_lock = threading.Lock()


def _log(job_id, message, level="INFO"):
    entry = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "level": level, "message": message}
    with _lock:
        job = _jobs.get(job_id)
        if job:
            job.setdefault("logs", []).append(entry)
            job["logs"] = job["logs"][-200:]


def _set(job_id, **updates):
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].update(updates)


def _stage(job_id, percent, stage, message, started):
    elapsed = max(0.0, time.time() - started)
    eta = round(elapsed * (100 - percent) / percent, 1) if 0 < percent < 100 else None
    _set(job_id, percent=percent, stage=stage, eta_seconds=eta, elapsed_seconds=round(elapsed, 1))
    _log(job_id, message)


def _apply_manual_mappings(manual_mapping, dataset_columns):
    """Temporarily force dummy-table variable labels to the user's exact columns."""
    if not manual_mapping:
        return {}
    missing = [column for column in manual_mapping.values() if column not in dataset_columns]
    if missing:
        raise ValueError(f"Manual mapping refers to dataset variable(s) not found: {', '.join(missing)}")
    backups = {}
    for dummy_variable, dataset_variable in manual_mapping.items():
        canonical = dummy_engine._canonical_variable(dummy_variable)
        backups[canonical] = list(dummy_engine.VARIABLE_ALIASES.get(canonical, []))
        aliases = list(dummy_engine.VARIABLE_ALIASES.get(canonical, []))
        if dataset_variable not in aliases:
            aliases.insert(0, dataset_variable)
        dummy_engine.VARIABLE_ALIASES[canonical] = aliases
    return backups


def _restore_manual_mappings(backups):
    for canonical, aliases in backups.items():
        dummy_engine.VARIABLE_ALIASES[canonical] = aliases


def _manual_only_finder(manual_mapping, dataset_columns):
    """Return a finder that honours ONLY variables explicitly mapped by the user.

    This prevents automatic alias/category matching from silently filling rows that the
    user intentionally left unmapped in the Variable Matching report.
    """
    canonical_mapping = {
        dummy_engine._canonical_variable(k): v for k, v in (manual_mapping or {}).items()
    }

    def finder(df, variable, categories=None):
        canonical = dummy_engine._canonical_variable(variable)
        selected = canonical_mapping.get(canonical)
        if selected and selected in df.columns:
            return selected, 1.0
        return None, 0.0

    return finder


def _excel_sheet_columns(content):
    """Return {sheet: set(columns)} for every readable Excel worksheet."""
    book = pd.ExcelFile(io.BytesIO(content))
    result = {}
    for sheet in book.sheet_names:
        try:
            probe = pd.read_excel(io.BytesIO(content), sheet_name=sheet, nrows=5)
            result[sheet] = {str(c) for c in probe.columns if not str(c).startswith("Unnamed:")}
        except Exception:
            result[sheet] = set()
    return result


def _choose_excel_sheet(content, required_columns):
    """Choose the best worksheet without failing because some mapped variables are elsewhere."""
    sheets = _excel_sheet_columns(content)
    if not sheets:
        return None, set()
    required = {str(x).strip() for x in required_columns if str(x).strip()}
    if not required:
        sheet = next(iter(sheets))
        return sheet, sheets[sheet]
    ranked = sorted(
        ((sheet, len(required & cols), len(cols), cols) for sheet, cols in sheets.items()),
        key=lambda x: (x[1], x[2]),
        reverse=True,
    )
    best = ranked[0]
    return best[0], best[3]


def _prepare_sheet_aware_datasets(datasets, names, manual_mapping, outcome):
    """Materialise the outcome/analysis worksheet without rejecting partial mappings.

    The outcome sheet is the primary row-level dataset. Variables that were manually mapped
    but are not present on that sheet are reported as skipped instead of causing the whole job
    to fail. This is safer than inventing row alignment across unrelated worksheets.
    """
    required = [outcome] if outcome else []
    if not required:
        return datasets, names, [None] * len(names)

    prepared, prepared_names, selected_sheets = [], [], []
    for content, name in zip(datasets, names):
        ext = name.lower().rsplit('.', 1)[-1]
        if ext not in ('xlsx', 'xls', 'xlsm'):
            prepared.append(content)
            prepared_names.append(name)
            selected_sheets.append(None)
            continue
        sheet, _ = _choose_excel_sheet(content, required)
        if not sheet:
            raise ValueError(f"Could not find the selected outcome variable in any worksheet of {name}.")
        df = pd.read_excel(io.BytesIO(content), sheet_name=sheet)
        output = io.BytesIO()
        df.to_excel(output, index=False, sheet_name='AnalysisData')
        prepared.append(output.getvalue())
        prepared_names.append(name.rsplit('.', 1)[0] + '_AnalysisData.xlsx')
        selected_sheets.append(sheet)
    return prepared, prepared_names, selected_sheets


def _worker(job_id, datasets, names, dummy, dummy_name, outcome, positive, adjustments, manual_mapping):
    started = time.time()
    mapping_backups = {}
    original_finder = dummy_engine._find_dataset_column
    try:
        _set(job_id, status="running")
        _log(job_id, f"Background worker started for job {job_id[:8]}")
        _log(job_id, f"Received {len(datasets)} dataset file(s): {', '.join(names)}")
        if manual_mapping:
            _log(job_id, f"Manual variable mappings received: {len(manual_mapping)}")
        else:
            _log(job_id, "No manual variable mappings supplied; automatic matching is enabled")
        _stage(job_id, 5, "Reading uploaded files", "Reading uploaded dataset files and dummy table", started)
        time.sleep(0.05)
        _log(job_id, f"Dummy table: {dummy_name}")
        _stage(job_id, 15, "Parsing dataset and dummy table", "Parsing columns, rows, variables and dummy-table structure", started)
        time.sleep(0.05)

        analysis_datasets, analysis_names, selected_sheets = _prepare_sheet_aware_datasets(
            datasets, names, manual_mapping, outcome
        )
        if any(selected_sheets):
            readable = ', '.join(f"{name}: {sheet}" for name, sheet in zip(names, selected_sheets) if sheet)
            _log(job_id, f"Excel sheet selected for row-level analysis: {readable}")

        dataset_columns = set()
        for content, name in zip(analysis_datasets, analysis_names):
            dataset_columns.update(str(c) for c in read_dataset(name, content).columns)

        if manual_mapping:
            # Validate against the actual analysis dataset, but do not fail the job for a
            # mapping that belongs to another worksheet. That mapping will simply be skipped.
            available = {column for column in manual_mapping.values() if column in dataset_columns}
            skipped = [column for column in manual_mapping.values() if column not in dataset_columns]
            if skipped:
                _log(job_id, f"Skipped mapped variable(s) not available on the selected analysis sheet: {', '.join(skipped)}", "WARNING")
            effective_mapping = {k: v for k, v in manual_mapping.items() if v in available}
            mapping_backups = _apply_manual_mappings(effective_mapping, dataset_columns)
            dummy_engine._find_dataset_column = _manual_only_finder(effective_mapping, dataset_columns)
            _log(job_id, f"Manual mappings applied as authoritative selection: {len(effective_mapping)}")
        else:
            effective_mapping = {}

        engine_dummy = dummy
        engine_dummy_name = dummy_name
        if dummy_name.lower().endswith(".docx"):
            _log(job_id, "DOCX dummy table detected; converting first Word table to an in-memory Excel template")
            engine_dummy = docx_dummy_to_xlsx(dummy)
            engine_dummy_name = dummy_name.rsplit('.', 1)[0] + '.xlsx'

        output, meta = fill_dummy_table(
            analysis_datasets,
            analysis_names,
            engine_dummy,
            engine_dummy_name,
            outcome=outcome or None,
            outcome_positive=positive or None,
            adjustment_variables=adjustments or None,
        )
        if selected_sheets and any(selected_sheets):
            meta["analysis_sheets"] = [
                {"dataset": name, "sheet": sheet} for name, sheet in zip(names, selected_sheets) if sheet
            ]
        if manual_mapping:
            meta["variable_mappings"] = [
                {"dummy_variable": dummy_variable, "dataset_variable": dataset_variable, "confidence": 1.0 if dataset_variable in dataset_columns else 0.0, "source": "manual", "status": "applied" if dataset_variable in dataset_columns else "skipped"}
                for dummy_variable, dataset_variable in manual_mapping.items()
            ]
        _log(job_id, "Dataset parsing and statistical table generation completed")
        _stage(job_id, 90, "Generating filled Excel result", "Building the final filled Excel workbook", started)
        time.sleep(0.05)
        elapsed = round(time.time() - started, 1)
        _set(job_id, status="completed", percent=100, stage="Analysis complete", eta_seconds=0, output=output, filename=dummy_name.rsplit('.', 1)[0] + '_filled.xlsx', meta=meta, elapsed_seconds=elapsed)
        _log(job_id, f"Analysis completed successfully in {elapsed}s", "SUCCESS")
    except Exception as exc:
        elapsed = round(time.time() - started, 1)
        _set(job_id, status="failed", percent=100, stage="Analysis failed", error=str(exc), elapsed_seconds=elapsed, eta_seconds=0)
        _log(job_id, f"Analysis failed after {elapsed}s: {exc}", "ERROR")
    finally:
        dummy_engine._find_dataset_column = original_finder
        _restore_manual_mappings(mapping_backups)


@router.post("/dummy-table/start")
async def start_dummy_job(background_tasks: BackgroundTasks, dataset: list[UploadFile] = File(...), dummy_table: UploadFile = File(...), outcome: str = Form(''), outcome_positive: str = Form(''), adjustment_variables: str = Form(''), manual_variable_mapping: str = Form('')):
    job_id = uuid.uuid4().hex
    datasets, names = [], []
    for upload in dataset:
        datasets.append(await upload.read()); names.append(upload.filename or 'upload.csv')
    dummy = await dummy_table.read()
    positive = [x.strip() for x in outcome_positive.split(',') if x.strip()]
    adjustments = [x.strip() for x in adjustment_variables.split(',') if x.strip()]
    try:
        parsed_mapping = json.loads(manual_variable_mapping) if manual_variable_mapping.strip() else {}
        if not isinstance(parsed_mapping, dict):
            raise ValueError('manual_variable_mapping must be a JSON object')
        parsed_mapping = {str(k).strip(): str(v).strip() for k, v in parsed_mapping.items() if str(k).strip() and str(v).strip()}
    except json.JSONDecodeError as exc:
        raise HTTPException(422, f'Invalid manual variable mapping JSON: {exc}') from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    with _lock:
        _jobs[job_id] = {'job_id': job_id, 'status': 'queued', 'percent': 0, 'stage': 'Queued for analysis', 'eta_seconds': None, 'elapsed_seconds': 0, 'error': None, 'logs': []}
    _log(job_id, "Analysis job queued")
    _log(job_id, f"Outcome: {outcome.strip() or 'auto-detect'}")
    _log(job_id, f"Positive values: {', '.join(positive) if positive else 'auto-detect'}")
    _log(job_id, f"Adjusted RR covariates: {', '.join(adjustments) if adjustments else 'none'}")
    background_tasks.add_task(_worker, job_id, datasets, names, dummy, dummy_table.filename or 'dummy.xlsx', outcome.strip(), positive, adjustments, parsed_mapping)
    return {'job_id': job_id, 'status': 'queued', 'percent': 0, 'stage': 'Queued for analysis'}


@router.post("/data-intelligence")
async def data_intelligence(files: list[UploadFile] = File(...)):
    if not files: raise HTTPException(422, 'Upload at least one Excel workbook')
    if len(files) > 10: raise HTTPException(422, 'Maximum 10 workbooks per inspection')
    payload=[]
    for upload in files:
        name=upload.filename or 'workbook.xlsx'
        if not name.lower().endswith(('.xlsx','.xls','.xlsm')): raise HTTPException(422, f'Unsupported workbook: {name}. Use XLSX, XLS or XLSM.')
        payload.append((name, await upload.read()))
    try: return profile_multiple_workbooks(payload)
    except Exception as exc: raise HTTPException(422, f'Unable to inspect workbook(s): {exc}') from exc


@router.post("/validate-variable-contract")
async def validate_variable_contract(payload: dict):
    try:
        confirmations=payload.get('confirmations') if isinstance(payload,dict) else None
        return validate_variable_confirmations(confirmations)
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc


@router.post("/workflow/quality")
async def workflow_quality(file: UploadFile = File(...), id_variables: str = Form('')):
    try:
        df=read_dataset(file.filename or 'upload.csv', await file.read()); ids=[x.strip() for x in id_variables.split(',') if x.strip()]
        return {'method':'enhanced_data_quality','results':data_quality_plus(df,ids)}
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc


@router.post("/workflow/diagnostic")
async def workflow_diagnostic(file: UploadFile = File(...), index_test: str = Form(...), reference_standard: str = Form(...), index_positive: str = Form(...), reference_positive: str = Form(...), index_negative: str = Form(''), reference_negative: str = Form('')):
    try:
        df=read_dataset(file.filename or 'upload.csv', await file.read()); parse=lambda s:[x.strip() for x in s.split(',') if x.strip()]
        return {'method':'validated_diagnostic_accuracy','results':diagnostic_validated(df,index_test,reference_standard,parse(index_positive),parse(reference_positive),parse(index_negative),parse(reference_negative))}
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc


@router.post("/workflow/roc")
async def workflow_roc(file: UploadFile = File(...), test: str = Form(...), outcome: str = Form(...), positive_values: str = Form(...)):
    try:
        df=read_dataset(file.filename or 'upload.csv', await file.read()); return {'method':'validated_roc_auc','results':roc_validated(df,test,outcome,[x.strip() for x in positive_values.split(',') if x.strip()])}
    except ValueError as exc: raise HTTPException(422,str(exc)) from exc


@router.post("/workflow/regression")
async def workflow_regression(file: UploadFile = File(...), config: str = Form(...)):
    try:
        cfg=json.loads(config); df=read_dataset(file.filename or 'upload.csv', await file.read()); kind=cfg.get('model','poisson'); fn=robust_poisson if kind=='poisson' else logistic_regression
        result=fn(df,cfg['outcome'],cfg.get('predictors',[]),cfg.get('categorical_predictors',[]),cfg.get('reference_categories',{}))
        return {'method':kind,'results':result}
    except (ValueError, KeyError, json.JSONDecodeError, np.linalg.LinAlgError) as exc: raise HTTPException(422,str(exc)) from exc


@router.get("/{job_id}")
def job_status(job_id: str):
    with _lock:
        job=_jobs.get(job_id)
        if not job: raise HTTPException(404,'Analysis job not found')
        return {k:v for k,v in job.items() if k!='output'}


@router.get("/{job_id}/logs")
def job_logs(job_id: str):
    with _lock:
        job=_jobs.get(job_id)
        if not job: raise HTTPException(404,'Analysis job not found')
        return {'job_id':job_id,'status':job.get('status'),'logs':list(job.get('logs',[]))}


@router.get("/{job_id}/result")
def job_result(job_id: str):
    with _lock:
        job=_jobs.get(job_id)
        if not job: raise HTTPException(404,'Analysis job not found')
        if job.get('status')!='completed': raise HTTPException(409,'Analysis is not complete yet')
        return {'job_id':job_id,'status':job['status'],'filename':job['filename'],'elapsed_seconds':job.get('elapsed_seconds'),'meta':job.get('meta',{})}


@router.get("/{job_id}/download")
def job_download(job_id: str):
    with _lock:
        job=_jobs.get(job_id)
        if not job: raise HTTPException(404,'Analysis job not found')
        if job.get('status')!='completed': raise HTTPException(409,'Analysis is not complete yet')
        output,filename=job['output'],job['filename']
    return StreamingResponse(io.BytesIO(output),media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':f'attachment; filename="{filename}"'})
