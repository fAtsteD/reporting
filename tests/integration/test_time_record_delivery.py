import datetime

import pytest
from sqlalchemy.orm import Session

from reporting.services.qatestlab_portal import qatestlab_portal_service
from reporting.services.qatestlab_portal.exceptions import (
    QATestLabPortalError,
    QATestLabPortalNotConfiguredError,
)
from reporting.services.qatestlab_portal.models import PortalTaskStatus
from tests.factories.database import KindFactory, ProjectFactory, ReportFactory, TaskFactory
from tests.fixtures.portal import PORTAL_CONFIG, PortalApiFake
from tests.fixtures.reporting_config import ReportingConfigFixture

_CATEGORY_NAME = "Develop"
_HOUR_SECONDS = 60 * 60
_PORTAL_HOUR = 100
_PROJECT_NAME = "My Project"
_REPORT_DATE = datetime.date(2026, 8, 20)


def test_describes_a_key_without_any_text_as_the_key_alone(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="TEST-1:   ")
    portal_api.add_category(_CATEGORY_NAME)
    portal_api.add_project(_PROJECT_NAME)

    qatestlab_portal_service.send_tasks(report)

    portal_api.assert_time_records_sent([{"description": "TEST-1:", "hours": _PORTAL_HOUR}])


def test_describes_a_task_without_a_key_or_text_as_an_empty_description(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="")
    portal_api.add_category(_CATEGORY_NAME)
    portal_api.add_project(_PROJECT_NAME)

    qatestlab_portal_service.send_tasks(report)

    portal_api.assert_time_records_sent([{"description": "", "hours": _PORTAL_HOUR}])


