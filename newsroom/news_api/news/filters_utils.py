import re
import pytz

from typing import Any, Tuple, cast
from datetime import datetime
from dateutil import parser

from superdesk import get_app_config
from superdesk.utc import utcnow, local_to_utc
from content_api.errors import BadParameterValueError

from .types import NewsApiSearchRequestArgs


def get_date_range(request_args: NewsApiSearchRequestArgs) -> Tuple[datetime | None, datetime | None]:
    """Extract the start and end date limits from request parameters.

    If start and/or end date parameter is not present, a default value is
    returned for the missing parameter(s).

    :param dict request_params: request parameter names and their
        corresponding values

    :return: a (start_date, end_date) tuple with both values being
        instances of Python's datetime.date

    :raises BadParameterValueError:
        * if any of the dates is not in the ISO 8601 format
        * if any of the dates is set in the future
        * if the start date is bigger than the end date
    """

    # regex that should match likely relative elastic searcg date math
    regex = r"now([-+][0-9]*([YMwdHhms]*)$|/d$)"

    # check date limits' format...
    err_msg = "{} parameter must be a valid ISO 8601 date (YYYY-MM-DD) " "with optional the time part"

    relative_start = False
    relative_end = False
    try:
        # check for a relative date
        if re.match(regex, (request_args.start_date or "")):
            start_date = request_args.start_date
            relative_start = True
        else:
            start_date = parse_iso_date(request_args.start_date, request_args.timezone)
    except BadParameterValueError:
        raise
    except ValueError:
        raise BadParameterValueError(desc=err_msg.format("start_date")) from None

    try:
        if request_args.end_date:
            if re.match(regex, request_args.end_date or ""):
                end_date = request_args.end_date
                relative_end = True
            else:
                end_date = parse_iso_date(request_args.end_date, request_args.timezone)
        else:
            end_date = None
    except ValueError:
        raise BadParameterValueError(desc=err_msg.format("end_date")) from None

    # disallow dates in the future
    err_msg = "{} date ({}) must not be set in the future " "(current server date (UTC): {})"
    today = utcnow()

    if (start_date is not None) and not relative_start and (start_date > today):
        raise BadParameterValueError(desc=err_msg.format("Start", start_date, today))

    if (end_date is not None) and not relative_end and (end_date > today):
        raise BadParameterValueError(desc=err_msg.format("End", end_date, today))

    # make sure that the date range limits make sense...
    if (
        (not relative_start or not relative_end)
        and (start_date is not None)
        and (end_date is not None)
        and (start_date > end_date)
    ):
        # NOTE: we allow start_date == end_date (for specific date queries)
        raise BadParameterValueError(desc="Start date must not be greater than end date")

    return cast(datetime, start_date), cast(datetime, end_date)


def create_date_range_filter(start_date: datetime | str | None, end_date: datetime | str | None) -> dict[str, Any]:
    """Create a MongoDB date range query filter from the given dates.

    If both the start date and the end date are None, an empty filter is
    returned. The filtering is performed on the `versioncreated` field in
    database.

    :param start_date: the minimum version creation date (inclusive)
    :type start_date: datetime.date or None
    :param end_date: the maximum version creation date (inclusive)
    :type end_date: datetime.date or None

    :return: MongoDB date range filter (as a dictionary)
    """
    if (start_date is None) and (end_date is None):
        return {}  # nothing to set for the date range filter

    if end_date is None:
        end_date = "now"

    return {
        "range": {
            "versioncreated": {
                "gte": start_date if isinstance(start_date, str) else format_date(start_date),
                "lte": end_date if isinstance(end_date, str) else format_date(end_date),
            }
        }
    }


def parse_iso_date(date_str, timezone=None):
    """Create a date object from the given string in ISO 8601 format.

    :param date_str:
    :type date_str: str or None

    :return: resulting date object or None if None is given
    :rtype: datetime.date

    :raises ValueError: if `date_str` is not in the ISO 8601 date format
    """
    if date_str is None:
        return None
    else:
        dt = parser.parse(date_str)
        if dt.tzinfo is None:
            if timezone:
                if timezone not in pytz.all_timezones:
                    raise BadParameterValueError("Bad parameter value for Parameter (timezone)")
                dt = local_to_utc(timezone, dt)
            else:
                dt = pytz.timezone("UTC").localize(dt)
        return dt


def format_date(date):
    return datetime.strftime(date, get_app_config("ELASTIC_DATETIME_FORMAT"))
