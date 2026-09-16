from src.models import Pet


class PetRepository:

    @staticmethod
    def create(**kwargs):
        return Pet.objects.create(**kwargs)

    @staticmethod
    def get_by_id(pet_id: int):
        return Pet.objects.filter(id=pet_id, is_active=True).first()

    @staticmethod
    def get_by_id_including_inactive(pet_id: int):
        return Pet.objects.filter(id=pet_id).first()

    @staticmethod
    def get_by_owner(owner):
        return Pet.objects.filter(owner=owner, is_active=True).order_by("-created_at")

    @staticmethod
    def delete(pet: Pet):
        pet.is_active = False
        pet.save(update_fields=["is_active", "updated_at"])

    @staticmethod
    def save(pet: Pet):
        pet.save()
        return pet
