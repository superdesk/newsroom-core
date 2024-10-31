from typing import TypedDict


class DateRangeQuery(TypedDict):
    gt: str
    gte: str
    lt: str
    lte: str
    time_zone: str | None


class TimeFilter(TypedDict):
    name: str
    default: bool
    query: DateRangeQuery
    filter: str
