from pydantic import BaseModel


class ContentType(BaseModel):
    media_type: str
    charset: str | None = None
    boundary: str | None = None

