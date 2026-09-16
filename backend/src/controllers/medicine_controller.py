from rest_framework import status
from rest_framework.views import APIView

from src.common.permissions import IsClinicStaffRole
from src.common.responses import success_response
from src.serializers.medicine_serializer import (
    MedicineCreateSerializer,
    MedicineSerializer,
    MedicineUpdateSerializer,
)
from src.services.medicine_service import MedicineService


class MedicineListCreateAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request):
        status_filter = request.query_params.get("status", "active")
        medicines = MedicineService.get_clinic_medicines(request.user, status=status_filter)
        serializer = MedicineSerializer(medicines, many=True)
        return success_response(serializer.data, "Lấy danh sách thuốc thành công")

    def post(self, request):
        serializer = MedicineCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        medicine = MedicineService.create_medicine(request.user, serializer.validated_data)
        output = MedicineSerializer(medicine)
        return success_response(
            output.data,
            "Tạo thuốc thành công",
            status.HTTP_201_CREATED,
        )


class MedicineDetailAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request, medicine_id):
        medicine = MedicineService.get_medicine_detail(request.user, medicine_id)
        serializer = MedicineSerializer(medicine)
        return success_response(serializer.data, "Lấy chi tiết thuốc thành công")

    def put(self, request, medicine_id):
        serializer = MedicineUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        medicine = MedicineService.update_medicine(
            request.user,
            medicine_id,
            serializer.validated_data,
        )
        output = MedicineSerializer(medicine)
        return success_response(output.data, "Cập nhật thuốc thành công")

    def delete(self, request, medicine_id):
        medicine = MedicineService.delete_medicine(request.user, medicine_id)
        output = MedicineSerializer(medicine)
        return success_response(output.data, "Xóa thuốc thành công")

    def patch(self, request, medicine_id):
        return self.put(request, medicine_id)