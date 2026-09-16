from src.models import Clinic, Service


class ClinicRepository:

    @staticmethod
    def create(**kwargs):
        return Clinic.objects.create(**kwargs)

    @staticmethod
    def get_all():
        return Clinic.objects.all().order_by("-created_at")

    @staticmethod
    def get_by_id(clinic_id: int):
        return Clinic.objects.filter(id=clinic_id).first()

    @staticmethod
    def save(clinic: Clinic):
        clinic.save()
        return clinic

    @staticmethod
    def delete(clinic: Clinic):
        clinic.delete()


class ServiceRepository:

    @staticmethod
    def create(**kwargs):
        return Service.objects.create(**kwargs)

    @staticmethod
    def get_by_id(service_id: int):
        return Service.objects.select_related("clinic").filter(id=service_id).first()

    @staticmethod
    def get_by_clinic(clinic):
        return Service.objects.filter(clinic=clinic).order_by("-created_at")

    @staticmethod
    def save(service: Service):
        service.save()
        return service

    @staticmethod
    def delete(service: Service):
        service.delete()