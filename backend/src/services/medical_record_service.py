from django.db import IntegrityError, transaction

from src.common.exceptions import (
    BusinessException,
    ConflictException,
    NotFoundException,
    PermissionDeniedException,
)
from src.models import Appointment
from src.repositories.appointment_repository import AppointmentRepository
from src.repositories.medical_record_repository import MedicalRecordRepository
from src.repositories.pet_repository import PetRepository


class MedicalRecordService:
    ALLOWED_APPOINTMENT_STATUSES = {
        Appointment.STATUS_CHECKED_IN,
        Appointment.STATUS_IN_PROGRESS,
        Appointment.STATUS_COMPLETED,
    }

    @staticmethod
    def _get_staff_clinic_appointment(user, appointment_id):
        if not user.clinic_id:
            raise BusinessException("Tài khoản staff chưa được gán phòng khám.")

        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundException("Không tìm thấy lịch hẹn.")

        if user.clinic_id != appointment.clinic_id:
            raise PermissionDeniedException("Bạn không có quyền thao tác hồ sơ bệnh án của phòng khám khác.")

        if appointment.status not in MedicalRecordService.ALLOWED_APPOINTMENT_STATUSES:
            raise BusinessException("Chỉ được tạo hồ sơ bệnh án khi lịch hẹn đã check-in, đang khám hoặc đã hoàn tất.")

        return appointment

    @staticmethod
    def create_medical_record(user, appointment_id, data):
        with transaction.atomic():
            appointment = MedicalRecordService._get_staff_clinic_appointment(user, appointment_id)

            existing_record = MedicalRecordRepository.get_by_appointment_id(appointment_id)
            if existing_record:
                raise BusinessException("Lịch hẹn này đã có hồ sơ bệnh án.")

            try:
                return MedicalRecordRepository.create(
                    appointment=appointment,
                    pet=appointment.pet,
                    clinic=appointment.clinic,
                    staff=user,
                    symptoms=data["symptoms"],
                    diagnosis=data["diagnosis"],
                    treatment=data.get("treatment", ""),
                    note=data.get("note", ""),
                )
            except IntegrityError as exc:
                raise ConflictException("Hồ sơ bệnh án này đã tồn tại.") from exc

    @staticmethod
    def get_medical_record_by_appointment(user, appointment_id):
        MedicalRecordService._get_staff_clinic_appointment(user, appointment_id)

        record = MedicalRecordRepository.get_by_appointment_id(appointment_id)
        if not record:
            raise NotFoundException("Không tìm thấy hồ sơ bệnh án.")

        return record

    @staticmethod
    def get_medical_record_detail(user, record_id):
        record = MedicalRecordRepository.get_by_id(record_id)
        if not record:
            raise NotFoundException("Không tìm thấy hồ sơ bệnh án.")

        if not user.clinic_id:
            raise BusinessException("Tài khoản staff chưa được gán phòng khám.")

        if user.clinic_id != record.clinic_id:
            raise PermissionDeniedException("Bạn không có quyền xem hồ sơ bệnh án của phòng khám khác.")

        return record

    @staticmethod
    def get_pet_medical_records(user, pet_id):
        if not user.clinic_id:
            raise BusinessException("Tài khoản staff chưa được gán phòng khám.")

        pet = PetRepository.get_by_id_including_inactive(pet_id)
        if not pet:
            raise NotFoundException("Không tìm thấy thú cưng.")

        return MedicalRecordRepository.get_by_pet_id_and_clinic_id(pet_id, user.clinic_id)

    @staticmethod
    def get_pet_owner_medical_records(user, pet_id):
        pet = PetRepository.get_by_id_including_inactive(pet_id)
        if not pet:
            raise NotFoundException("Không tìm thấy thú cưng.")

        if pet.owner_id != user.id:
            raise PermissionDeniedException("Bạn không có quyền xem hồ sơ của thú cưng này.")

        return MedicalRecordRepository.get_by_pet_id(pet_id)

    @staticmethod
    def get_pet_owner_medical_record_detail(user, record_id):
        record = MedicalRecordRepository.get_by_id(record_id)
        if not record:
            raise NotFoundException("Không tìm thấy hồ sơ bệnh án.")

        if record.pet.owner_id != user.id:
            raise PermissionDeniedException("Bạn không có quyền xem hồ sơ bệnh án này.")

        return record

    @staticmethod
    def update_medical_record(user, record_id, data):
        record = MedicalRecordService.get_medical_record_detail(user, record_id)

        for field in ["symptoms", "diagnosis", "treatment", "note"]:
            if field in data:
                setattr(record, field, data[field])

        return MedicalRecordRepository.save(record)
