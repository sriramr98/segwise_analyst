
from enum import Enum
from typing import Any
from pydantic import BaseModel


class UploadCsvRequest(BaseModel):
    csv_link: str


class Condition(str, Enum):
    EQ = 'eq' # equal_to
    GT = 'gt' # greater_than
    LT = 'lt' # less_than
    GTE = 'gte' # greater_than_or_equal
    LTE = 'lte' # less_than_or_equal

class AggregateFunction(str, Enum):
    COUNT = 'count'
    SUM = 'sum'
    MAX = 'max'
    MIN = 'min'

class Filter(BaseModel):
    column: str
    value: Any
    condition: Condition

class Aggregation(BaseModel):
    column: str
    function: AggregateFunction
    alias: str
    filter: bool = False
    filterCriteria: Any = None
    filterCondition: Condition | None = None

class ExploreDataRequest(BaseModel):
    filters: list[Filter]
    group_bys: list[str]
    aggregations: list[Aggregation]
