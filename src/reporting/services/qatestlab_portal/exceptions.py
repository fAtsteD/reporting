from reporting.exceptions import ReportingError


class QATestLabPortalError(ReportingError):
    pass


class QATestLabPortalNotConfiguredError(QATestLabPortalError):
    pass
