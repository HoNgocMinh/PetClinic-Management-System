from datetime import date

import pytest

from src.controllers.report_controller import (
    AdminClinicReportAPIView,
    AdminReportOverviewAPIView,
    AdminRevenueReportAPIView,
)
from src.tests.factories import AdminUserFactory
from src.tests.unit.controllers.helpers import assert_success, make_request


pytestmark = pytest.mark.django_db


def test_report_controller_delegates_admin_report_flows(mocker):
    admin = AdminUserFactory()

    overview = {
        "total_revenue": "100000.00",
        "paid_payment_count": 1,
    }
    get_overview = mocker.patch(
        "src.controllers.report_controller.ReportService.get_overview",
        return_value=overview,
    )
    assert_success(
        AdminReportOverviewAPIView().get(
            make_request(
                admin,
                query_params={
                    "date_from": "2026-05-01",
                    "date_to": "2026-05-31",
                },
            ),
        ),
    )
    get_overview.assert_called_once_with(
        date_from=date(2026, 5, 1),
        date_to=date(2026, 5, 31),
    )

    revenue = {
        "group_by": "month",
        "series": [],
    }
    get_revenue_report = mocker.patch(
        "src.controllers.report_controller.ReportService.get_revenue_report",
        return_value=revenue,
    )
    assert_success(
        AdminRevenueReportAPIView().get(
            make_request(
                admin,
                query_params={
                    "group_by": "month",
                },
            ),
        ),
    )
    get_revenue_report.assert_called_once_with(group_by="month")

    clinic_report = {
        "clinics": [],
    }
    get_clinic_report = mocker.patch(
        "src.controllers.report_controller.ReportService.get_clinic_report",
        return_value=clinic_report,
    )
    assert_success(AdminClinicReportAPIView().get(make_request(admin)))
    get_clinic_report.assert_called_once_with()
