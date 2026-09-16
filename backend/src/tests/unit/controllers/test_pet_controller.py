import pytest
from rest_framework import status

from src.controllers.pet_controller import PetDetailAPIView, PetListCreateAPIView
from src.tests.factories import PetFactory, UserFactory
from src.tests.unit.controllers.helpers import assert_success, make_request, pet_payload


pytestmark = pytest.mark.django_db


def test_pet_controller_delegates_pet_flows(mocker):
    owner = UserFactory()
    pet = PetFactory(owner=owner)

    mocker.patch("src.controllers.pet_controller.PetService.get_user_pets", return_value=[pet])
    assert_success(PetListCreateAPIView().get(make_request(owner)))

    mocker.patch("src.controllers.pet_controller.PetService.create_pet", return_value=pet)
    assert_success(
        PetListCreateAPIView().post(make_request(owner, pet_payload())),
        status.HTTP_201_CREATED,
    )

    mocker.patch("src.controllers.pet_controller.PetService.get_pet_detail", return_value=pet)
    assert_success(PetDetailAPIView().get(make_request(owner), pet.id))

    mocker.patch("src.controllers.pet_controller.PetService.update_pet", return_value=pet)
    assert_success(PetDetailAPIView().put(make_request(owner, {"name": "Milu"}), pet.id))

    mocker.patch("src.controllers.pet_controller.PetService.delete_pet")
    assert_success(PetDetailAPIView().delete(make_request(owner), pet.id))
