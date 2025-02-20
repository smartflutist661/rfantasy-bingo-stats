from collections import Counter
from typing import (
    Any,
    Optional,
    cast,
)

from pydantic import ValidationError
from pydantic.functional_serializers import field_serializer
from pydantic.functional_validators import field_validator
from pydantic.main import BaseModel
from pydantic_core.core_schema import (
    SerializerFunctionWrapHandler,
    ValidatorFunctionWrapHandler,
)

from rfantasy_bingo_stats.models.author_info import (
    Ethnicity,
    Gender,
    Nationality,
)
from rfantasy_bingo_stats.models.defined_types import SortedCounter


class AuthorStatistics(BaseModel):
    """Counters for unique books + authors"""

    gender_count: SortedCounter[Gender] = Counter()
    ethnicity_count: SortedCounter[Ethnicity] = Counter()
    queer_count: Counter[Optional[bool]] = Counter()
    nationality_count: SortedCounter[Nationality] = Counter()

    @field_serializer("queer_count", mode="wrap")
    def sort_ser_none_key(
        self,
        data: Counter[Optional[bool]],
        handler: SerializerFunctionWrapHandler,
    ) -> dict[str, int]:
        out = handler(data)
        return dict(sorted(out.items()))

    @field_validator("queer_count", mode="wrap")
    @classmethod
    def deser_none_key(  # type: ignore[explicit-any]
        cls,
        data: Any,
        handler: ValidatorFunctionWrapHandler,
    ) -> Counter[Optional[bool]]:
        try:
            return cast(Counter[Optional[bool]], handler(data))
        except ValidationError as exc:
            error = exc.errors()[0]
            if error["type"] == "bool_parsing" and error["input"] == "null":
                rehandle = {}
                for key, val in data.items():
                    if key == "null":
                        key = None
                    rehandle[key] = val
                    return cast(Counter[Optional[bool]], handler(rehandle))
            raise
