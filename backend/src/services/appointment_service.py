from datetime import timedelta

from django.db import transaction

from src.common.exceptions import (
    BusinessException,
    NotFoundException,
    PermissionDeniedException,
)
from src.models import Appointment, Clinic, Pet, Service
from src.repositories.appointment_repository import AppointmentRepository
from src.services.payment_service import PaymentService


class AppointmentService:
    @staticmethod
    def _has_time_conflict(clinic_id, appointment_time, duration_minutes, exclude_appointment_id=None):
        appointment_end = appointment_time + timedelta(minutes=duration_minutes)
        active_appointments = AppointmentRepository.get_active_by_clinic_id(clinic_id)

        for existing_appointment in active_appointments:
            if exclude_appointment_id and existing_appointment.id == exclude_appointment_id:
                continue

            existing_end = existing_appointment.appointment_time + timedelta(
                minutes=existing_appointment.service.duration_minutes
            )

            if appointment_time < existing_end and existing_appointment.appointment_time < appointment_end:
                return True

        return False

    @staticmethod
    def create_appointment(user, data):
        pet = Pet.objects.filter(id=data["pet_id"], owner=user, is_active=True).first()
        if not pet:
            raise NotFoundException("Không tìm thấy thú cưng hoặc bạn không có quyền sử dụng.")

        clinic = Clinic.objects.filter(id=data["clinic_id"], is_active=True).first()
        if not clinic:
            raise NotFoundException("Phòng khám không tồn tại hoặc đang ngừng hoạt động.")

        service = Service.objects.filter(
            id=data["service_id"],
            clinic=clinic,
            is_active=True,
        ).first()
        if not service:
            raise NotFoundException("Dịch vụ không hợp lệ tại phòng khám này.")

        appointment_time = data["appointment_time"]

        if AppointmentService._has_time_conflict(
            clinic.id,
            appointment_time,
            service.duration_minutes,
        ):
            raise BusinessException("Khung giờ này bị trùng với lịch hẹn khác.")

        return AppointmentRepository.create(
            owner=user,
            pet=pet,
            clinic=clinic,
            service=service,
            appointment_time=appointment_time,
            note=data.get("note", ""),
            status=Appointment.STATUS_PENDING,
        )

    @staticmethod
    def get_user_appointments(user):
        return AppointmentRepository.get_all_by_owner(user)

    @staticmethod
    def get_clinic_appointments(user):
        if not user.clinic_id:
            raise BusinessException("Tài khoản staff chưa được gán phòng khám.")

        return AppointmentRepository.get_all_by_clinic_id(user.clinic_id)

    @staticmethod
    def get_clinic_appointment_detail(user, appointment_id):
        if not user.clinic_id:
            raise BusinessException("Tài khoản staff chưa được gán phòng khám.")

        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Không tìm thấy lịch hẹn.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Bạn không có quyền xem lịch hẹn của phòng khám khác.")

        return appointment

    @staticmethod
    def get_appointment_detail(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Không tìm thấy lịch hẹn.")

        if appointment.owner != user:
            raise BusinessException("Bạn không có quyền truy cập lịch hẹn này.")

        return appointment

    @staticmethod
    def update_appointment(user, appointment_id, data):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Không tìm thấy lịch hẹn.")

        if appointment.owner != user:
            raise BusinessException("Bạn không có quyền sửa lịch hẹn này.")

        if appointment.status in [
            Appointment.STATUS_CONFIRMED,
            Appointment.STATUS_CHECKED_IN,
            Appointment.STATUS_IN_PROGRESS,
            Appointment.STATUS_WAITING_PAYMENT,
            Appointment.STATUS_COMPLETED,
            Appointment.STATUS_CANCELLED,
            Appointment.STATUS_NO_SHOW,
        ]:
            raise BusinessException("Không thể cập nhật lịch hẹn khi phòng khám đã tiếp nhận xử lý.")

        new_time = data.get("appointment_time")
        if new_time and new_time != appointment.appointment_time:
            if AppointmentService._has_time_conflict(
                appointment.clinic.id,
                new_time,
                appointment.service.duration_minutes,
                exclude_appointment_id=appointment.id,
            ):
                raise BusinessException("Khung giờ mới bị trùng với lịch hẹn khác.")
            appointment.appointment_time = new_time

        if "note" in data:
            appointment.note = data["note"]

        return AppointmentRepository.save(appointment)

    @staticmethod
    def cancel_appointment(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Không tìm thấy lịch hẹn.")

        if appointment.owner != user:
            raise BusinessException("Bạn không có quyền hủy lịch hẹn này.")

        if appointment.status in [
            Appointment.STATUS_CHECKED_IN,
            Appointment.STATUS_IN_PROGRESS,
            Appointment.STATUS_WAITING_PAYMENT,
            Appointment.STATUS_COMPLETED,
            Appointment.STATUS_CANCELLED,
            Appointment.STATUS_NO_SHOW,
        ]:
            raise BusinessException("Không thể hủy lịch hẹn ở trạng thái hiện tại.")

        if appointment.status == Appointment.STATUS_CONFIRMED:
            raise BusinessException("Không thể hủy lịch hẹn sau khi phòng khám đã xác nhận.")

        appointment.status = Appointment.STATUS_CANCELLED
        return AppointmentRepository.save(appointment)

    @staticmethod
    def confirm_appointment(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Không tìm thấy lịch hẹn.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Bạn không có quyền xác nhận lịch hẹn của phòng khám khác.")

        if appointment.status != Appointment.STATUS_PENDING:
            raise BusinessException("Chỉ lịch hẹn đang chờ xác nhận mới được duyệt.")

        appointment.status = Appointment.STATUS_CONFIRMED
        return AppointmentRepository.save(appointment)

    @staticmethod
    def check_in(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Không tìm thấy lịch hẹn.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Bạn không có quyền check-in lịch hẹn của phòng khám khác.")

        if appointment.status != Appointment.STATUS_CONFIRMED:
            raise BusinessException("Chỉ lịch hẹn đã xác nhận mới được check-in.")

        appointment.status = Appointment.STATUS_CHECKED_IN
        return AppointmentRepository.save(appointment)

    @staticmethod
    def start_appointment(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Không tìm thấy lịch hẹn.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Bạn không có quyền bắt đầu khám lịch hẹn của phòng khám khác.")

        if appointment.status != Appointment.STATUS_CHECKED_IN:
            raise BusinessException("Chỉ lịch hẹn đã check-in mới có thể bắt đầu khám.")

        appointment.status = Appointment.STATUS_IN_PROGRESS
        return AppointmentRepository.save(appointment)

    @staticmethod
    def complete_appointment(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Không tìm thấy lịch hẹn.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Bạn không có quyền hoàn tất lịch hẹn của phòng khám khác.")

        if appointment.status != Appointment.STATUS_IN_PROGRESS:
            raise BusinessException("Chỉ lịch hẹn đang khám mới có thể hoàn tất.")

        with transaction.atomic():
            appointment.status = Appointment.STATUS_WAITING_PAYMENT
            appointment = AppointmentRepository.save(appointment)
            PaymentService.create_pending_payment_for_appointment(appointment)
            return appointment

    @staticmethod
    def mark_no_show(user, appointment_id):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Không tìm thấy lịch hẹn.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Bạn không có quyền cập nhật lịch hẹn của phòng khám khác.")

        if appointment.status != Appointment.STATUS_CONFIRMED:
            raise BusinessException("Chỉ lịch hẹn đã xác nhận mới có thể đánh dấu vắng mặt.")

        appointment.status = Appointment.STATUS_NO_SHOW
        return AppointmentRepository.save(appointment)
