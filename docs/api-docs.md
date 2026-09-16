# Pet Care API Documentation

Tài liệu này mô tả các API chính của hệ thống quản lý thú cưng/phòng khám thú y.

## 1. Thông tin chung

### Base URL

```http
http://127.0.0.1:8000/api
```

### Header chung

Với các API cần đăng nhập:

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Format response thành công

```json
{
  "success": true,
  "message": "Thành công.",
  "data": {}
}
```

### Format response lỗi

```json
{
  "success": false,
  "message": "Dữ liệu không hợp lệ.",
  "errors": {}
}
```

### Role trong hệ thống

| Role | Mô tả |
|---|---|
| `PET_OWNER` | Chủ thú cưng |
| `CLINIC_STAFF` | Nhân viên phòng khám/groomer |
| `ADMIN` | Quản trị viên hệ thống |

### Enum thường dùng

| Nhóm | Giá trị |
|---|---|
| Pet species | `DOG`, `CAT`, `OTHER` |
| Pet gender | `MALE`, `FEMALE` |
| Service type | `EXAM`, `GROOMING`, `VACCINE`, `OTHER` |
| Appointment status | `PENDING`, `CONFIRMED`, `CHECKED_IN`, `IN_PROGRESS`, `WAITING_PAYMENT`, `COMPLETED`, `CANCELLED`, `NO_SHOW` |
| Payment method | `CASH`, `VNPAY` |
| Payment status | `PENDING`, `PAID`, `FAILED`, `CANCELLED` |

---

## 2. Auth APIs

### 2.1. Đăng ký tài khoản chủ thú cưng

```http
POST /auth/register/
```

Quyền: Public

Request body:

```json
{
  "username": "owner01",
  "email": "owner01@example.com",
  "password": "StrongPass123!",
  "full_name": "Nguyen Van A",
  "phone": "0900000000",
  "address": "Ho Chi Minh City"
}
```

Response `201`:

```json
{
  "success": true,
  "message": "Đăng ký thành công.",
  "data": {
    "id": 1,
    "username": "owner01",
    "email": "owner01@example.com",
    "full_name": "Nguyen Van A",
    "role": "PET_OWNER"
  }
}
```

### 2.2. Đăng nhập

```http
POST /auth/login/
```

Quyền: Public

Request body:

```json
{
  "username": "owner01",
  "password": "StrongPass123!"
}
```

Response `200`:

```json
{
  "success": true,
  "message": "Đăng nhập thành công.",
  "data": {
    "user": {
      "id": 1,
      "username": "owner01",
      "role": "PET_OWNER"
    },
    "access_token": "<access_token>",
    "refresh_token": "<refresh_token>"
  }
}
```

### 2.3. Refresh access token

```http
POST /auth/refresh/
```

Quyền: Public

Request body:

```json
{
  "refresh_token": "<refresh_token>"
}
```

### 2.4. Đăng xuất

```http
POST /auth/logout/
```

Quyền: Authenticated

Request body:

```json
{
  "refresh_token": "<refresh_token>"
}
```

### 2.5. Xem thông tin cá nhân

```http
GET /auth/profile/
```

Quyền: Authenticated

### 2.6. Cập nhật thông tin cá nhân

```http
PUT /auth/profile/
```

Quyền: Authenticated

Request body:

```json
{
  "full_name": "Nguyen Van A Updated",
  "phone": "0911111111",
  "address": "Updated address"
}
```

### 2.7. Đổi mật khẩu

```http
PUT /auth/change-password/
```

Quyền: Authenticated

Request body:

```json
{
  "old_password": "OldPass123!",
  "new_password": "NewPass123!",
  "confirm_password": "NewPass123!"
}
```

Ghi chú:

- `old_password` phải khớp với mật khẩu hiện tại của người dùng.
- `new_password` phải thỏa các rule validate mật khẩu của Django.
- `confirm_password` phải trùng với `new_password`.
- Sau khi đổi mật khẩu thành công, người dùng có thể đăng nhập bằng mật khẩu mới.

---

## 3. Pet Owner APIs

### 3.1. Danh sách thú cưng của tôi

