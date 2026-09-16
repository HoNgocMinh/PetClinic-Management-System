from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from src.controllers.appointment_controller import (
    AppointmentCheckInAPIView,
    AppointmentCompleteAPIView,
    AppointmentConfirmAPIView,
    AppointmentDetailAPIView,
    AppointmentListCreateAPIView,
    AppointmentNoShowAPIView,
    AppointmentStartAPIView,
    StaffClinicAppointmentDetailAPIView,
    StaffClinicAppointmentListAPIView,
)
from src.tests.factories import (
    AppointmentFactory,
    ClinicFactory,
    PetFactory,
    ServiceFactory,
    StaffUserFactory,
    UserFactory,
)
from src.tests.unit.controllers.helpers import (
    appointment_payload,
    assert_success,
    make_request,
)


pytestmark = pytest.mark.django_db


def test_appointment_controller_delegates_owner_and_staff_flows(mocker):
    clinic = ClinicFactory()
    owner = UserFactory()
    staff = StaffUserFactory(clinic=clinic)
    pet = PetFactory(owner=owner)
    service = ServiceFactory(clinic=clinic)
    appointment = AppointmentFactory(owner=owner, pet=pet, clinic=clinic, service=service)

    mocker.patch(
        "src.controllers.appointment_controller.AppointmentService.get_user_appointments",
        return_value=[appointment],
    )
    assert_success(AppointmentListCreateAPIView().get(make_request(owner)))

    create_appointment = mocker.patch(
        "src.controllers.appointment_controller.AppointmentService.create_appointment",
        return_value=appointment,
    )
    assert_success(
        AppointmentListCreateAPIView().post(make_request(owner, appointment_payload(appointment))),
        status.HTTP_201_CREATED,
    )
    create_appointment.assert_called_once()

    mocker.patch(
        "src.controllers.appointment_controller.AppointmentService.get_clinic_appointments",
        return_value=[appointment],
    )
    assert_success(StaffClinicAppointmentListAPIView().get(make_request(staff)))

    mocker.patch(
        "src.controllers.appointment_controller.AppointmentService.get_clinic_appointment_detail",
        return_value=appointment,
    )
    assert_success(
        StaffClinicAppointmentDetailAPIView().get(make_request(staff), appointment.id),
    )

    mocker.patch(
        "src.controllers.appointment_controller.AppointmentService.get_appointment_detail",
        return_value=appointment,
    )
    assert_success(AppointmentDetailAPIView().get(make_request(owner), appointment.id))

    mocker.patch(
        "src.controllers.appointment_controller.AppointmentService.update_appointment",
        return_value=appointment,
    )
    assert_success(
        AppointmentDetailAPIView().put(
            make_request(owner, {"appointment_time": timezone.now() + timedelta(days=3)}),
            appointment.id,
        ),
    )

    mocker.patch(
        "src.controllers.appointment_controller.AppointmentService.cancel_appointment",
        return_value=appointment,
    )
    assert_success(AppointmentDetailAPIView().delete(make_request(owner), appointment.id))

    for view_class, service_method in [
        (AppointmentCheckInAPIView, "check_in"),
        (AppointmentConfirmAPIView, "confirm_appointment"),
        (AppointmentStartAPIView, "start_appointment"),
        (AppointmentCompleteAPIView, "complete_appointment"),
        (AppointmentNoShowAPIView, "mark_no_show"),
    ]:
        mocker.patch(
            f"src.controllers.appointment_controller.AppointmentService.{service_method}",
            return_value=appointment,
        )
        assert_success(view_class().post(make_request(staff), appointment.id))
