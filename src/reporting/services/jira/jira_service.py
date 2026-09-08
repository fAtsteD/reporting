from collections.abc import Sequence

import jira.client
import jira.exceptions

from reporting import config
from reporting.database.models import Report, Task
from reporting.services.jira.exceptions import JiraNotConfiguredError
from reporting.services.jira.models import JiraMergedTask, JiraTaskResult, JiraTaskStatus


def convert_time_to_jira_time(seconds: int) -> str:
    return f"{round((seconds / 60) // 60)}h {round((seconds / 60) % 60)}m"


def set_worklog(report: Report) -> list[JiraTaskResult]:
    config_jira = config.jira

    if not config_jira.is_use:
        raise JiraNotConfiguredError("Jira is not configured. Server address, login and password are required")

    jira_client = jira.client.JIRA(server=config_jira.server, basic_auth=(config_jira.login, config_jira.password))
    results: list[JiraTaskResult] = []

    for merged_task in _merge_tasks(report.tasks):
        try:
            issue = jira_client.issue(merged_task.key)
            issue_summary: str = issue.fields.summary
            comment = _build_comment(merged_task, issue_summary)
            jira_client.add_worklog(
                merged_task.key,
                convert_time_to_jira_time(merged_task.logged_rounded),
                comment=comment or None,
            )
            results.append(JiraTaskResult(status=JiraTaskStatus.SENT, merged_task=merged_task))
        except jira.exceptions.JIRAError as error:
            results.append(
                JiraTaskResult(status=JiraTaskStatus.FAILED, merged_task=merged_task, reason=error.text or "")
            )

    return results


def _build_comment(merged_task: JiraMergedTask, issue_summary: str) -> str:
    written_summary = issue_summary.strip().casefold()

    return _format_texts([text for text in merged_task.texts if text.casefold() != written_summary])


def _build_description(key: str, texts: Sequence[str]) -> str:
    if not texts:
        return f"{key}:"

    if len(texts) == 1:
        return f"{key}: {texts[0]}"

    return f"{key}:\n{_format_texts(texts)}"


def _build_merged_task(key: str, tasks: Sequence[Task]) -> JiraMergedTask:
    texts = _unique_texts(tasks)

    return JiraMergedTask(description=_build_description(key, texts), key=key, tasks=tuple(tasks), texts=texts)


def _format_texts(texts: Sequence[str]) -> str:
    if not texts:
        return ""

    if len(texts) == 1:
        return texts[0]

    return "\n".join(f"- {text}" for text in texts)


def _is_issue_key(summary_key: str) -> bool:
    return any(
        summary_key.startswith(base) and summary_key[len(base) :].isdigit() for base in config.jira.issue_key_bases
    )


def _merge_tasks(tasks: Sequence[Task]) -> list[JiraMergedTask]:
    tasks_by_key: dict[str, list[Task]] = {}

    for task in tasks:
        if not _is_issue_key(task.summary_key):
            continue

        tasks_by_key.setdefault(task.summary_key, []).append(task)

    return [_build_merged_task(key, key_tasks) for key, key_tasks in tasks_by_key.items()]


def _unique_texts(tasks: Sequence[Task]) -> tuple[str, ...]:
    unique_texts: dict[str, str] = {}

    for task in tasks:
        text = task.summary_text

        if text:
            unique_texts.setdefault(text.casefold(), text)

    return tuple(unique_texts.values())