```http
GET /pets/
```

Quyền: `PET_OWNER`

### 3.2. Tạo hồ sơ thú cưng

```http
POST /pets/
```

Quyền: `PET_OWNER`

Request body:

```json
{
  "name": "Milu",
  "species": "DOG",
  "breed": "Poodle",
  "gender": "MALE",
  "birth_date": "2022-01-15",
  "weight": "4.50",
  "note": "Friendly"
}
```

### 3.3. Chi tiết thú cưng

```http
GET /pets/{pet_id}/
```

Quyền: `PET_OWNER`

### 3.4. Cập nhật hồ sơ thú cưng

```http
PUT /pets/{pet_id}/
```

Quyền: `PET_OWNER`

Request body:

```json
{
  "name": "Milu Updated",
  "weight": "5.00",
  "note": "Updated note"
}
```

### 3.5. Xóa mềm hồ sơ thú cưng

```http
DELETE /pets/{pet_id}/
```

Quyền: `PET_OWNER`

---

## 4. Clinic và Service APIs

### 4.1. Danh sách phòng khám

```http
GET /clinics/
```

Quyền: Public

### 4.2. Tạo phòng khám

```http
POST /clinics/
```

Quyền: `ADMIN`

Request body:

```json
{
  "name": "PetCare Clinic Q1",
  "address": "123 Nguyen Trai",
  "phone": "0900000000",
  "email": "clinic@example.com"
}
```

### 4.3. Chi tiết phòng khám

```http
GET /clinics/{clinic_id}/
```

Quyền: Public

### 4.4. Cập nhật phòng khám

```http
PUT /clinics/{clinic_id}/
```

Quyền: `ADMIN`

Request body:

```json
{
  "name": "PetCare Clinic Q1 Updated",
  "address": "456 Nguyen Trai",
  "phone": "0911111111",
  "email": "clinic-updated@example.com",
  "is_active": true
}
```

### 4.5. Xóa mềm phòng khám

```http
DELETE /clinics/{clinic_id}/
```

Quyền: `ADMIN`

### 4.6. Tạo dịch vụ

```http
POST /services/
```

Quyền: `ADMIN`

Request body:

```json
{
  "clinic_id": 1,
  "name": "Khám tổng quát",
  "service_type": "EXAM",
  "description": "Dịch vụ khám sức khỏe tổng quát",
  "price": "100000.00",
  "duration_minutes": 60
}
```

### 4.7. Cập nhật dịch vụ

```http
PUT /services/{service_id}/
```

Quyền: `ADMIN`

Request body:

```json
{
  "name": "Khám tổng quát nâng cao",
  "price": "150000.00",
  "duration_minutes": 90,
  "is_active": true
}
```

### 4.8. Xóa mềm dịch vụ

```http
DELETE /services/{service_id}/
```

Quyền: `ADMIN`

### 4.9. Danh sách dịch vụ theo phòng khám

```http
GET /clinics/{clinic_id}/services/
```

Quyền: Public

---

## 5. Appointment APIs

### 5.1. Chủ thú cưng xem lịch hẹn của mình

```http
GET /appointments/
```

Quyền: `PET_OWNER`

Appointment response có các trường chính:

```json
{
  "id": 1,
  "owner": 1,
  "owner_username": "owner01",
  "pet": 1,
  "pet_name": "Milu",
  "clinic": 1,
  "clinic_name": "PetCare Clinic Q1",
  "service": 1,
  "service_name": "Khám tổng quát",
  "appointment_time": "2026-05-20T09:00:00+07:00",
  "note": "Khám sức khỏe định kỳ",
  "status": "PENDING",
  "medical_record_id": null,
  "payment": null,
  "created_at": "2026-05-10T09:00:00+07:00",
  "updated_at": "2026-05-10T09:00:00+07:00"
}
```

Ghi chú:

