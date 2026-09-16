from django.db import IntegrityError, transaction

from src.common.exceptions import (
    BusinessException,
    ConflictException,
    NotFoundException,
    PermissionDeniedException,
)
from src.repositories.medical_record_repository import MedicalRecordRepository
from src.repositories.medicine_repository import MedicineRepository
from src.repositories.prescription_item_repository import PrescriptionItemRepository
from src.repositories.prescription_repository import PrescriptionRepository


class PrescriptionService:
    @staticmethod
    def _get_staff_clinic_id(user):
        if not user.clinic_id:
            raise BusinessException("Tài khoản staff chưa được gán phòng khám.")
        return user.clinic_id

    @staticmethod
    def _get_staff_clinic_medical_record(user, medical_record_id):
        clinic_id = PrescriptionService._get_staff_clinic_id(user)

        record = MedicalRecordRepository.get_by_id(medical_record_id)
        if not record:
            raise NotFoundException("Không tìm thấy hồ sơ bệnh án.")

        if record.clinic_id != clinic_id:
            raise PermissionDeniedException("Bạn không có quyền thao tác đơn thuốc của phòng khám khác.")

        return record

    @staticmethod
    def _get_staff_clinic_prescription(user, prescription_id):
        clinic_id = PrescriptionService._get_staff_clinic_id(user)

        prescription = PrescriptionRepository.get_by_id(prescription_id)
        if not prescription:
            raise NotFoundException("Không tìm thấy đơn thuốc.")

        if prescription.clinic_id != clinic_id:
            raise PermissionDeniedException("Bạn không có quyền thao tác đơn thuốc của phòng khám khác.")

        return prescription

    @staticmethod
    def _validate_staff_clinic_medicine(user, medicine):
        clinic_id = PrescriptionService._get_staff_clinic_id(user)

        if not medicine:
            raise NotFoundException("Không tìm thấy thuốc.")

        if medicine.clinic_id != clinic_id:
            raise PermissionDeniedException("Bạn không có quyền sử dụng thuốc của phòng khám khác.")

        if not medicine.is_active:
            raise BusinessException("Thuốc này đã ngừng hoạt động.")

        return medicine

    @staticmethod
    def _get_staff_clinic_medicine(user, medicine_id):
        medicine = MedicineRepository.get_by_id(medicine_id)
        return PrescriptionService._validate_staff_clinic_medicine(user, medicine)

    @staticmethod
    def _get_staff_clinic_medicine_for_update(user, medicine_id):
        medicine = MedicineRepository.get_by_id_for_update(medicine_id)
        return PrescriptionService._validate_staff_clinic_medicine(user, medicine)

    @staticmethod
    def create_prescription(user, medical_record_id, data):
        with transaction.atomic():
            record = PrescriptionService._get_staff_clinic_medical_record(user, medical_record_id)

            existing_prescription = PrescriptionRepository.get_by_medical_record_id(medical_record_id)
            if existing_prescription:
                raise BusinessException("Hồ sơ bệnh án này đã có đơn thuốc.")

            try:
                return PrescriptionRepository.create(
                    medical_record=record,
                    clinic=record.clinic,
                    staff=user,
                    note=data.get("note", ""),
                )
            except IntegrityError as exc:
                raise ConflictException("Hồ sơ bệnh án này đã có đơn thuốc.") from exc

    @staticmethod
    def get_prescription_by_medical_record(user, medical_record_id):
        PrescriptionService._get_staff_clinic_medical_record(user, medical_record_id)

        prescription = PrescriptionRepository.get_by_medical_record_id(medical_record_id)
        if not prescription:
            raise NotFoundException("Không tìm thấy đơn thuốc.")

        return prescription

    @staticmethod
    def get_pet_owner_prescription_by_medical_record(user, medical_record_id):
        record = MedicalRecordRepository.get_by_id(medical_record_id)
        if not record:
            raise NotFoundException("Không tìm thấy hồ sơ bệnh án.")

        if record.pet.owner_id != user.id:
            raise PermissionDeniedException("Bạn không có quyền xem đơn thuốc này.")

        prescription = PrescriptionRepository.get_by_medical_record_id(medical_record_id)
        if not prescription:
            raise NotFoundException("Không tìm thấy đơn thuốc.")

        return prescription

    @staticmethod
    def get_prescription_detail(user, prescription_id):
        return PrescriptionService._get_staff_clinic_prescription(user, prescription_id)

    @staticmethod
    def update_prescription(user, prescription_id, data):
        prescription = PrescriptionService._get_staff_clinic_prescription(user, prescription_id)

        if "note" in data:
            prescription.note = data["note"]

        return PrescriptionRepository.save(prescription)

    @staticmethod
    def add_prescription_item(user, prescription_id, data):
        with transaction.atomic():
            prescription = PrescriptionService._get_staff_clinic_prescription(user, prescription_id)
            medicine = PrescriptionService._get_staff_clinic_medicine_for_update(user, data["medicine_id"])

            if medicine.stock_quantity < data["quantity"]:
                raise BusinessException("Số lượng thuốc tồn kho không đủ.")

            existing_item = PrescriptionItemRepository.get_by_prescription_and_medicine(
                prescription.id,
                medicine.id,
            )
            if existing_item:
                raise BusinessException("Thuốc này đã tồn tại trong đơn thuốc.")

            medicine.stock_quantity -= data["quantity"]
            MedicineRepository.save(medicine)

            try:
                return PrescriptionItemRepository.create(
                    prescription=prescription,
                    medicine=medicine,
                    quantity=data["quantity"],
                    dosage=data["dosage"],
                    frequency=data["frequency"],
                    duration_days=data["duration_days"],
                    instruction=data.get("instruction", ""),
                )
            except IntegrityError as exc:
                raise ConflictException("Thuốc này đã tồn tại trong đơn thuốc.") from exc

    @staticmethod
    def update_prescription_item(user, item_id, data):
        with transaction.atomic():
            item = PrescriptionItemRepository.get_by_id_for_update(item_id)
            if not item:
                raise NotFoundException("Không tìm thấy chi tiết đơn thuốc.")

            PrescriptionService._get_staff_clinic_prescription(user, item.prescription_id)
            medicine = PrescriptionService._get_staff_clinic_medicine_for_update(user, item.medicine_id)

            new_quantity = data.get("quantity", item.quantity)
            quantity_diff = new_quantity - item.quantity

            if quantity_diff > 0 and medicine.stock_quantity < quantity_diff:
                raise BusinessException("Số lượng thuốc tồn kho không đủ.")

            if quantity_diff != 0:
                medicine.stock_quantity -= quantity_diff
                MedicineRepository.save(medicine)

            item.quantity = new_quantity

            if "dosage" in data:
                item.dosage = data["dosage"]
            if "frequency" in data:
                item.frequency = data["frequency"]
            if "duration_days" in data:
                item.duration_days = data["duration_days"]
            if "instruction" in data:
                item.instruction = data["instruction"]

            return PrescriptionItemRepository.save(item)

    @staticmethod
    def delete_prescription_item(user, item_id):
        with transaction.atomic():
            item = PrescriptionItemRepository.get_by_id_for_update(item_id)
            if not item:
                raise NotFoundException("Không tìm thấy chi tiết đơn thuốc.")

            PrescriptionService._get_staff_clinic_prescription(user, item.prescription_id)

            medicine = PrescriptionService._get_staff_clinic_medicine_for_update(user, item.medicine_id)
            medicine.stock_quantity += item.quantity
            MedicineRepository.save(medicine)

            PrescriptionItemRepository.delete(item)
