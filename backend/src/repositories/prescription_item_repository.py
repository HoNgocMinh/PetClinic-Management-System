from src.models import PrescriptionItem


class PrescriptionItemRepository:
    @staticmethod
    def create(**kwargs):
        return PrescriptionItem.objects.create(**kwargs)

    @staticmethod
    def get_by_id(item_id: int):
        return PrescriptionItem.objects.select_related(
            "prescription", "medicine"
        ).filter(id=item_id).first()

    @staticmethod
    def get_by_id_for_update(item_id: int):
        return PrescriptionItem.objects.select_related(
            "prescription", "medicine"
        ).select_for_update().filter(id=item_id).first()

    @staticmethod
    def get_by_prescription_and_medicine(prescription_id: int, medicine_id: int):
        return PrescriptionItem.objects.filter(
            prescription_id=prescription_id,
            medicine_id=medicine_id,
        ).first()

    @staticmethod
    def save(item: PrescriptionItem):
        item.save()
        return item

    @staticmethod
    def delete(item: PrescriptionItem):
        item.delete()