- `medical_record_id` là `null` nếu lịch hẹn chưa có hồ sơ bệnh án.
- Khi đã tạo bệnh án cho lịch hẹn, `medical_record_id` trả về id của hồ sơ bệnh án để frontend có thể gọi API chi tiết phù hợp với quyền người dùng.
- `payment` là `null` trước khi staff hoàn tất khám. Khi appointment ở `WAITING_PAYMENT` hoặc `COMPLETED`, field này trả về payment gắn với lịch hẹn.

### 5.2. Chủ thú cưng đặt lịch

```http
POST /appointments/
```

Quyền: `PET_OWNER`

Request body:

```json
{
  "pet_id": 1,
  "clinic_id": 1,
  "service_id": 1,
  "appointment_time": "2026-05-20T09:00:00+07:00",
  "note": "Khám sức khỏe định kỳ"
}
```

Ghi chú:

- `appointment_time` phải lớn hơn thời điểm hiện tại.
- `pet_id` phải thuộc về user đang đăng nhập.
- Service phải thuộc phòng khám đã chọn.
- Không được trùng khung giờ với lịch hẹn đang hoạt động của phòng khám.

### 5.3. Chi tiết lịch hẹn

```http
GET /appointments/{appointment_id}/
```

Quyền: `PET_OWNER`

### 5.4. Chủ thú cưng cập nhật lịch hẹn

```http
PUT /appointments/{appointment_id}/
```

Quyền: `PET_OWNER`

Request body:

```json
{
  "appointment_time": "2026-05-21T10:00:00+07:00",
  "note": "Đổi giờ hẹn"
}
```

### 5.5. Chủ thú cưng hủy lịch hẹn

```http
DELETE /appointments/{appointment_id}/
```

Quyền: `PET_OWNER`

### 5.6. Staff xem lịch hẹn của phòng khám

```http
GET /appointments/clinic/
```

Quyền: `CLINIC_STAFF`

### 5.7. Staff xem chi tiết lịch hẹn của phòng khám

```http
GET /appointments/clinic/{appointment_id}/
```

Quyền: `CLINIC_STAFF`

### 5.8. Staff xác nhận lịch hẹn

```http
POST /appointments/{appointment_id}/confirm/
```

Quyền: `CLINIC_STAFF`

Trạng thái hợp lệ: `PENDING` -> `CONFIRMED`

### 5.9. Staff check-in

```http
POST /appointments/{appointment_id}/check-in/
```

Quyền: `CLINIC_STAFF`

Trạng thái hợp lệ: `CONFIRMED` -> `CHECKED_IN`

### 5.10. Staff bắt đầu khám

```http
POST /appointments/{appointment_id}/start/
```

Quyền: `CLINIC_STAFF`

Trạng thái hợp lệ: `CHECKED_IN` -> `IN_PROGRESS`

### 5.11. Staff hoàn tất khám và tạo thanh toán

```http
POST /appointments/{appointment_id}/complete/
```

Quyền: `CLINIC_STAFF`

Trạng thái hợp lệ: `IN_PROGRESS` -> `WAITING_PAYMENT`

Ghi chú:

- Backend tự tạo `Payment` với trạng thái `PENDING` nếu lịch hẹn chưa có payment.
- `COMPLETED` chỉ được set sau khi owner xác nhận thanh toán thành công.

Response mẫu:

```json
{
  "success": true,
  "message": "Hoàn tất lịch hẹn thành công",
  "data": {
    "id": 1,
    "status": "WAITING_PAYMENT",
    "payment": {
      "id": 1,
      "appointment_id": 1,
      "amount": "110000.00",
      "method": "VNPAY",
      "status": "PENDING",
      "paid_at": null,
      "transaction_code": null
    }
  }
}
```

### 5.12. Staff đánh dấu vắng mặt

```http
POST /appointments/{appointment_id}/no-show/
```

Quyền: `CLINIC_STAFF`

Trạng thái hợp lệ: `CONFIRMED` -> `NO_SHOW`

---

## 6. Medical Record APIs

### 6.1. Staff xem bệnh án theo lịch hẹn

```http
GET /appointments/{appointment_id}/medical-record/
```

Quyền: `CLINIC_STAFF`

### 6.2. Staff tạo bệnh án cho lịch hẹn

```http
POST /appointments/{appointment_id}/medical-record/
```