def test_fails_a_task_when_no_category_is_bound_to_the_corp_struct_item(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    portal_api.add_project(_PROJECT_NAME)
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 0")

    results = qatestlab_portal_service.send_tasks(report)

    assert [(result.status, result.reason) for result in results] == [
        (PortalTaskStatus.FAILED, f"Category not found for {_CATEGORY_NAME}")
    ]


def test_fails_a_task_when_the_category_is_deleted(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    portal_api.add_category(_CATEGORY_NAME, deleted=True)
    portal_api.add_project(_PROJECT_NAME)
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 0")

    results = qatestlab_portal_service.send_tasks(report)

    assert [(result.status, result.reason) for result in results] == [
        (PortalTaskStatus.FAILED, f"Category not found for {_CATEGORY_NAME}")
    ]


def test_fails_a_task_when_the_configured_corp_struct_item_is_not_on_the_portal(
    database_session: Session,
    portal_api: PortalApiFake,
    reporting_config: ReportingConfigFixture,
) -> None:
    reporting_config(
        PORTAL_CONFIG
        | {
            "qatestlab-portal": PORTAL_CONFIG["qatestlab-portal"] | {"project-to-corp-struct-item": {"mp": "MISSING"}},
        }
    )
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(alias="mp", name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 0")
    portal_api.add_category(_CATEGORY_NAME)
    portal_api.add_project(_PROJECT_NAME)

    results = qatestlab_portal_service.send_tasks(report)

    assert [(result.status, result.reason) for result in results] == [
        (PortalTaskStatus.FAILED, "Corp struct item not found")
    ]


def test_fails_a_task_when_the_portal_does_not_have_the_project(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    portal_api.add_category(_CATEGORY_NAME)
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 0")

    results = qatestlab_portal_service.send_tasks(report)

    assert [(result.status, result.reason) for result in results] == [
        (PortalTaskStatus.FAILED, f"Project not found for {_PROJECT_NAME}")
    ]


def test_fails_a_task_when_the_portal_has_no_corp_struct_item(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 0")
    portal_api.add_category(_CATEGORY_NAME)
    portal_api.add_project(_PROJECT_NAME)
    portal_api.forget_corp_struct_items()

    results = qatestlab_portal_service.send_tasks(report)

    assert [(result.status, result.reason) for result in results] == [
        (PortalTaskStatus.FAILED, "Corp struct item not found")
    ]
    assert portal_api.sent_time_records == []


def test_fails_a_task_when_the_portal_project_is_inactive(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    portal_api.add_category(_CATEGORY_NAME)
    portal_api.add_project(_PROJECT_NAME, active=False)
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 0")

    results = qatestlab_portal_service.send_tasks(report)

    assert [(result.status, result.reason) for result in results] == [
        (PortalTaskStatus.FAILED, f"Project not found for {_PROJECT_NAME}")
    ]


def test_fails_when_the_employee_does_not_have_a_main_position(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 0")
    portal_api.add_category(_CATEGORY_NAME)
    portal_api.add_project(_PROJECT_NAME)
    portal_api.forget_employee_positions()

    with pytest.raises(QATestLabPortalError, match="Employee does not have a main position"):
        qatestlab_portal_service.send_tasks(report)


def test_fails_when_the_portal_is_not_configured(
    database_session: Session,
) -> None:
    with pytest.raises(QATestLabPortalNotConfiguredError):
        qatestlab_portal_service.send_tasks(ReportFactory.create())


def test_fails_when_the_report_cannot_be_created(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 0")
    portal_api.add_category(_CATEGORY_NAME)
    portal_api.add_project(_PROJECT_NAME)
    portal_api.fail_report_save()

    with pytest.raises(QATestLabPortalError, match="Failed create/load report"):
        qatestlab_portal_service.send_tasks(report)


def test_keeps_a_task_without_a_key_as_its_own_time_record(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(
        kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="TEST-1: text a"
    )
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="without a key")
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="another one")
    portal_api.add_category(_CATEGORY_NAME)
    portal_api.add_project(_PROJECT_NAME)

    qatestlab_portal_service.send_tasks(report)

    portal_api.assert_time_records_sent(
        [
            {"description": "TEST-1: text a", "hours": _PORTAL_HOUR},
            {"description": "without a key", "hours": _PORTAL_HOUR},
            {"description": "another one", "hours": _PORTAL_HOUR},
        ]
    )


def test_keeps_the_same_key_in_another_kind_as_a_separate_time_record(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(alias="dev", name=_CATEGORY_NAME)
    other_kind = KindFactory.create(alias="rev", name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(
        kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="TEST-1: text a"
    )
    TaskFactory.create(
        kind=other_kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="TEST-1: text b"
    )
    portal_api.add_category(_CATEGORY_NAME)
    portal_api.add_project(_PROJECT_NAME)

    qatestlab_portal_service.send_tasks(report)

    portal_api.assert_time_records_sent(
        [
            {"description": "TEST-1: text a", "hours": _PORTAL_HOUR},
            {"description": "TEST-1: text b", "hours": _PORTAL_HOUR},
        ]
    )


def test_merges_tasks_with_the_same_key_into_one_time_record(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(
        kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="TEST-1: text a"
    )
    TaskFactory.create(
        kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="TEST-1: text b"
    )
    TaskFactory.create(
        kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="TEST-2: text c"
    )
    portal_api.add_category(_CATEGORY_NAME)
    portal_api.add_project(_PROJECT_NAME)

    qatestlab_portal_service.send_tasks(report)

    portal_api.assert_time_records_sent(
        [
            {"description": "TEST-1:\n- text a\n- text b", "hours": 2 * _PORTAL_HOUR, "orderNumber": 1},
            {"description": "TEST-2: text c", "hours": _PORTAL_HOUR, "orderNumber": 2},
        ]
    )


def test_numbers_the_time_records_in_order(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 0")
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 1")
    portal_api.add_category(_CATEGORY_NAME)
    portal_api.add_project(_PROJECT_NAME)

    qatestlab_portal_service.send_tasks(report)

    assert [time_record["orderNumber"] for time_record in portal_api.sent_time_records] == [1, 2]


def test_reuses_the_existing_portal_report_for_the_day(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    existing_report = portal_api.add_report(_REPORT_DATE)
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 0")
    portal_api.add_category(_CATEGORY_NAME)
    portal_api.add_project(_PROJECT_NAME)

    qatestlab_portal_service.send_tasks(report)

    assert [saved["id"] for saved in portal_api.saved_reports] == [existing_report.id]


def test_sends_one_time_record_per_task(
    database_session: Session,
    portal_api: PortalApiFake,
    portal_config: None,
) -> None:
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(alias="dev", name=_CATEGORY_NAME)
    project = ProjectFactory.create(alias="mp", name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 0")
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 1")
    category = portal_api.add_category(_CATEGORY_NAME)
    portal_project = portal_api.add_project(_PROJECT_NAME)

    results = qatestlab_portal_service.send_tasks(report)

    assert [result.status for result in results] == [PortalTaskStatus.SENT, PortalTaskStatus.SENT]
    assert [result.merged_task.project_names for result in results] == [_PROJECT_NAME, _PROJECT_NAME]
    portal_api.assert_time_records_sent(
        [
            {"categoryId": category.id, "description": "task 0", "hours": _PORTAL_HOUR, "projectId": portal_project.id},
            {"categoryId": category.id, "description": "task 1", "hours": _PORTAL_HOUR, "projectId": portal_project.id},
        ]
    )


def test_sends_to_the_corp_struct_item_configured_for_the_project(
    database_session: Session,
    portal_api: PortalApiFake,
    reporting_config: ReportingConfigFixture,
) -> None:
    other_corp_struct_item = portal_api.add_corp_struct_item(alias="OTHER")
    reporting_config(
        PORTAL_CONFIG
        | {
            "qatestlab-portal": PORTAL_CONFIG["qatestlab-portal"] | {"project-to-corp-struct-item": {"mp": "OTHER"}},
        }
    )
    portal_api.add_category(_CATEGORY_NAME, corp_struct_item=other_corp_struct_item)
    portal_api.add_project(_PROJECT_NAME)
    report = ReportFactory.create(date=_REPORT_DATE)
    kind = KindFactory.create(name=_CATEGORY_NAME)
    project = ProjectFactory.create(alias="mp", name=_PROJECT_NAME)
    TaskFactory.create(kind=kind, logged_seconds=_HOUR_SECONDS, project=project, report=report, summary="task 0")

    qatestlab_portal_service.send_tasks(report)

    portal_api.assert_time_records_sent([{"corpStructItemId": other_corp_struct_item.id}])
