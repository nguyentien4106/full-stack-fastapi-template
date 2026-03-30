from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Nested models
# ---------------------------------------------------------------------------

class ExtractProgress(BaseModel):
    totalPages: int | None = None
    extractedPages: int
    startTime: str | None = None
    endTime: str | None = None


class ResultUrl(BaseModel):
    jsonUrl: str | None = None
    markdownUrl: str | None = None


# ---------------------------------------------------------------------------
# Submit-job response (POST /jobs)
# ---------------------------------------------------------------------------

class OcrSubmitData(BaseModel):
    jobId: str


class OcrSubmitResponse(BaseModel):
    traceId: str | None = None
    code: int | None = None
    msg: str | None = None
    data: OcrSubmitData


# ---------------------------------------------------------------------------
# Job-level response (GET /jobs/{jobId})
# ---------------------------------------------------------------------------

class OcrJobData(BaseModel):
    jobId: str
    state: str  # OcrJobStatus values: pending | running | done | failed
    extractProgress: ExtractProgress | None = None
    resultUrl: ResultUrl | None = None
    errorMsg: str | None = None


class OcrJobResponse(BaseModel):
    traceId: str | None = None
    code: int | None = None
    msg: str | None = None
    data: OcrJobData


# ---------------------------------------------------------------------------
# Batch-job response (GET /jobs/batch/{batchId})
# ---------------------------------------------------------------------------

class OcrBatchExtractResult(BaseModel):
    jobId: str
    state: str  # pending | running | done | failed
    extractProgress: ExtractProgress | None = None
    resultUrl: ResultUrl | None = None
    errorMsg: str | None = None


class OcrBatchData(BaseModel):
    batchId: str
    extractResult: list[OcrBatchExtractResult]


class OcrBatchResponse(BaseModel):
    traceId: str | None = None
    code: int | None = None
    msg: str | None = None
    data: OcrBatchData

