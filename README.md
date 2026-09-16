# Phòng Khám Thú Y Tích hợp hồ sơ bệnh án điện tử 2DEL

## Mô tả
2DEL là hệ thống quản lý phòng khám thú y hỗ trợ chủ thú cưng đặt lịch khám, theo dõi lịch hẹn, xem hồ sơ điều trị và thanh toán trực tuyến qua VNPAY sandbox. Nhân viên phòng khám có thể quản lý quy trình tiếp nhận, khám bệnh, tạo hồ sơ y tế, kê đơn thuốc và hoàn tất ca khám. Admin quản lý phòng khám, nhân viên, dịch vụ và xem báo cáo doanh thu.

## Thông tin sinh viên thực hiện
* **Sinh viên thực hiện:** HỒ NGỌC MINH
* **Mã số sinh viên:** 2251012092
* **Ngành:** Khoa học Máy tính
* **Trường:** Trường Đại học Mở Thành phố Hồ Chí Minh
* **Giảng viên hướng dẫn:** Th.S NGUYỄN TRUNG HẬU

## Chức năng chính
- Đăng ký, đăng nhập và phân quyền theo vai trò: chủ thú cưng, nhân viên phòng khám, admin.
- Chủ thú cưng quản lý hồ sơ thú cưng, đặt lịch khám và xem lịch sử điều trị.
- Nhân viên phòng khám xác nhận lịch hẹn, check-in, bắt đầu khám, nhập kết quả và kê đơn thuốc.
- Thanh toán trực tuyến qua VNPAY sandbox cho lịch hẹn ở trạng thái chờ thanh toán.
- Admin quản lý phòng khám, nhân viên, dịch vụ và xem báo cáo tổng quan.
- Báo cáo doanh thu theo ngày/tháng, thống kê trạng thái lịch hẹn và hiệu suất từng phòng khám.

## Công nghệ sử dụng
### Backend
- Python
- Django 6.0.3
- Django REST Framework 3.17.1
- Simple JWT
- django-cors-headers
- MySQL, `mysqlclient`
- Pytest, pytest-django, factory_boy, coverage

### Frontend
- React 19
- Vite 8
- React Router DOM 7
- Axios
- React Bootstrap, Bootstrap 5
- React Hot Toast
- Moment.js
- React Icons
- react-cookies

### Tích hợp
- VNPAY sandbox payment gateway
- JWT authentication
- RESTful API

## Cài đặt và chạy
### Yêu cầu
- Python 3.13+
- Node.js 18+
- MySQL
- Tài khoản sandbox VNPAY nếu muốn test thanh toán

### Cấu hình backend
Tạo hoặc cập nhật file `backend/.env`:

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DJANGO_CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

DB_ENGINE=django.db.backends.mysql
DB_NAME=pet_care_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_CHARSET=utf8mb4

VNPAY_TMN_CODE=your-vnpay-tmn-code
VNPAY_HASH_SECRET=your-vnpay-hash-secret
VNPAY_PAYMENT_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
VNPAY_RETURN_URL=http://localhost:5173/payment-result
VNPAY_IPN_URL=http://localhost:8000/api/payments/vnpay/ipn/
```

### Chạy Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

Backend API chạy tại:

```text
http://127.0.0.1:8000/api/
```

### Chạy Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend chạy tại:

```text
http://localhost:5173
```

## Tài khoản và phân quyền
- `PET_OWNER`: chủ thú cưng, đặt lịch và thanh toán.
- `CLINIC_STAFF`: nhân viên phòng khám, xử lý lịch hẹn và hồ sơ khám.
- `ADMIN`: quản trị hệ thống, quản lý dữ liệu và xem báo cáo.

## Luồng nghiệp vụ thanh toán
1. Chủ thú cưng đặt lịch khám.
2. Nhân viên xác nhận, check-in và bắt đầu khám.
3. Nhân viên hoàn tất khám, lịch hẹn chuyển sang `WAITING_PAYMENT`.
4. Hệ thống tạo payment ở trạng thái `PENDING`.
5. Chủ thú cưng xác nhận thanh toán và được chuyển sang VNPAY sandbox.
6. Sau khi thanh toán thành công, payment chuyển sang `PAID`, lịch hẹn chuyển sang `COMPLETED`.

## Kiểm thử
Chạy test backend:

```bash
cd backend
venv\Scripts\activate
pytest
```

Chạy build frontend:

```bash
cd frontend
npm run build
```

## Demo
[Link video demo hoặc screenshots]

## Tài liệu
- [Phân tích yêu cầu](docs/requirements.md)
- [Database Design](docs/database-design.md)
- [Test Plan](docs/test-plan.md)
- [API Documentation](docs/api-docs.md)
