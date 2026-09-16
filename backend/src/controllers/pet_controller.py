from rest_framework import status
from rest_framework.views import APIView

from src.common.permissions import IsPetOwnerRole
from src.common.responses import success_response
from src.serializers.pet_serializer import (
    PetCreateSerializer,
    PetSerializer,
    PetUpdateSerializer,
)
from src.services.pet_service import PetService


class PetListCreateAPIView(APIView):
    permission_classes = [IsPetOwnerRole]

    def get(self, request):
        pets = PetService.get_user_pets(request.user)
        serializer = PetSerializer(pets, many=True)
        return success_response(serializer.data, "Lấy danh sách thú cưng thành công")

    def post(self, request):
        serializer = PetCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pet = PetService.create_pet(request.user, serializer.validated_data)
        output = PetSerializer(pet)
        return success_response(
            output.data,
            "Tạo thú cưng thành công",
            status.HTTP_201_CREATED,
        )


class PetDetailAPIView(APIView):
    permission_classes = [IsPetOwnerRole]

    def get(self, request, pet_id):
        pet = PetService.get_pet_detail(request.user, pet_id)
        serializer = PetSerializer(pet)
        return success_response(serializer.data, "Lấy chi tiết thú cưng thành công")

    def put(self, request, pet_id):
        serializer = PetUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        pet = PetService.update_pet(request.user, pet_id, serializer.validated_data)
        output = PetSerializer(pet)
        return success_response(output.data, "Cập nhật thú cưng thành công")

    def delete(self, request, pet_id):
        PetService.delete_pet(request.user, pet_id)
        return success_response(message="Xóa thú cưng thành công")