Quyền: `CLINIC_STAFF`

Request body:

```json
{
  "symptoms": "Ho nhẹ, bỏ ăn",
  "diagnosis": "Viêm đường hô hấp nhẹ",
  "treatment": "Theo dõi và dùng thuốc",
  "note": "Tái khám sau 7 ngày nếu không giảm"
}
```

### 6.3. Staff xem chi tiết bệnh án

```http
GET /medical-records/{record_id}/
```

Quyền: `CLINIC_STAFF`

### 6.4. Staff cập nhật bệnh án

```http
PUT /medical-records/{record_id}/
```

Quyền: `CLINIC_STAFF`

Request body:

```json
{
  "symptoms": "Ho nhẹ",
  "diagnosis": "Viêm đường hô hấp nhẹ",
  "treatment": "Uống thuốc theo đơn",
  "note": "Cập nhật ghi chú"
}
```

### 6.5. Staff xem lịch sử bệnh án của thú cưng

```http
GET /pets/{pet_id}/medical-records/
```

Quyền: `CLINIC_STAFF`

### 6.6. Chủ thú cưng xem lịch sử bệnh án của thú cưng

```http
GET /owner/pets/{pet_id}/medical-records/
```

Quyền: `PET_OWNER`

### 6.7. Chủ thú cưng xem chi tiết bệnh án

```http
GET /owner/medical-records/{record_id}/
```

Quyền: `PET_OWNER`

---

## 7. Medicine APIs

### 7.1. Staff xem danh sách thuốc của phòng khám

```http
GET /medicines/?status=active
```

Quyền: `CLINIC_STAFF`

Query params:

| Tên | Bắt buộc | Mô tả |
|---|---|---|
| `status` | Không | `active`, `inactive`, `all`. Mặc định `active` |

### 7.2. Staff tạo thuốc

```http
POST /medicines/
```

Quyền: `CLINIC_STAFF`

Request body:

```json
{
  "name": "Amoxicillin",
  "unit": "tablet",
  "description": "Antibiotic",
  "stock_quantity": 100,
  "price": "5000.00"
}
```

### 7.3. Staff xem chi tiết thuốc

```http
GET /medicines/{medicine_id}/
```

Quyền: `CLINIC_STAFF`

### 7.4. Staff cập nhật thuốc

```http
PUT /medicines/{medicine_id}/
```

Quyền: `CLINIC_STAFF`

Request body:

```json
{
  "name": "Amoxicillin Updated",
  "unit": "capsule",
  "description": "Updated description",
  "stock_quantity": 120,
  "price": "6000.00",
  "is_active": true
}
```

### 7.5. Staff xóa mềm thuốc

```http
DELETE /medicines/{medicine_id}/
```

Quyền: `CLINIC_STAFF`

---

## 8. Prescription APIs

### 8.1. Staff xem đơn thuốc theo bệnh án

```http
GET /medical-records/{medical_record_id}/prescription/
```

Quyền: `CLINIC_STAFF`

### 8.2. Staff tạo đơn thuốc

```http
POST /medical-records/{medical_record_id}/prescription/
```

Quyền: `CLINIC_STAFF`

Request body:

```json
{
  "note": "Uống thuốc sau ăn"
}
```

### 8.3. Staff xem chi tiết đơn thuốc

```http
GET /prescriptions/{prescription_id}/
```

Quyền: `CLINIC_STAFF`

### 8.4. Staff cập nhật đơn thuốc

```http
PUT /prescriptions/{prescription_id}/
```

Quyền: `CLINIC_STAFF`

Request body:

```json
{
  "note": "Cập nhật hướng dẫn dùng thuốc"
}
```

### 8.5. Staff thêm thuốc vào đơn

```http
POST /prescriptions/{prescription_id}/items/
```

Quyền: `CLINIC_STAFF`

Request body:

```json
{
  "medicine_id": 1,
  "quantity": 2,
  "dosage": "1 viên",
  "frequency": "2 lần/ngày",
  "duration_days": 5,
  "instruction": "Uống sau ăn"
}
```

Ghi chú:

