from pydantic.main import BaseModel


class RawPollData(BaseModel):
    poll_post_id: str
    poll_type: str
    poll_year: int
    comments: tuple[str, ...]
