from src.common.exceptions import BusinessException, NotFoundException
from src.repositories.pet_repository import PetRepository


class PetService:
    @staticmethod
    def create_pet(user, data):
        return PetRepository.create(
            owner=user,
            name=data["name"],
            species=data["species"],
            breed=data.get("breed", ""),
            gender=data["gender"],
            birth_date=data.get("birth_date"),
            weight=data.get("weight"),
            note=data.get("note", ""),
        )

    @staticmethod
    def get_user_pets(user):
        return PetRepository.get_by_owner(user)

    @staticmethod
    def get_pet_detail(user, pet_id):
        pet = PetRepository.get_by_id(pet_id)
        if not pet:
            raise NotFoundException("Không tìm thấy thú cưng.")

        if pet.owner != user:
            raise BusinessException("Bạn không có quyền truy cập thú cưng này.")

        return pet

    @staticmethod
    def update_pet(user, pet_id, data):
        pet = PetRepository.get_by_id(pet_id)

        if not pet:
            raise NotFoundException("Không tìm thấy thú cưng.")

        if pet.owner != user:
            raise BusinessException("Bạn không có quyền sửa thú cưng này.")

        for field, value in data.items():
            setattr(pet, field, value)

        return PetRepository.save(pet)

    @staticmethod
    def delete_pet(user, pet_id):
        pet = PetRepository.get_by_id(pet_id)

        if not pet:
            raise NotFoundException("Không tìm thấy thú cưng.")

        if pet.owner != user:
            raise BusinessException("Bạn không có quyền xóa thú cưng này.")

        PetRepository.delete(pet)
