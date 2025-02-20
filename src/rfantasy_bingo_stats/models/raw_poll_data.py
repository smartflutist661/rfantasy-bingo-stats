from pydantic.main import BaseModel


class RawPollData(BaseModel):
    poll_post_id: str
    poll_name: str
    comments: list[str]
