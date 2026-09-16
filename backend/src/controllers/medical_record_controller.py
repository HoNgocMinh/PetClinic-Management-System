from rest_framework.views import APIView

from src.common.permissions import IsClinicStaffRole, IsPetOwnerRole
from src.common.responses import success_response
from src.serializers.medical_record_serializer import (
    MedicalRecordCreateSerializer,
    MedicalRecordSerializer,
    MedicalRecordUpdateSerializer,
)
from src.services.medical_record_service import MedicalRecordService


class AppointmentMedicalRecordAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request, appointment_id):
        record = MedicalRecordService.get_medical_record_by_appointment(request.user, appointment_id)
        serializer = MedicalRecordSerializer(record)
        return success_response(serializer.data, "Lấy hồ sơ bệnh án thành công")

    def post(self, request, appointment_id):
        serializer = MedicalRecordCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record = MedicalRecordService.create_medical_record(
            request.user,
            appointment_id,
            serializer.validated_data,
        )
        output = MedicalRecordSerializer(record)
        return success_response(output.data, "Tạo hồ sơ bệnh án thành công", 201)


class MedicalRecordDetailAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request, record_id):
        record = MedicalRecordService.get_medical_record_detail(request.user, record_id)
        serializer = MedicalRecordSerializer(record)
        return success_response(serializer.data, "Lấy chi tiết hồ sơ bệnh án thành công")

    def put(self, request, record_id):
        serializer = MedicalRecordUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        record = MedicalRecordService.update_medical_record(
            request.user,
            record_id,
            serializer.validated_data,
        )
        output = MedicalRecordSerializer(record)
        return success_response(output.data, "Cập nhật hồ sơ bệnh án thành công")


class PetMedicalRecordListAPIView(APIView):
    permission_classes = [IsClinicStaffRole]

    def get(self, request, pet_id):
        records = MedicalRecordService.get_pet_medical_records(request.user, pet_id)
        serializer = MedicalRecordSerializer(records, many=True)
        return success_response(serializer.data, "Lấy lịch sử hồ sơ bệnh án của thú cưng thành công")


class PetOwnerMedicalRecordListAPIView(APIView):
    permission_classes = [IsPetOwnerRole]

    def get(self, request, pet_id):
        records = MedicalRecordService.get_pet_owner_medical_records(request.user, pet_id)
        serializer = MedicalRecordSerializer(records, many=True)
        return success_response(serializer.data, "Lấy lịch sử hồ sơ bệnh án của thú cưng thành công")


class PetOwnerMedicalRecordDetailAPIView(APIView):
    permission_classes = [IsPetOwnerRole]

    def get(self, request, record_id):
        record = MedicalRecordService.get_pet_owner_medical_record_detail(request.user, record_id)
        serializer = MedicalRecordSerializer(record)
        return success_response(serializer.data, "Lấy chi tiết hồ sơ bệnh án thành công")
