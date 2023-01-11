def restrict_coverage_info(company) -> bool:
    if company:
        return company.get("restrict_coverage_info", False)
    return False
