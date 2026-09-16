from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from src.common.permissions import IsPetOwnerRole
from src.common.responses import success_response
from src.serializers.payment_serializer import (
    PaymentCreateSerializer,
    PaymentSerializer,
)
from src.services.payment_service import PaymentService


class PaymentListCreateAPIView(APIView):
    permission_classes = [IsPetOwnerRole]

    def get(self, request):
        payments = PaymentService.get_user_payments(request.user)
        serializer = PaymentSerializer(payments, many=True)
        return success_response(serializer.data, "Lay danh sach thanh toan thanh cong")

    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment = PaymentService.create_payment(request.user, serializer.validated_data)
        output = PaymentSerializer(payment)
        return success_response(
            output.data,
            "Tao thanh toan thanh cong",
            status.HTTP_201_CREATED,
        )


class PaymentDetailAPIView(APIView):
    permission_classes = [IsPetOwnerRole]

    def get(self, request, payment_id):
        payment = PaymentService.get_payment_detail(request.user, payment_id)
        serializer = PaymentSerializer(payment)
        return success_response(serializer.data, "Lay chi tiet thanh toan thanh cong")


class VnpayCreatePaymentUrlAPIView(APIView):
    permission_classes = [IsPetOwnerRole]

    def post(self, request, payment_id):
        payment_url = PaymentService.create_vnpay_payment_url(
            request.user,
            payment_id,
            request,
        )
        return success_response(
            {"payment_url": payment_url},
            "Tao URL thanh toan VNPAY thanh cong",
        )


class VnpayIpnAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        query_params = (
            request.query_params.dict()
            if hasattr(request.query_params, "dict")
            else dict(request.query_params)
        )
        result = PaymentService.handle_vnpay_ipn(query_params)
        return Response(result)


class VnpayReturnAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        query_params = (
            request.query_params.dict()
            if hasattr(request.query_params, "dict")
            else dict(request.query_params)
        )
        result = PaymentService.handle_vnpay_return(query_params)
        return success_response(result, "Xac nhan ket qua thanh toan VNPAY thanh cong")
