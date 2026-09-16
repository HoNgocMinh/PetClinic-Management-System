from django.db import transaction

from src.common.exceptions import (
    BusinessException,
    NotFoundException,
    PermissionDeniedException,
)
from src.repositories.medicine_repository import MedicineRepository


class MedicineService:
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_ALL = "all"

    @staticmethod
    def _get_staff_clinic_id(user):
        if not user.clinic_id:
            raise BusinessException("Tài khoản staff chưa được gán phòng khám.")
        return user.clinic_id

    @staticmethod
    def _parse_status_filter(status):
        if not status:
            return True

        normalized_status = status.strip().lower()
        if normalized_status == MedicineService.STATUS_ACTIVE:
            return True
        if normalized_status == MedicineService.STATUS_INACTIVE:
            return False
        if normalized_status == MedicineService.STATUS_ALL:
            return None

        raise BusinessException("Status thuốc không hợp lệ. Chỉ chấp nhận active, inactive hoặc all.")

    @staticmethod
    def _validate_staff_clinic_medicine(user, medicine):
        clinic_id = MedicineService._get_staff_clinic_id(user)

        if not medicine:
            raise NotFoundException("Không tìm thấy thuốc.")

        if medicine.clinic_id != clinic_id:
            raise PermissionDeniedException("Bạn không có quyền thao tác thuốc của phòng khám khác.")

        return medicine

    @staticmethod
    def _get_staff_clinic_medicine(user, medicine_id):
        medicine = MedicineRepository.get_by_id(medicine_id)
        return MedicineService._validate_staff_clinic_medicine(user, medicine)

    @staticmethod
    def _get_staff_clinic_medicine_for_update(user, medicine_id):
        medicine = MedicineRepository.get_by_id_for_update(medicine_id)
        return MedicineService._validate_staff_clinic_medicine(user, medicine)

    @staticmethod
    def get_clinic_medicines(user, status=None):
        clinic_id = MedicineService._get_staff_clinic_id(user)
        is_active = MedicineService._parse_status_filter(status)
        return MedicineRepository.get_by_clinic_id(clinic_id, is_active=is_active)

    @staticmethod
    def get_medicine_detail(user, medicine_id):
        return MedicineService._get_staff_clinic_medicine(user, medicine_id)

    @staticmethod
    def create_medicine(user, data):
        clinic_id = MedicineService._get_staff_clinic_id(user)
        medicine_name = data["name"].strip()

        existing_medicine = MedicineRepository.get_by_clinic_id_and_name(clinic_id, medicine_name)
        if existing_medicine:
            if existing_medicine.is_active:
                raise BusinessException("Thuốc này đã tồn tại trong phòng khám.")

            existing_medicine.unit = data["unit"].strip()
            existing_medicine.description = data.get("description", "")
            existing_medicine.stock_quantity = data.get("stock_quantity", 0)
            existing_medicine.price = data.get("price", 0)
            existing_medicine.is_active = True
            return MedicineRepository.save(existing_medicine)

        return MedicineRepository.create(
            clinic_id=clinic_id,
            name=medicine_name,
            unit=data["unit"].strip(),
            description=data.get("description", ""),
            stock_quantity=data.get("stock_quantity", 0),
            price=data.get("price", 0),
            is_active=True,
        )

    @staticmethod
    def update_medicine(user, medicine_id, data):
        with transaction.atomic():
            medicine = MedicineService._get_staff_clinic_medicine_for_update(user, medicine_id)

            if "name" in data:
                new_name = data["name"].strip()
                existing_medicine = MedicineRepository.get_by_clinic_id_and_name(medicine.clinic_id, new_name)
                if existing_medicine and existing_medicine.id != medicine.id:
                    if existing_medicine.is_active:
                        raise BusinessException("Thuốc này đã tồn tại trong phòng khám.")
                    raise BusinessException(
                        "Tên thuốc này đang thuộc về một thuốc đã ngừng hoạt động. Hãy kích hoạt lại thuốc đó thay vì đổi tên."
                    )
                medicine.name = new_name

            if "unit" in data:
                medicine.unit = data["unit"].strip()

            if "description" in data:
                medicine.description = data["description"]

            if "stock_quantity" in data:
                medicine.stock_quantity = data["stock_quantity"]

            if "price" in data:
                medicine.price = data["price"]

            if "is_active" in data:
                medicine.is_active = data["is_active"]

            return MedicineRepository.save(medicine)

    @staticmethod
    def delete_medicine(user, medicine_id):
        medicine = MedicineService._get_staff_clinic_medicine(user, medicine_id)
        medicine.is_active = False
        return MedicineRepository.save(medicine)
