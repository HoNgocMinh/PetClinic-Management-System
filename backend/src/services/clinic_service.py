from src.common.exceptions import BusinessException, NotFoundException
from src.repositories.clinic_repository import ClinicRepository, ServiceRepository


class ClinicService:
    @staticmethod
    def create_clinic(data):
        return ClinicRepository.create(
            name=data["name"],
            address=data["address"],
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            is_active=True,
        )

    @staticmethod
    def get_all_clinics():
        # Chỉ trả về phòng khám đang hoạt động.
        return ClinicRepository.get_all().filter(is_active=True)

    @staticmethod
    def get_clinic_detail(clinic_id):
        clinic = ClinicRepository.get_by_id(clinic_id)
        if not clinic:
            raise NotFoundException("Không tìm thấy phòng khám.")

        if not clinic.is_active:
            raise BusinessException("Phòng khám đang ngừng hoạt động.")

        return clinic

    @staticmethod
    def update_clinic(clinic_id, data):
        clinic = ClinicRepository.get_by_id(clinic_id)
        if not clinic:
            raise NotFoundException("Không tìm thấy phòng khám.")

        for field, value in data.items():
            setattr(clinic, field, value)

        return ClinicRepository.save(clinic)

    @staticmethod
    def delete_clinic(clinic_id):
        clinic = ClinicRepository.get_by_id(clinic_id)
        if not clinic:
            raise NotFoundException("Không tìm thấy phòng khám.")

        # Không xóa cứng, chỉ soft delete.
        clinic.is_active = False
        return ClinicRepository.save(clinic)


class ServiceService:
    @staticmethod
    def create_service(data):
        clinic = ClinicRepository.get_by_id(data["clinic_id"])
        if not clinic:
            raise NotFoundException("Không tìm thấy phòng khám.")

        if not clinic.is_active:
            raise BusinessException("Không thể tạo dịch vụ cho phòng khám đang ngừng hoạt động.")

        return ServiceRepository.create(
            clinic=clinic,
            name=data["name"],
            service_type=data["service_type"],
            description=data.get("description", ""),
            price=data["price"],
            duration_minutes=data["duration_minutes"],
            is_active=True,
        )

    @staticmethod
    def get_services_by_clinic(clinic_id):
        clinic = ClinicRepository.get_by_id(clinic_id)
        if not clinic:
            raise NotFoundException("Không tìm thấy phòng khám.")

        if not clinic.is_active:
            raise BusinessException("Phòng khám đang ngừng hoạt động.")

        return ServiceRepository.get_by_clinic(clinic).filter(is_active=True)

    @staticmethod
    def update_service(service_id, data):
        service = ServiceRepository.get_by_id(service_id)
        if not service:
            raise NotFoundException("Không tìm thấy dịch vụ.")

        if not service.clinic.is_active:
            raise BusinessException("Không thể cập nhật dịch vụ của phòng khám đã ngừng hoạt động.")

        for field, value in data.items():
            setattr(service, field, value)

        return ServiceRepository.save(service)

    @staticmethod
    def delete_service(service_id):
        service = ServiceRepository.get_by_id(service_id)
        if not service:
            raise NotFoundException("Không tìm thấy dịch vụ.")

        # Không xóa cứng, chỉ soft delete.
        service.is_active = False
        return ServiceRepository.save(service)
