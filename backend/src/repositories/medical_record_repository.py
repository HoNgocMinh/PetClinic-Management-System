from src.models import MedicalRecord


class MedicalRecordRepository:
    @staticmethod
    def create(**kwargs):
        return MedicalRecord.objects.create(**kwargs)

    @staticmethod
    def get_by_id(record_id: int):
        return MedicalRecord.objects.select_related(
            "appointment", "pet", "clinic", "staff"
        ).filter(id=record_id).first()

    @staticmethod
    def get_by_appointment_id(appointment_id: int):
        return MedicalRecord.objects.select_related(
            "appointment", "pet", "clinic", "staff"
        ).filter(appointment_id=appointment_id).first()

    @staticmethod
    def get_by_pet_id_and_clinic_id(pet_id: int, clinic_id: int):
        return MedicalRecord.objects.select_related(
            "appointment", "pet", "clinic", "staff"
        ).filter(
            pet_id=pet_id,
            clinic_id=clinic_id,
        ).order_by("-created_at")

    @staticmethod
    def get_by_pet_id(pet_id: int):
        return MedicalRecord.objects.select_related(
            "appointment", "pet", "clinic", "staff"
        ).filter(pet_id=pet_id).order_by("-created_at")

    @staticmethod
    def save(record: MedicalRecord):
        record.save()
        return record
