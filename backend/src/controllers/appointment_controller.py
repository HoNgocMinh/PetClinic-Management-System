from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from src.common.permissions import IsClinicStaffRole, IsPetOwnerRole
from src.common.responses import success_response
from src.serializers.appointment_serializer import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
    AppointmentUpdateSerializer,
)
from src.services.appointment_service import AppointmentService


class AppointmentListCreateAPIView(APIView):
    permission_classes = [IsPetOwnerRole]

    def get(self, request):
        appointments = AppointmentService.get_user_appointments(request.user)
        serializer = AppointmentSerializer(appointments, many=True)
        return success_response(serializer.data, "Lấy danh sách lịch hẹn thành công")

    def post(self, request):
        serializer = AppointmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment = AppointmentService.create_appointment(request.user, serializer.validated_data)
        output = AppointmentSerializer(appointment)
        return success_response(
            output.data,
            "Tạo lịch hẹn thành công",
            status.HTTP_201_CREATED,
        )


class StaffClinicAppointmentListAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request):
        appointments = AppointmentService.get_clinic_appointments(request.user)
        serializer = AppointmentSerializer(appointments, many=True)
        return success_response(serializer.data, "Lấy danh sách lịch hẹn theo phòng khám thành công")


class StaffClinicAppointmentDetailAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request, appointment_id):
        appointment = AppointmentService.get_clinic_appointment_detail(request.user, appointment_id)
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Lấy chi tiết lịch hẹn theo phòng khám thành công")


class AppointmentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, appointment_id):
        appointment = AppointmentService.get_appointment_detail(request.user, appointment_id)
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Lấy chi tiết lịch hẹn thành công")

    def put(self, request, appointment_id):
        serializer = AppointmentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment = AppointmentService.update_appointment(
            request.user,
            appointment_id,
            serializer.validated_data,
        )
        output = AppointmentSerializer(appointment)
        return success_response(output.data, "Cập nhật lịch hẹn thành công")

    def delete(self, request, appointment_id):
        appointment = AppointmentService.cancel_appointment(request.user, appointment_id)
        output = AppointmentSerializer(appointment)
        return success_response(output.data, "Hủy lịch hẹn thành công")


class AppointmentCheckInAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def post(self, request, appointment_id):
        appointment = AppointmentService.check_in(request.user, appointment_id)
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Check-in thành công")


class AppointmentConfirmAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def post(self, request, appointment_id):
        appointment = AppointmentService.confirm_appointment(request.user, appointment_id)
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Xác nhận lịch hẹn thành công")


class AppointmentStartAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def post(self, request, appointment_id):
        appointment = AppointmentService.start_appointment(request.user, appointment_id)
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Bắt đầu khám thành công")


class AppointmentCompleteAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def post(self, request, appointment_id):
        appointment = AppointmentService.complete_appointment(request.user, appointment_id)
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Hoàn tất lịch hẹn thành công")


class AppointmentNoShowAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def post(self, request, appointment_id):
        appointment = AppointmentService.mark_no_show(request.user, appointment_id)
        serializer = AppointmentSerializer(appointment)
        return success_response(serializer.data, "Đánh dấu vắng mặt thành công")
