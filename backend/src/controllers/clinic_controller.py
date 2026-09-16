from rest_framework import status
from rest_framework.views import APIView

from src.common.permissions import IsAdminUserRole, IsReadOnlyOrAdminRole
from src.common.responses import success_response
from src.serializers.clinic_serializer import (
    ClinicCreateSerializer,
    ClinicSerializer,
    ClinicUpdateSerializer,
    ServiceCreateSerializer,
    ServiceSerializer,
    ServiceUpdateSerializer,
)
from src.services.clinic_service import ClinicService, ServiceService


class ClinicListCreateAPIView(APIView):
    """
    GET  : Ai cũng có thể xem danh sách phòng khám
    POST : Chỉ ADMIN mới được tạo phòng khám
    """

    permission_classes = [IsReadOnlyOrAdminRole]

    def get(self, request):
        clinics = ClinicService.get_all_clinics()
        serializer = ClinicSerializer(clinics, many=True)
        return success_response(serializer.data, "Lấy danh sách phòng khám thành công")

    def post(self, request):
        serializer = ClinicCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        clinic = ClinicService.create_clinic(serializer.validated_data)
        output = ClinicSerializer(clinic)
        return success_response(
            output.data,
            "Tạo phòng khám thành công",
            status.HTTP_201_CREATED,
        )


class ClinicDetailAPIView(APIView):
    """
    GET    : Ai cũng có thể xem chi tiết phòng khám
    PUT    : Chỉ ADMIN mới được cập nhật phòng khám
    DELETE : Chỉ ADMIN mới được xóa phòng khám
    """

    permission_classes = [IsReadOnlyOrAdminRole]

    def get(self, request, clinic_id):
        clinic = ClinicService.get_clinic_detail(clinic_id)
        serializer = ClinicSerializer(clinic)
        return success_response(serializer.data, "Lấy chi tiết phòng khám thành công")

    def put(self, request, clinic_id):
        serializer = ClinicUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        clinic = ClinicService.update_clinic(clinic_id, serializer.validated_data)
        output = ClinicSerializer(clinic)
        return success_response(output.data, "Cập nhật phòng khám thành công")

    def delete(self, request, clinic_id):
        ClinicService.delete_clinic(clinic_id)
        return success_response(message="Xóa phòng khám thành công")


class ServiceCreateAPIView(APIView):
    """
    POST : Chỉ ADMIN mới được tạo dịch vụ
    """

    permission_classes = [IsAdminUserRole]

    def post(self, request):
        serializer = ServiceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ServiceService.create_service(serializer.validated_data)
        output = ServiceSerializer(service)
        return success_response(
            output.data,
            "Tạo dịch vụ thành công",
            status.HTTP_201_CREATED,
        )


class ServiceUpdateDeleteAPIView(APIView):
    """
    PUT    : Chỉ ADMIN mới được cập nhật dịch vụ
    DELETE : Chỉ ADMIN mới được xóa dịch vụ
    """

    permission_classes = [IsAdminUserRole]

    def put(self, request, service_id):
        serializer = ServiceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = ServiceService.update_service(service_id, serializer.validated_data)
        output = ServiceSerializer(service)
        return success_response(output.data, "Cập nhật dịch vụ thành công")

    def delete(self, request, service_id):
        ServiceService.delete_service(service_id)
        return success_response(message="Xóa dịch vụ thành công")


class ServiceByClinicAPIView(APIView):
    """
    GET : Ai cũng có thể xem danh sách dịch vụ của một phòng khám
    """

    def get(self, request, clinic_id):
        services = ServiceService.get_services_by_clinic(clinic_id)
        serializer = ServiceSerializer(services, many=True)
        return success_response(serializer.data, "Lấy danh sách dịch vụ thành công")
