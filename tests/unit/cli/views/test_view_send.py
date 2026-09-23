from reporting.cli.views import view_send
from reporting.services.jira.models import JiraMergedTask, JiraTaskResult, JiraTaskStatus
from tests.assertions import cli_output
from tests.factories.database import KindFactory, ProjectFactory, TaskFactory
from tests.fixtures.reporting_config import ReportingConfigFixture

_HOUR_SECONDS = 60 * 60


def test_marks_a_failed_task_with_a_cross(reporting_config: ReportingConfigFixture) -> None:
    result = JiraTaskResult(status=JiraTaskStatus.FAILED, merged_task=_build_merged_task("wrote the parser"))

    output = cli_output.render(view_send.render_jira_results([result]))

    cli_output.assert_lines(output, ["Jira", "✗ 01:00 wrote the parser My Project"])


def test_marks_a_sent_task_with_a_check(reporting_config: ReportingConfigFixture) -> None:
    result = JiraTaskResult(status=JiraTaskStatus.SENT, merged_task=_build_merged_task("wrote the parser"))

    output = cli_output.render(view_send.render_jira_results([result]))

    cli_output.assert_lines(output, ["Jira", "✓ 01:00 wrote the parser My Project"])


def test_renders_a_note_when_there_is_nothing_to_send(reporting_config: ReportingConfigFixture) -> None:
    output = cli_output.render(view_send.render_jira_results([]))

    cli_output.assert_lines(output, ["Jira", "No tasks to send"])


def test_renders_one_row_per_result(reporting_config: ReportingConfigFixture) -> None:
    sent = JiraTaskResult(status=JiraTaskStatus.SENT, merged_task=_build_merged_task("wrote the parser"))
    failed = JiraTaskResult(status=JiraTaskStatus.FAILED, merged_task=_build_merged_task("wrote the docs"))

    output = cli_output.render(view_send.render_jira_results([sent, failed]))

    cli_output.assert_lines(
        output,
        [
            "Jira",
            "✓ 01:00 wrote the parser My Project",
            "✗ 01:00 wrote the docs My Project",
        ],
    )


def test_renders_the_failure_reason_under_a_failed_task(reporting_config: ReportingConfigFixture) -> None:
    result = JiraTaskResult(
        status=JiraTaskStatus.FAILED,
        merged_task=_build_merged_task("wrote the parser"),
        reason="Issue does not exist",
    )

    output = cli_output.render(view_send.render_jira_results([result]))

    cli_output.assert_lines(output, ["Jira", "✗ 01:00 wrote the parser My Project", "Issue does not exist"])


def _build_merged_task(description: str, project_name: str = "My Project") -> JiraMergedTask:
    task = TaskFactory.build(
        kind=KindFactory.build(name="Develop"),
        logged_seconds=_HOUR_SECONDS,
        project=ProjectFactory.build(name=project_name),
        summary=f"TEST-1: {description}",
    )

    return JiraMergedTask(description=description, key="TEST-1", tasks=(task,), texts=(description,))
