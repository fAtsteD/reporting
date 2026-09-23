import datetime
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field


class BaseConfig(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class AppConfig(BaseConfig):
    default_kind: str = Field(
        default="Development",
        alias="default-type",
        description="Kind for a task that does not have one",
    )
    default_project: str = Field(
        default="Default",
        alias="default-project",
        description="Project for a task that does not have one",
    )
    input_file_hours: str = Field(
        default="",
        alias="hour-report-path",
        description="Path to the file with tasks by hours",
    )
    minute_round_to: int = Field(
        default=15,
        alias="minute-round-to",
        description="Round logged minutes to this number, 0 keeps the exact time",
    )
    skip_tasks: list[str] = Field(
        default_factory=list,
        alias="omit-task",
        description="Task names that are skipped while the file is parsed",
    )
    sqlite_database_path: str = Field(
        default="",
        alias="sqlite-database-path",
        description="Path to the SQLite database file",
    )
    timezone_name: str | None = Field(
        default=None,
        alias="timezone",
        description="IANA timezone of the times in the task file, empty for the system one",
    )
    work_day_hours: float = Field(
        default=8.0,
        alias="work-day-hours",
        description="Length of a work day in hours, used to fill the last task of a day",
    )

    @property
    def timezone(self) -> datetime.tzinfo:
        if self.timezone_name:
            return ZoneInfo(self.timezone_name)

        return datetime.datetime.now().astimezone().tzinfo or datetime.UTC

    @property
    def work_day_duration(self) -> datetime.timedelta:
        return datetime.timedelta(hours=self.work_day_hours)


class Dictionary(BaseConfig):
    kinds: dict[str, str] = Field(
        default_factory=dict,
        alias="type",
        description="Written kind name to the kind alias",
    )
    projects: dict[str, str] = Field(
        default_factory=dict,
        alias="project",
        description="Written project name to the project alias",
    )
    tasks: dict[str, str] = Field(
        default_factory=dict,
        alias="task",
        description="Written task name to the full task name",
    )

    def translate_kind(self, text: str) -> str:
        return self.kinds.get(text, text)

    def translate_project(self, text: str) -> str:
        return self.projects.get(text, text)

    def translate_task(self, text: str) -> str:
        return self.tasks.get(text, text)


class JiraConfig(BaseConfig):
    issue_key_bases: list[str] = Field(
        default_factory=list,
        alias="issue-key-base",
        description="Prefixes of an issue key to search in a task name",
    )
    login: str = Field(default="", description="Login of the Jira account")
    password: str = Field(default="", description="Password of the Jira account")
    server: str = Field(default="", description="Address of the Jira server")

    @property
    def is_use(self) -> bool:
        return bool(self.login and self.password and self.server)


class KeyKind(StrEnum):
    DICT_ENTRY = "dict-entry"
    DICT_FIELD = "dict-field"
    LIST_FIELD = "list-field"
    SCALAR_FIELD = "scalar-field"
    SECTION = "section"


class QATestLabPortalConfig(BaseConfig):
    kinds: dict[str, str] = Field(
        default_factory=dict,
        description="Kind alias to the category name in the portal",
    )
    login: str = Field(default="", description="Login of the portal account")
    password: str = Field(default="", description="Password of the portal account")
    project_to_corp_struct_item: dict[str, str] = Field(
        default_factory=dict,
        alias="project-to-corp-struct-item",
        description="Project alias to the corp struct item alias in the portal",
    )
    projects: dict[str, str] = Field(
        default_factory=dict,
        description="Project alias to the project name in the portal. Unmapped projects are sent without a project",
    )
    url: str = Field(default="", description="Address of the portal api")

    @property
    def is_use(self) -> bool:
        return bool(self.login and self.password and self.url)


@dataclass
class ResolvedKey:
    kind: KeyKind
    aliases: list[str] = field(default_factory=list)
    description: str = ""
    entry_key: str = ""
    field_names: list[str] = field(default_factory=list)
    value_type: Any = str


class RootConfig(BaseConfig):
    app: AppConfig = Field(default_factory=AppConfig)
    dictionary: Dictionary = Field(default_factory=Dictionary)
    jira: JiraConfig = Field(default_factory=JiraConfig)
    qatestlab_portal: QATestLabPortalConfig = Field(default_factory=QATestLabPortalConfig, alias="qatestlab-portal")