- Thuốc phải thuộc cùng phòng khám với staff.
- Số lượng thuốc tồn kho phải đủ.
- Một thuốc chỉ được xuất hiện một lần trong cùng đơn thuốc.

### 8.6. Staff cập nhật chi tiết thuốc trong đơn

```http
PUT /prescription-items/{item_id}/
```

Quyền: `CLINIC_STAFF`

Request body:

```json
{
  "quantity": 3,
  "dosage": "1 viên",
  "frequency": "3 lần/ngày",
  "duration_days": 5,
  "instruction": "Uống sau ăn"
}
```

### 8.7. Staff xóa thuốc khỏi đơn

```http
DELETE /prescription-items/{item_id}/
```

Quyền: `CLINIC_STAFF`

### 8.8. Chủ thú cưng xem đơn thuốc theo bệnh án

```http
GET /owner/medical-records/{medical_record_id}/prescription/
```

Quyền: `PET_OWNER`

---

## 9. Payment APIs

### 9.1. Chủ thú cưng xem danh sách thanh toán

```http
GET /payments/
```

Quyền: `PET_OWNER`

### 9.2. Chủ thú cưng tạo thanh toán

```http
POST /payments/
```

Quyền: `PET_OWNER`

Ghi chú: trong luồng chính, payment đã được tạo tự động khi staff gọi `POST /appointments/{appointment_id}/complete/`. Endpoint này dùng cho trường hợp cần tạo payment thủ công cho appointment đang `WAITING_PAYMENT`.

Request body:

```json
{
  "appointment_id": 1,
  "method": "VNPAY",
  "note": "Thanh toán online"
}
```

Ghi chú:

- Chỉ chủ của lịch hẹn mới được tạo thanh toán.
- Chỉ lịch hẹn `WAITING_PAYMENT` mới được tạo thanh toán.
- Mỗi lịch hẹn chỉ có một payment.
- Backend tự tính `amount = service.price + tổng tiền thuốc trong đơn`, không lấy amount từ frontend.

### 9.3. Chủ thú cưng xem chi tiết thanh toán

```http
GET /payments/{payment_id}/
```

Quyền: `PET_OWNER`

### 9.4. Chủ thú cưng tạo URL thanh toán VNPAY

```http
POST /payments/{payment_id}/vnpay/create-url/
```

Quyền: `PET_OWNER`

Ghi chú:

- Chỉ chủ của payment mới được tạo URL thanh toán.
- Payment phải ở trạng thái `PENDING`.
- Nếu payment chưa có `method = VNPAY`, backend sẽ cập nhật sang `VNPAY`.
- URL thanh toán có thời hạn 15 phút theo tham số `vnp_ExpireDate`.
- Backend ký tham số bằng `VNPAY_HASH_SECRET` và dùng cấu hình `VNPAY_TMN_CODE`, `VNPAY_PAYMENT_URL`, `VNPAY_RETURN_URL`.

Response mẫu:

```json
{
  "success": true,
  "message": "Tạo URL thanh toán VNPAY thành công",
  "data": {
    "payment_url": "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html?vnp_Amount=11000000&vnp_Command=pay&vnp_TmnCode=DEMO&vnp_TxnRef=1&vnp_SecureHash=..."
  }
}
```

### 9.5. VNPAY IPN callback

```http
GET /payments/vnpay/ipn/?vnp_TxnRef=1&vnp_Amount=11000000&vnp_ResponseCode=00&vnp_SecureHash=...
```

Quyền: Public callback từ VNPAY

Ghi chú:

- Endpoint này không yêu cầu JWT vì do VNPAY gọi server-to-server.
- Backend kiểm tra chữ ký VNPAY, mã payment trong `vnp_TxnRef` và số tiền `vnp_Amount`.
- Nếu `vnp_ResponseCode = 00` và payment đang `PENDING`, payment chuyển sang `PAID`, ghi `paid_at`, `transaction_code`, và appointment chuyển sang `COMPLETED`.
- Nếu thanh toán thất bại, payment chuyển sang `FAILED`.
- Response dùng format IPN của VNPAY, không bọc trong `success_response`.

