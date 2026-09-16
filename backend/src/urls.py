from django.urls import path
from src.controllers.user_controller import (
    ChangePasswordAPIView,
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    ProfileAPIView,
    RefreshTokenAPIView,
    StaffAdminDetailAPIView,
    StaffAdminListCreateAPIView,
)
from src.controllers.appointment_controller import (
    AppointmentListCreateAPIView,
    StaffClinicAppointmentListAPIView,
    StaffClinicAppointmentDetailAPIView,
    AppointmentDetailAPIView,
    AppointmentConfirmAPIView,
    AppointmentCheckInAPIView,
    AppointmentStartAPIView,
    AppointmentCompleteAPIView,
    AppointmentNoShowAPIView,
)
from src.controllers.pet_controller import (
    PetListCreateAPIView,
    PetDetailAPIView,
)
from src.controllers.medical_record_controller import (
    AppointmentMedicalRecordAPIView,
    MedicalRecordDetailAPIView,
    PetMedicalRecordListAPIView,
    PetOwnerMedicalRecordListAPIView,
    PetOwnerMedicalRecordDetailAPIView,
)
from src.controllers.medicine_controller import (
    MedicineListCreateAPIView,
    MedicineDetailAPIView,
)
from src.controllers.prescription_controller import (
    MedicalRecordPrescriptionAPIView,
    PrescriptionDetailAPIView,
    PrescriptionItemListCreateAPIView,
    PrescriptionItemDetailAPIView,
    PetOwnerMedicalRecordPrescriptionAPIView,
)
from src.controllers.payment_controller import (
    PaymentDetailAPIView,
    PaymentListCreateAPIView,
    VnpayCreatePaymentUrlAPIView,
    VnpayIpnAPIView,
    VnpayReturnAPIView,
)
from src.controllers.report_controller import (
    AdminClinicReportAPIView,
    AdminReportOverviewAPIView,
    AdminRevenueReportAPIView,
)
from src.controllers.clinic_controller import (
    ClinicListCreateAPIView,
    ClinicDetailAPIView,
    ServiceCreateAPIView,
    ServiceUpdateDeleteAPIView,
    ServiceByClinicAPIView,
)
urlpatterns = [
    # Auth
    path("auth/register/", RegisterAPIView.as_view(), name="register"),
    path("auth/login/", LoginAPIView.as_view(), name="login"),
    path("auth/refresh/", RefreshTokenAPIView.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutAPIView.as_view(), name="logout"),
    path("auth/profile/", ProfileAPIView.as_view(), name="profile"),
    path("auth/change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path("admin/staffs/", StaffAdminListCreateAPIView.as_view(), name="admin-staff-list-create"),
    path("admin/staffs/<int:staff_id>/", StaffAdminDetailAPIView.as_view(), name="admin-staff-detail"),
    path("admin/reports/overview/", AdminReportOverviewAPIView.as_view(), name="admin-report-overview"),
    path("admin/reports/revenue/", AdminRevenueReportAPIView.as_view(), name="admin-report-revenue"),
    path("admin/reports/clinics/", AdminClinicReportAPIView.as_view(), name="admin-report-clinics"),

    # Pets
    path("pets/", PetListCreateAPIView.as_view(), name="pet-list-create"),
    path("pets/<int:pet_id>/", PetDetailAPIView.as_view(), name="pet-detail"),

    # Clinics
    path("clinics/", ClinicListCreateAPIView.as_view(), name="clinic-list-create"),
    path("clinics/<int:clinic_id>/", ClinicDetailAPIView.as_view(), name="clinic-detail"),

    # Services
    path("services/", ServiceCreateAPIView.as_view(), name="service-create"),
    path("services/<int:service_id>/", ServiceUpdateDeleteAPIView.as_view(), name="service-update-delete"),
    path("clinics/<int:clinic_id>/services/", ServiceByClinicAPIView.as_view(), name="service-by-clinic"),

    # Appointments
    path("appointments/", AppointmentListCreateAPIView.as_view(), name="appointment-list-create"),
    path("appointments/clinic/", StaffClinicAppointmentListAPIView.as_view(), name="appointment-clinic-list"),
    path("appointments/clinic/<int:appointment_id>/", StaffClinicAppointmentDetailAPIView.as_view(), name="appointment-clinic-detail"),
    path("appointments/<int:appointment_id>/", AppointmentDetailAPIView.as_view(), name="appointment-detail"),
    path("appointments/<int:appointment_id>/confirm/", AppointmentConfirmAPIView.as_view(), name="appointment-confirm"),
    path("appointments/<int:appointment_id>/check-in/", AppointmentCheckInAPIView.as_view(), name="appointment-check-in"),
    path("appointments/<int:appointment_id>/start/", AppointmentStartAPIView.as_view(), name="appointment-start"),
    path("appointments/<int:appointment_id>/complete/", AppointmentCompleteAPIView.as_view(), name="appointment-complete"),
    path("appointments/<int:appointment_id>/no-show/", AppointmentNoShowAPIView.as_view(), name="appointment-no-show"),

    # Medical Records
    path("appointments/<int:appointment_id>/medical-record/", AppointmentMedicalRecordAPIView.as_view(), name="appointment-medical-record"),
    path("medical-records/<int:record_id>/", MedicalRecordDetailAPIView.as_view(), name="medical-record-detail"),
    path("pets/<int:pet_id>/medical-records/", PetMedicalRecordListAPIView.as_view(), name="pet-medical-record-list"),
    path("owner/pets/<int:pet_id>/medical-records/", PetOwnerMedicalRecordListAPIView.as_view(), name="owner-pet-medical-record-list"),
    path("owner/medical-records/<int:record_id>/", PetOwnerMedicalRecordDetailAPIView.as_view(), name="owner-medical-record-detail"),

    # Medicines
    path("medicines/", MedicineListCreateAPIView.as_view(), name="medicine-list-create"),
    path("medicines/<int:medicine_id>/", MedicineDetailAPIView.as_view(), name="medicine-detail"),

    # Prescriptions
    path("medical-records/<int:medical_record_id>/prescription/", MedicalRecordPrescriptionAPIView.as_view(), name="medical-record-prescription"),
    path("prescriptions/<int:prescription_id>/", PrescriptionDetailAPIView.as_view(), name="prescription-detail"),
    path("prescriptions/<int:prescription_id>/items/", PrescriptionItemListCreateAPIView.as_view(), name="prescription-item-list-create"),
    path("prescription-items/<int:item_id>/", PrescriptionItemDetailAPIView.as_view(), name="prescription-item-detail"),
    path("owner/medical-records/<int:medical_record_id>/prescription/", PetOwnerMedicalRecordPrescriptionAPIView.as_view(), name="owner-medical-record-prescription"),

    # Payments
    path("payments/", PaymentListCreateAPIView.as_view(), name="payment-list-create"),
    path("payments/<int:payment_id>/", PaymentDetailAPIView.as_view(), name="payment-detail"),
    path("payments/<int:payment_id>/vnpay/create-url/", VnpayCreatePaymentUrlAPIView.as_view(), name="payment-vnpay-create-url"),
    path("payments/vnpay/ipn/", VnpayIpnAPIView.as_view(), name="payment-vnpay-ipn"),
    path("payments/vnpay/return/", VnpayReturnAPIView.as_view(), name="payment-vnpay-return"),
]
