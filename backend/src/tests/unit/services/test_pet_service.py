from types import SimpleNamespace

import pytest

from src.common.exceptions import BusinessException, NotFoundException
from src.models import Pet
from src.services.pet_service import PetService
from src.tests.factories import PetFactory, UserFactory


pytestmark = pytest.mark.django_db


@pytest.fixture
def pet_context():
    return SimpleNamespace(
        owner=UserFactory(),
        other_owner=UserFactory(),
    )


def pet_data(**overrides):
    data = {
        "name": "Milu",
        "species": Pet.SPECIES_DOG,
        "breed": "Poodle",
        "gender": Pet.GENDER_MALE,
        "birth_date": None,
        "weight": "4.50",
        "note": "Friendly",
    }
    data.update(overrides)
    return data


def test_create_pet_success(pet_context):
    pet = PetService.create_pet(pet_context.owner, pet_data())

    assert pet.owner == pet_context.owner
    assert pet.name == "Milu"
    assert pet.species == Pet.SPECIES_DOG
    assert pet.gender == Pet.GENDER_MALE
    assert pet.is_active is True


def test_get_user_pets_returns_only_active_pets_for_owner(pet_context):
    active_pet = PetFactory(owner=pet_context.owner, name="Active")
    PetFactory(owner=pet_context.owner, name="Inactive", is_active=False)
    PetFactory(owner=pet_context.other_owner, name="Other Owner")

    pets = PetService.get_user_pets(pet_context.owner)

    assert list(pets) == [active_pet]


def test_get_pet_detail_rejects_another_owners_pet(pet_context):
    pet = PetFactory(owner=pet_context.other_owner)

    with pytest.raises(BusinessException):
        PetService.get_pet_detail(pet_context.owner, pet.id)


def test_get_pet_detail_rejects_missing_or_inactive_pet(pet_context):
    inactive_pet = PetFactory(owner=pet_context.owner, is_active=False)

    with pytest.raises(NotFoundException):
        PetService.get_pet_detail(pet_context.owner, inactive_pet.id)

    with pytest.raises(NotFoundException):
        PetService.get_pet_detail(pet_context.owner, 999999)


def test_update_pet_success(pet_context):
    pet = PetFactory(owner=pet_context.owner)

    updated_pet = PetService.update_pet(
        pet_context.owner,
        pet.id,
        {
            "name": "Milu Updated",
            "breed": "Shiba",
            "weight": "7.25",
            "note": "Updated note",
        },
    )

    assert updated_pet.name == "Milu Updated"
    assert updated_pet.breed == "Shiba"
    assert str(updated_pet.weight) == "7.25"
    assert updated_pet.note == "Updated note"


def test_update_pet_rejects_another_owners_pet(pet_context):
    pet = PetFactory(owner=pet_context.other_owner)

    with pytest.raises(BusinessException):
        PetService.update_pet(pet_context.owner, pet.id, {"name": "Updated"})


def test_delete_pet_soft_deletes_owned_pet(pet_context):
    pet = PetFactory(owner=pet_context.owner)

    PetService.delete_pet(pet_context.owner, pet.id)

    pet.refresh_from_db()
    assert pet.is_active is False


def test_delete_pet_rejects_another_owners_pet(pet_context):
    pet = PetFactory(owner=pet_context.other_owner)

    with pytest.raises(BusinessException):
        PetService.delete_pet(pet_context.owner, pet.id)