Response mẫu:

```json
{
  "RspCode": "00",
  "Message": "Confirm Success"
}
```

### 9.6. VNPAY return callback

```http
GET /payments/vnpay/return/?vnp_TxnRef=1&vnp_Amount=11000000&vnp_ResponseCode=00&vnp_SecureHash=...
```

Quyền: Public redirect từ VNPAY

Ghi chú:

- Endpoint này dùng khi trình duyệt người dùng được VNPAY chuyển về `VNPAY_RETURN_URL`.
- Backend kiểm tra chữ ký, payment và số tiền tương tự IPN.
- Nếu giao dịch thành công và payment còn `PENDING`, backend cập nhật payment sang `PAID` và appointment sang `COMPLETED`.
- Nếu payment đã được IPN xử lý trước đó, endpoint trả về trạng thái hiện tại của payment.

Response mẫu:

```json
{
  "success": true,
  "message": "Xác nhận kết quả thanh toán VNPAY thành công",
  "data": {
    "payment_id": 1,
    "appointment_id": 1,
    "payment_status": "PAID",
    "appointment_status": "COMPLETED",
    "is_success": true,
    "response_code": "00"
  }
}
```

---

## 10. Admin Staff APIs

### 10.1. Admin xem danh sách nhân viên

```http
GET /admin/staffs/?clinic_id=1&is_active=true
```

Quyền: `ADMIN`

Query params:

| Tên | Bắt buộc | Mô tả |
|---|---|---|
| `clinic_id` | Không | Lọc theo phòng khám |
| `is_active` | Không | `true`, `false`, `1`, `yes` |

### 10.2. Admin tạo nhân viên

```http
POST /admin/staffs/
```

Quyền: `ADMIN`

Request body:

```json
{
  "username": "staff01",
  "email": "staff01@example.com",
  "password": "StrongStaffPass123!",
  "full_name": "Clinic Staff 01",
  "phone": "0900000000",
  "address": "123 Street",
  "clinic_id": 1,
  "is_active": true
}
```

### 10.3. Admin xem chi tiết nhân viên

```http
GET /admin/staffs/{staff_id}/
```

Quyền: `ADMIN`

### 10.4. Admin cập nhật nhân viên

```http
PUT /admin/staffs/{staff_id}/
```

Quyền: `ADMIN`

Request body:

```json
{
  "email": "staff01-updated@example.com",
  "password": "AnotherStrongPass123!",
  "full_name": "Clinic Staff Updated",
  "phone": "0911111111",
  "address": "Updated address",
  "clinic_id": 1,
  "is_active": true
}
```

### 10.5. Admin khóa nhân viên

```http
DELETE /admin/staffs/{staff_id}/
```

Quyền: `ADMIN`

---

## 11. Admin Report APIs

### 11.1. Báo cáo tổng quan

```http
GET /admin/reports/overview/?date_from=2026-05-01&date_to=2026-05-31
```

Quyền: `ADMIN`

Query params:

| Tên | Bắt buộc | Mô tả |
|---|---|---|
| `date_from` | Không | Ngày bắt đầu, format `YYYY-MM-DD` |
| `date_to` | Không | Ngày kết thúc, format `YYYY-MM-DD` |

Response mẫu:

```json
{
  "success": true,
  "message": "Lấy báo cáo tổng quan thành công",
  "data": {
    "date_from": "2026-05-01",
    "date_to": "2026-05-31",
    "total_revenue": "2500000.00",
    "paid_payment_count": 12,
    "appointment_count": 20,
    "appointment_status": {
      "PENDING": 3,
      "CONFIRMED": 4,
      "CHECKED_IN": 1,
      "IN_PROGRESS": 0,
      "WAITING_PAYMENT": 0,
      "COMPLETED": 12,
      "CANCELLED": 0,
      "NO_SHOW": 0
    },
    "new_pet_owner_count": 5,
    "new_pet_count": 8,
    "clinic_count": 2,
    "service_count": 6
  }
}
```

### 11.2. Báo cáo doanh thu theo ngày/tháng

