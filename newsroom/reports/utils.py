from typing import Callable, Dict, Union
from newsroom.auth.utils import is_current_user_account_mgr, is_current_user_admin, is_current_user_company_admin
from . import admin_reports, company_admin_reports


def get_current_user_reports() -> Union[Dict[str, Callable], Dict]:
    """Return reports according to the user type"""

    if is_current_user_admin() or is_current_user_account_mgr():
        return admin_reports

    if is_current_user_company_admin():
        return company_admin_reports

    return {}
