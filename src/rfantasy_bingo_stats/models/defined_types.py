from collections import (
    Counter,
    defaultdict,
)
from collections.abc import (
    Iterable,
    Mapping,
)
from typing import (
    AbstractSet,
    Annotated,
    NewType,
    Self,
    TypeVar,
    cast,
)

from pydantic.annotated_handlers import GetCoreSchemaHandler
from pydantic.fields import Field
from pydantic.functional_serializers import PlainSerializer
from pydantic.main import BaseModel
from pydantic_core.core_schema import (
    CoreSchema,
    no_info_after_validator_function,
)


# The purpose of these types is to make each kind of string distinct
# More complex logic can be implemented as a class, if necessary
# Inheritance employed for runtime-checkability
class Author(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Self,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return no_info_after_validator_function(cls, handler(str))


class Book(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Self,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return no_info_after_validator_function(cls, handler(str))


class Series(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Self,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return no_info_after_validator_function(cls, handler(str))


class SquareName(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Self,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return no_info_after_validator_function(cls, handler(str))


class Title(str):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Self,
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return no_info_after_validator_function(cls, handler(str))


BingoName = NewType("BingoName", str)

TitleCol = NewType("TitleCol", str)
AuthorCol = NewType("AuthorCol", str)
HardModeCol = NewType("HardModeCol", str)

CardID = NewType("CardID", str)

DistName = NewType("DistName", str)

# These are aliases for convenience
TitleAuthor = tuple[Title, Author]
TitleAuthorHMCols = tuple[TitleCol, AuthorCol, HardModeCol]

BookOrAuthor = TypeVar("BookOrAuthor", Book, Author)


# Pydantic types
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


# Note this function must handle serialization as well as sorting
def sort(data: Mapping[K, V] | Iterable[T] | T) -> dict[K, V] | list[T] | T:
    if isinstance(data, BaseModel):
        return cast(dict[K, V], data.model_dump())

    if isinstance(data, Mapping):
        out_dict: dict[K, V] = {}
        for key, val in sorted(data.items(), key=lambda item: item[0]):
            out_dict[key] = cast(V, sort(val))
        return out_dict

    if isinstance(data, Iterable) and not isinstance(data, str):
        out_list: list[T] = []
        for val in sorted(data):
            out_list.append(cast(T, sort(val)))
        return out_list

    return cast(T, data)


SortedCounter = Annotated[Counter[K], PlainSerializer(sort)]
SortedDefaultdict = Annotated[defaultdict[K, V], PlainSerializer(sort)]
SortedMapping = Annotated[Mapping[K, V], PlainSerializer(sort)]
SortedSet = Annotated[set[T], PlainSerializer(sort), Field(default_factory=set)]
SortedAbstractSet = Annotated[
    AbstractSet[T], PlainSerializer(sort), Field(default_factory=frozenset)
]
