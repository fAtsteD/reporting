import datetime
from dataclasses import dataclass, field


@dataclass
class ReportingConfig:
    kinds: dict = field(default_factory=lambda: {})  # Kinds relation: key - from db, value - from reporting
    login: str = ""
    password: str = ""
    projects: dict = field(default_factory=lambda: {})  # Projects relation: key - from db, value - from reporting
    project_to_corp_struct_item: dict = field(
        default_factory=lambda: {}
    )  # Projects relation: key - from db, value - from reporting corp struct item alias
    report_date: str | datetime.date = "last"
    safe_send_report_days: int = 0
    url: str = ""

    @property
    def is_use(self) -> bool:
        return bool(self.login and self.password and self.url)
