from superdesk import get_resource_service


def get_user_company(user=None):
    if user is None:
        from newsroom.auth import get_user

        user = get_user()

    if user and user.get("company"):
        return get_resource_service("companies").find_one(req=None, _id=user["company"])
    return None


def restrict_coverage_info(company=None):
    if company is None:
        company = get_user_company()
    return (company or {}).get("restrict_coverage_info", False)
