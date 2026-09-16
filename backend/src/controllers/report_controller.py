from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from src.common.permissions import IsAdminUserRole
from src.common.responses import success_response
from src.serializers.report_serializer import (
    ReportDateRangeSerializer,
    RevenueReportQuerySerializer,
)
from src.services.report_service import ReportService


class AdminReportOverviewAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        serializer = ReportDateRangeSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = ReportService.get_overview(**serializer.validated_data)
        return success_response(data, "Lấy báo cáo tổng quan thành công")


class AdminRevenueReportAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        serializer = RevenueReportQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = ReportService.get_revenue_report(**serializer.validated_data)
        return success_response(data, "Lấy báo cáo doanh thu thành công")


class AdminClinicReportAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUserRole]

    def get(self, request):
        serializer = ReportDateRangeSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        data = ReportService.get_clinic_report(**serializer.validated_data)
        return success_response(data, "Lấy báo cáo phòng khám thành công")
