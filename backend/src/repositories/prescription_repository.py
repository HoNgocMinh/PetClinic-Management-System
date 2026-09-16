from src.models import Prescription


class PrescriptionRepository:
    @staticmethod
    def create(**kwargs):
        return Prescription.objects.create(**kwargs)

    @staticmethod
    def get_by_id(prescription_id: int):
        return Prescription.objects.select_related(
            "medical_record", "clinic", "staff"
        ).prefetch_related("items__medicine").filter(id=prescription_id).first()

    @staticmethod
    def get_by_medical_record_id(medical_record_id: int):
        return Prescription.objects.select_related(
            "medical_record", "clinic", "staff"
        ).prefetch_related("items__medicine").filter(medical_record_id=medical_record_id).first()

    @staticmethod
    def save(prescription: Prescription):
        prescription.save()
        return prescription
