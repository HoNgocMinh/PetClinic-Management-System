import axios from "axios";
import cookie from 'react-cookies';

// Địa chỉ Backend Django của bạn
const BASE_URL = 'http://127.0.0.1:8000/api/';

export const endpoint = {
    // Auth
    'register': '/auth/register/',
    'login': '/auth/login/',
    'refresh': '/auth/refresh/',
    'logout': '/auth/logout/',
    'current_user': '/auth/profile/',
    'change_password': '/auth/change-password/',

    // Pets
    'pets': '/pets/',
    'pet_detail': (petId) => `/pets/${petId}/`,

    // Clinics & Services
    'clinics': '/clinics/',
    'services': '/services/',
    'services_by_clinic': (clinicId) => `/clinics/${clinicId}/services/`,
    'users': '/users/',
    'admin_staffs': '/admin/staffs/', 
    'admin_report_overview': '/admin/reports/overview/',
    'admin_report_revenue': '/admin/reports/revenue/',
    'admin_report_clinics': '/admin/reports/clinics/',
    // Appointments (Chung & Staff)
    'appointments': '/appointments/',
    'staff_clinic_appointments': '/appointments/clinic/', // Mới bổ sung
    'appointment_detail': (appId) => `/appointments/${appId}/`,
    'appointment_confirm': (appId) => `/appointments/${appId}/confirm/`,
    'appointment_check_in': (appId) => `/appointments/${appId}/check-in/`,
    'appointment_start': (appId) => `/appointments/${appId}/start/`,
    'appointment_complete': (appId) => `/appointments/${appId}/complete/`, // Mới bổ sung
    'appointment_no_show': (appId) => `/appointments/${appId}/no-show/`,

    // Medical Records
    'appointment_medical_record': (appId) => `/appointments/${appId}/medical-record/`, // Dành cho Staff tạo record
    'medical_record_detail': (recordId) => `/medical-records/${recordId}/`,
    'medical_records_by_pet': (petId) => `/pets/${petId}/medical-records/`,

    // Medical Records dành cho Pet Owner
    'owner_pet_medical_records': (petId) => `/owner/pets/${petId}/medical-records/`,
    'owner_medical_record_detail': (recordId) => `/owner/medical-records/${recordId}/`,

    // Medicines & Prescriptions (Staff)[cite: 23]
    'medicines': '/medicines/',
    'medicine_detail': (medId) => `/medicines/${medId}/`,
    'medical_record_prescription': (recordId) => `/medical-records/${recordId}/prescription/`,
    'prescription_items': (presId) => `/prescriptions/${presId}/items/`, // Thêm thuốc vào đơn

    'pet_medical_records': (petId) => `/pets/${petId}/medical-records/`,
    'medical_record_detail': (recordId) => `/medical-records/${recordId}/`,

    // Prescriptions dành cho Pet Owner[cite: 23]
    'owner_prescription_by_record': (recordId) => `/owner/medical-records/${recordId}/prescription/`,
    // Medical Records (Dành cho Owner - Backend đã có sẵn)
    'owner_medical_record_detail': (recordId) => `/owner/medical-records/${recordId}/`,

    // Prescriptions (Dành cho Owner - Backend đã có sẵn)
    'owner_prescription_by_record': (recordId) => `/owner/medical-records/${recordId}/prescription/`,

    // Lấy Hồ sơ từ Lịch hẹn (Cho Staff)
    'appointment_medical_record': (appId) => `/appointments/${appId}/medical-record/`,
    // THÊM CÁC DÒNG NÀY (Dành cho Owner)
    'owner_medical_record_by_app': (appId) => `/owner/appointments/${appId}/medical-record/`,
    'owner_medical_record_detail': (recordId) => `/owner/medical-records/${recordId}/`,
    'owner_medical_record_prescription': (recordId) => `/owner/medical-records/${recordId}/prescription/`,

    // Payments
    'payment_detail': (paymentId) => `/payments/${paymentId}/`,
    'payment_vnpay_create_url': (paymentId) => `/payments/${paymentId}/vnpay/create-url/`,
    'payment_vnpay_return': '/payments/vnpay/return/',

};

// Instance cho các request công khai (Login, Register)
export default axios.create({
    baseURL: BASE_URL
});

// Instance cho các request cần đăng nhập (Có gắn Token)
export const authApis = () => {
    return axios.create({
        baseURL: BASE_URL,
        headers: {
            'Authorization': `Bearer ${cookie.load('token')}`
        }
    });
};

// Instance cho upload file (Ảnh đại diện, ảnh thú cưng)
export const authFormDataApis = () => {
    return axios.create({
        baseURL: BASE_URL,
        headers: {
            'Authorization': `Bearer ${cookie.load('token')}`,
            'Content-Type': 'multipart/form-data'
        }
    });
};
