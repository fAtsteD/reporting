from reporting.exceptions import ReportingError


class FileParseError(ReportingError):
    pass


class FileParseNotConfiguredError(FileParseError):
    pass


class UnknownKindError(FileParseError):
    pass


class UnknownProjectError(FileParseError):
    pass
