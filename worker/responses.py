from pydantic import BaseModel

from models import WorkerStatus


class BaseWorkerResponse(BaseModel):
    message: str


class StatusResponse(BaseModel):
    status: WorkerStatus
