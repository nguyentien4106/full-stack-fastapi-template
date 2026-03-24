from pydantic import BaseModel


class PresignRequest(BaseModel):
    filename: str
    content_type: str | None = None
    bucket: str | None = None


class PresignResponse(BaseModel):
    url: str
    key: str