```http
GET /admin/reports/revenue/?date_from=2026-05-01&date_to=2026-05-31&group_by=day
```

Quyền: `ADMIN`

Query params:

| Tên | Bắt buộc | Mô tả |
|---|---|---|
| `date_from` | Không | Ngày bắt đầu, format `YYYY-MM-DD` |
| `date_to` | Không | Ngày kết thúc, format `YYYY-MM-DD` |
| `group_by` | Không | `day` hoặc `month`. Mặc định `day` |

Response mẫu:

```json
{
  "success": true,
  "message": "Lấy báo cáo doanh thu thành công",
  "data": {
    "date_from": "2026-05-01",
    "date_to": "2026-05-31",
    "group_by": "day",
    "total_revenue": "2500000.00",
    "series": [
      {
        "period": "2026-05-08",
        "revenue": "500000.00",
        "paid_payment_count": 2
      }
    ]
  }
}
```

### 11.3. Báo cáo theo phòng khám

```http
GET /admin/reports/clinics/?date_from=2026-05-01&date_to=2026-05-31
```

Quyền: `ADMIN`

Query params:

| Tên | Bắt buộc | Mô tả |
|---|---|---|
| `date_from` | Không | Ngày bắt đầu, format `YYYY-MM-DD` |
| `date_to` | Không | Ngày kết thúc, format `YYYY-MM-DD` |

Response mẫu:

```json
{
  "success": true,
  "message": "Lấy báo cáo phòng khám thành công",
  "data": {
    "date_from": "2026-05-01",
    "date_to": "2026-05-31",
    "clinics": [
      {
        "clinic_id": 1,
        "clinic_name": "PetCare Clinic Q1",
        "appointment_count": 10,
        "completed_appointment_count": 6,
        "paid_payment_count": 6,
        "revenue": "1200000.00"
      }
    ]
  }
}
```

---

## 12. Luồng test nhanh bằng Postman

### 12.1. Chuẩn bị token

1. Gọi `POST /auth/login/`.
2. Copy `data.access_token`.
3. Với request cần đăng nhập, thêm header:

```http
Authorization: Bearer <access_token>
```

### 12.2. Luồng pet-owner đặt lịch và thanh toán

1. Pet-owner đăng nhập.
2. Tạo pet: `POST /pets/`.
3. Xem phòng khám: `GET /clinics/`.
4. Xem dịch vụ phòng khám: `GET /clinics/{clinic_id}/services/`.
5. Đặt lịch: `POST /appointments/`.
6. Staff xác nhận/check-in/start/complete lịch. Khi complete, appointment chuyển sang `WAITING_PAYMENT` và payment `PENDING` được tạo tự động.
7. Pet-owner tạo URL thanh toán: `POST /payments/{payment_id}/vnpay/create-url/`.
8. Frontend redirect người dùng sang `data.payment_url` của VNPAY sandbox.
9. Sau khi VNPAY chuyển về `GET /payments/vnpay/return/` hoặc gọi `GET /payments/vnpay/ipn/`, payment `PAID` và appointment chuyển sang `COMPLETED` nếu giao dịch thành công.

### 12.3. Luồng staff khám và kê đơn

1. Staff đăng nhập.
2. Xem lịch phòng khám: `GET /appointments/clinic/`.
3. Xác nhận/check-in/start lịch.
4. Tạo bệnh án: `POST /appointments/{appointment_id}/medical-record/`.
5. Tạo đơn thuốc: `POST /medical-records/{medical_record_id}/prescription/`.
6. Thêm thuốc vào đơn: `POST /prescriptions/{prescription_id}/items/`.
7. Hoàn tất lịch: `POST /appointments/{appointment_id}/complete/`.

### 12.4. Luồng admin quản trị và xem báo cáo

1. Admin đăng nhập.
2. Tạo phòng khám: `POST /clinics/`.
3. Tạo dịch vụ: `POST /services/`.
4. Tạo staff: `POST /admin/staffs/`.
5. Xem báo cáo:
   - `GET /admin/reports/overview/`
   - `GET /admin/reports/revenue/?group_by=day`
   - `GET /admin/reports/clinics/`
