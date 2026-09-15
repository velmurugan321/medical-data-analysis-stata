import io
import json
import threading
import time
import uuid
from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from .dummy_table_fill import fill_dummy_table

router = APIRouter(prefix="/api/v1/jobs", tags=["analysis-progress"])
_jobs = {}
_lock = threading.Lock()


def _set(job_id, **updates):
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].update(updates)


def _worker(job_id, datasets, names, dummy, dummy_name, outcome, positive, adjustments):
    started = time.time()
    try:
        _set(job_id, status="running", percent=5, stage="Reading uploaded files", eta_seconds=None)
        time.sleep(0.05)
        _set(job_id, percent=15, stage="Parsing dataset and dummy table")
        output, meta = fill_dummy_table(
            datasets, names, dummy, dummy_name,
            outcome=outcome or None,
            outcome_positive=positive or None,
            adjustment_variables=adjustments or None,
        )
        _set(job_id, percent=90, stage="Generating filled Excel result")
        time.sleep(0.05)
        _set(job_id, status="completed", percent=100, stage="Analysis complete", eta_seconds=0,
             output=output, filename=dummy_name.rsplit('.', 1)[0] + '_filled.xlsx', meta=meta,
             elapsed_seconds=round(time.time() - started, 1))
    except Exception as exc:
        _set(job_id, status="failed", percent=100, stage="Analysis failed", error=str(exc),
             elapsed_seconds=round(time.time() - started, 1))


@router.post("/dummy-table/start")
async def start_dummy_job(
    background_tasks: BackgroundTasks,
    dataset: list[UploadFile] = File(...),
    dummy_table: UploadFile = File(...),
    outcome: str = Form(''),
    outcome_positive: str = Form(''),
    adjustment_variables: str = Form(''),
):
    job_id = uuid.uuid4().hex
    datasets, names = [], []
    for upload in dataset:
        datasets.append(await upload.read())
        names.append(upload.filename or 'upload.csv')
    dummy = await dummy_table.read()
    positive = [x.strip() for x in outcome_positive.split(',') if x.strip()]
    adjustments = [x.strip() for x in adjustment_variables.split(',') if x.strip()]
    with _lock:
        _jobs[job_id] = {
            'job_id': job_id, 'status': 'queued', 'percent': 0,
            'stage': 'Queued for analysis', 'eta_seconds': None,
            'elapsed_seconds': 0, 'error': None,
        }
    background_tasks.add_task(_worker, job_id, datasets, names, dummy, dummy_table.filename or 'dummy.xlsx',
                              outcome.strip(), positive, adjustments)
    return {'job_id': job_id, 'status': 'queued', 'percent': 0, 'stage': 'Queued for analysis'}


@router.get("/{job_id}")
def job_status(job_id: str):
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            raise HTTPException(404, 'Analysis job not found')
        return {k: v for k, v in job.items() if k != 'output'}


@router.get("/{job_id}/download")
def job_download(job_id: str):
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            raise HTTPException(404, 'Analysis job not found')
        if job.get('status') != 'completed':
            raise HTTPException(409, 'Analysis is not complete yet')
        output = job['output']
        filename = job['filename']
    return StreamingResponse(io.BytesIO(output), media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                             headers={'Content-Disposition': f'attachment; filename="{filename}"'})
