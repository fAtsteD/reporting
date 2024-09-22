import datetime
from dataclasses import dataclass, field


@dataclass
class JiraConfig:
    report_date: str | datetime.date = field(default="last", init=False)

    # Urls
    server: str = ""

    # Auth
    login: str = ""
    password: str = ""

    # Tasks
    issue_key_bases: list[str] = field(default_factory=lambda: [])

    @property
    def is_use(self) -> bool:
        return bool(self.login and self.password and self.server)
