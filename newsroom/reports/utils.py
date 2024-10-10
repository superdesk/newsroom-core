from typing import Callable, Dict, Union

from newsroom.auth.utils import get_user_or_none_from_request
from . import admin_reports, company_admin_reports


def get_current_user_reports() -> Union[Dict[str, Callable], Dict]:
    """Return reports according to the user type"""

    user = get_user_or_none_from_request(None)

    if not user:
        return {}
    elif user.is_admin() or user.is_account_manager():
        return admin_reports
    elif user.is_company_admin():
        return company_admin_reports

    return {}
