from reporting.exceptions import ReportingError


class JiraError(ReportingError):
    pass


class JiraNotConfiguredError(JiraError):
    pass
