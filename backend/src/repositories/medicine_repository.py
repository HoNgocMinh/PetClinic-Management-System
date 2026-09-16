from src.models import Medicine


class MedicineRepository:
    @staticmethod
    def create(**kwargs):
        return Medicine.objects.create(**kwargs)

    @staticmethod
    def get_by_id(medicine_id: int):
        return Medicine.objects.select_related("clinic").filter(id=medicine_id).first()

    @staticmethod
    def get_by_id_for_update(medicine_id: int):
        return Medicine.objects.select_related("clinic").select_for_update().filter(id=medicine_id).first()

    @staticmethod
    def get_by_clinic_id(clinic_id: int, is_active=None):
        queryset = Medicine.objects.select_related("clinic").filter(clinic_id=clinic_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        return queryset.order_by("name")

    @staticmethod
    def get_by_clinic_id_and_name(clinic_id: int, name: str):
        return Medicine.objects.filter(clinic_id=clinic_id, name__iexact=name).first()

    @staticmethod
    def get_active_by_clinic_id_and_name(clinic_id: int, name: str):
        return Medicine.objects.filter(
            clinic_id=clinic_id,
            name__iexact=name,
            is_active=True,
        ).first()

    @staticmethod
    def save(medicine: Medicine):
        medicine.save()
        return medicine
