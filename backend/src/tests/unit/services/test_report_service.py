from decimal import Decimal

import pytest
from django.utils import timezone

from src.models import Appointment, Payment
from src.services.report_service import ReportService
from src.tests.factories import (
    AppointmentFactory,
    ClinicFactory,
    PaymentFactory,
)


pytestmark = pytest.mark.django_db


def test_overview_report_counts_paid_revenue_and_appointment_statuses():
    paid_payment = PaymentFactory(
        amount=Decimal("100000.00"),
        status=Payment.STATUS_PAID,
        paid_at=timezone.now(),
    )
    PaymentFactory(
        amount=Decimal("200000.00"),
        status=Payment.STATUS_PENDING,
        paid_at=None,
    )

    report = ReportService.get_overview(
        date_from=timezone.localdate(),
        date_to=timezone.localdate(),
    )

    assert report["total_revenue"] == "100000.00"
    assert report["paid_payment_count"] == 1
    assert report["appointment_count"] == 2
    assert report["appointment_status"][Appointment.STATUS_COMPLETED] == 2
    assert report["clinic_count"] == 2
    assert report["service_count"] == 2
    assert paid_payment.clinic.name


def test_revenue_report_groups_paid_payments_by_day():
    PaymentFactory(
        amount=Decimal("100000.00"),
        status=Payment.STATUS_PAID,
        paid_at=timezone.now(),
    )
    PaymentFactory(
        amount=Decimal("50000.00"),
        status=Payment.STATUS_PAID,
        paid_at=timezone.now(),
    )
    PaymentFactory(
        amount=Decimal("70000.00"),
        status=Payment.STATUS_FAILED,
        paid_at=timezone.now(),
    )

    report = ReportService.get_revenue_report(group_by="day")

    assert report["group_by"] == "day"
    assert report["total_revenue"] == "150000.00"
    assert len(report["series"]) == 1
    assert report["series"][0]["period"] == timezone.localdate().isoformat()
    assert report["series"][0]["revenue"] == "150000.00"
    assert report["series"][0]["paid_payment_count"] == 2


def test_revenue_report_ignores_paid_payments_without_paid_at():
    PaymentFactory(
        amount=Decimal("100000.00"),
        status=Payment.STATUS_PAID,
        paid_at=None,
    )

    report = ReportService.get_revenue_report(group_by="day")

    assert report["total_revenue"] == "0.00"
    assert report["series"] == []


def test_clinic_report_returns_revenue_and_appointment_counts_per_clinic():
    clinic = ClinicFactory(name="Clinic A")
    other_clinic = ClinicFactory(name="Clinic B")
    paid_appointment = AppointmentFactory(
        clinic=clinic,
        status=Appointment.STATUS_COMPLETED,
    )
    AppointmentFactory(
        clinic=clinic,
        status=Appointment.STATUS_PENDING,
    )
    PaymentFactory(
        appointment=paid_appointment,
        owner=paid_appointment.owner,
        clinic=clinic,
        amount=Decimal("120000.00"),
        status=Payment.STATUS_PAID,
        paid_at=timezone.now(),
    )

    report = ReportService.get_clinic_report()

    first_clinic = report["clinics"][0]
    second_clinic = report["clinics"][1]

    assert first_clinic["clinic_id"] == clinic.id
    assert first_clinic["appointment_count"] == 2
    assert first_clinic["completed_appointment_count"] == 1
    assert first_clinic["paid_payment_count"] == 1
    assert first_clinic["revenue"] == "120000.00"
    assert second_clinic["clinic_id"] == other_clinic.id
    assert second_clinic["revenue"] == "0.00"
