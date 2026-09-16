from decimal import Decimal
from types import SimpleNamespace

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from src.models import Appointment, Payment
from src.tests.factories import AdminUserFactory, AppointmentFactory, PaymentFactory, UserFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def report_context():
    admin = AdminUserFactory()
    owner = UserFactory()
    appointment = AppointmentFactory(status=Appointment.STATUS_COMPLETED)
    PaymentFactory(
        appointment=appointment,
        owner=appointment.owner,
        clinic=appointment.clinic,
        amount=Decimal("100000.00"),
        status=Payment.STATUS_PAID,
        paid_at=timezone.now(),
    )

    return SimpleNamespace(
        client=APIClient(),
        admin=admin,
        owner=owner,
        appointment=appointment,
    )


def authenticate(ctx, user):
    ctx.client.force_authenticate(user=user)


def test_admin_can_view_system_reports(report_context):
    authenticate(report_context, report_context.admin)

    overview_response = report_context.client.get(reverse("admin-report-overview"))
    revenue_response = report_context.client.get(
        reverse("admin-report-revenue"),
        {"group_by": "day"},
    )
    clinic_response = report_context.client.get(reverse("admin-report-clinics"))

    assert overview_response.status_code == status.HTTP_200_OK
    assert overview_response.data["data"]["total_revenue"] == "100000.00"
    assert overview_response.data["data"]["paid_payment_count"] == 1
    assert revenue_response.status_code == status.HTTP_200_OK
    assert revenue_response.data["data"]["series"][0]["revenue"] == "100000.00"
    assert clinic_response.status_code == status.HTTP_200_OK
    assert clinic_response.data["data"]["clinics"][0]["revenue"] == "100000.00"


def test_non_admin_cannot_view_system_reports(report_context):
    authenticate(report_context, report_context.owner)

    response = report_context.client.get(reverse("admin-report-overview"))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["success"] is False


def test_admin_report_rejects_invalid_date_range(report_context):
    authenticate(report_context, report_context.admin)

    response = report_context.client.get(
        reverse("admin-report-overview"),
        {
            "date_from": "2026-05-31",
            "date_to": "2026-05-01",
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
