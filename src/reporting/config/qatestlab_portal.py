import datetime
from dataclasses import dataclass, field


@dataclass
class QATestLabPortalConfig:
    kinds: dict = field(default_factory=dict)
    login: str = ""
    password: str = ""
    projects: dict = field(default_factory=dict)
    project_to_corp_struct_item: dict = field(default_factory=dict)
    report_date: str | datetime.date = "last"
    safe_send_report_days: int = 0
    url: str = ""

    @property
    def is_use(self) -> bool:
        return bool(self.login and self.password and self.url)
