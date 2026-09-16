# Hệ thống quản lý thú cưng/phòng khám thú y - Requirements

----------

## 1. Actors

Hệ thống có 3 tác nhân chính:

-   **Chủ thú cưng (Pet Owner)**

-   **Phòng khám/Groomer (Clinic Staff / Business User)**

-   **Admin (System Admin)**

----------

## 2. Functional Requirements

### 2.1 Chủ thú cưng

-   Đăng ký, đăng nhập, đăng xuất và quản lý thông tin cá nhân

-   Xem hồ sơ cá nhân, cập nhật họ tên/số điện thoại/địa chỉ và đổi mật khẩu

-   Tạo, xem, cập nhật và xóa mềm hồ sơ thú cưng

-   Xem danh sách phòng khám và dịch vụ

-   Đặt lịch khám/grooming

-   Xem, cập nhật hoặc hủy lịch hẹn ở trạng thái cho phép

-   Xem lịch sử bệnh án của thú cưng

-   Xem đơn thuốc theo bệnh án

-   Tạo và xác nhận thanh toán dịch vụ

### 2.2 Phòng khám/Groomer

-   Xem danh sách lịch hẹn của phòng khám

-   Xem chi tiết lịch hẹn thuộc phòng khám

-   Xác nhận lịch hẹn

-   Check-in thú cưng khi khách đến

-   Chuyển lịch hẹn sang trạng thái đang khám/chăm sóc

-   Hoàn tất lịch hẹn hoặc đánh dấu khách không đến

-   Tạo, xem và cập nhật hồ sơ bệnh án

-   Quản lý thuốc của phòng khám

-   Kê đơn thuốc và quản lý chi tiết thuốc trong đơn

### 2.3 Admin

-   Quản lý phòng khám (CRUD mềm)

-   Quản lý tài khoản bác sĩ/nhân viên phòng khám

-   Quản lý danh mục dịch vụ

-   Xem báo cáo tổng quan hệ thống

-   Xem báo cáo doanh thu theo ngày/tháng

-   Xem báo cáo hiệu quả từng phòng khám

----------

## 3. Global Business Rules

-   Không xóa cứng dữ liệu đã phát sinh nghiệp vụ quan trọng như appointment, medical record, prescription, payment.

-   Các dữ liệu chính phải có thông tin audit cơ bản: `created_at`, `updated_at`.

-   Phân quyền dựa trên `role`: `PET_OWNER`, `CLINIC_STAFF`, `ADMIN`.

-   Staff chỉ được thao tác dữ liệu thuộc phòng khám của mình.

-   Chủ thú cưng chỉ được thao tác dữ liệu thuộc tài khoản của mình.

-   Các màn hình của chủ thú cưng trên frontend phải yêu cầu đăng nhập và đúng role `PET_OWNER`.

-   Dữ liệu thú cưng là trung tâm của hệ thống.

-   Dữ liệu đã phát sinh lịch sử nên được vô hiệu hóa bằng `is_active` thay vì xóa cứng.

-   Doanh thu báo cáo chỉ tính từ payment có trạng thái `PAID`.

----------

## 4. Use Case Diagram

<p align="center">
  <img src="UseCasePetCare.png" width="700">
</p>

----------

## 5. Use Case Specifications

----------

# UC01 - Quản lý hồ sơ thú cưng

| Thuộc tính | Mô tả |
|---|---|
| Use case ID | UC01 |
| Actor chính | Chủ thú cưng |
| Mô tả | Chủ thú cưng tạo và quản lý hồ sơ thú cưng của mình |

### Pre-conditions

-   Người dùng đã đăng nhập

-   Người dùng có role `PET_OWNER`

### Post-conditions

-   Hồ sơ thú cưng được tạo/cập nhật/xóa mềm

### Input

-   name

-   species

-   breed

-   gender

-   birth_date

-   weight

-   note

### Output

-   petId

-   Thông tin hồ sơ thú cưng

### Business Rules

-   Chủ thú cưng chỉ được xem và chỉnh sửa pet của mình.

-   `name` không được để trống.

-   `species` chỉ nhận `DOG`, `CAT`, `OTHER`.

-   `gender` chỉ nhận `MALE`, `FEMALE`.

-   `birth_date` không được lớn hơn ngày hiện tại.

-   `weight` phải lớn hơn 0 nếu có nhập.

-   Khi xóa pet, hệ thống dùng soft delete bằng `is_active = false`.

### Main Flow

1.  Chủ thú cưng mở màn hình quản lý thú cưng.

2.  Nhập thông tin hồ sơ thú cưng.

3.  Hệ thống validate dữ liệu.

4.  Hệ thống lưu hồ sơ thú cưng.

5.  Hệ thống trả về thông tin pet vừa tạo/cập nhật.

### Alternative Flow

A1 - Chủ thú cưng cập nhật pet đã có  
→ Hệ thống kiểm tra quyền sở hữu và cập nhật thông tin.

### Exception Flow

E1 - Pet không thuộc user hiện tại  
→ Hệ thống trả về lỗi không có quyền.

----------

# UC02 - Đặt lịch khám/Grooming

| Thuộc tính | Mô tả |
|---|---|
| Use case ID | UC02 |
| Actor chính | Chủ thú cưng |
| Actor phụ | Phòng khám/Groomer |
| Mô tả | Chủ thú cưng đặt lịch khám hoặc grooming tại phòng khám |

### Pre-conditions

-   Người dùng đã đăng nhập

-   Người dùng có role `PET_OWNER`

-   Có ít nhất một hồ sơ thú cưng đang hoạt động

-   Phòng khám đang hoạt động

-   Dịch vụ đang hoạt động và thuộc phòng khám đã chọn

### Post-conditions

-   Tạo lịch hẹn mới

-   Trạng thái mặc định: `PENDING`

### Input

-   pet_id

-   clinic_id

-   service_id

-   appointment_time

-   note

### Output

-   appointmentId

-   status

-   Thông tin lịch hẹn

### Business Rules

-   Không cho đặt lịch trong quá khứ.

-   Pet phải thuộc user hiện tại.

-   Clinic phải đang hoạt động.

-   Service phải đang hoạt động và thuộc clinic đã chọn.

-   Slot không được trùng với lịch hẹn đang hoạt động của cùng phòng khám.

-   Thời lượng slot được tính theo `service.duration_minutes`.

### Main Flow

1.  User chọn thú cưng.

2.  User chọn phòng khám.

3.  User chọn dịch vụ.

4.  User chọn thời gian hẹn và nhập ghi chú nếu có.

5.  Hệ thống kiểm tra quyền sở hữu pet.

6.  Hệ thống kiểm tra clinic/service hợp lệ.

7.  Hệ thống kiểm tra trùng lịch theo phòng khám.

8.  Hệ thống tạo bản ghi Appointment.

9.  Hệ thống trả về lịch hẹn với trạng thái `PENDING`.

### Alternative Flow

A1 - Slot bị trùng  
→ Hệ thống báo lỗi khung giờ đã bị trùng.

### Exception Flow

E1 - Dữ liệu không hợp lệ  
→ Hệ thống trả về lỗi validate.

----------

# UC03 - Quản lý lịch hẹn và check-in

| Thuộc tính | Mô tả |
|---|---|
| Use case ID | UC03 |
| Actor chính | Phòng khám/Groomer |
| Actor phụ | Chủ thú cưng |
| Mô tả | Staff xử lý lịch hẹn từ lúc xác nhận đến lúc hoàn tất |

### Pre-conditions

-   Staff đã đăng nhập

-   Staff có role `CLINIC_STAFF`

-   Staff đã được gán phòng khám

-   Lịch hẹn tồn tại và thuộc phòng khám của staff

### Post-conditions

-   Trạng thái lịch hẹn được cập nhật

### Business Rules

-   Staff chỉ thao tác lịch hẹn thuộc phòng khám của mình.

-   Chỉ lịch `PENDING` mới được xác nhận.

-   Chỉ lịch `CONFIRMED` mới được check-in.

-   Chỉ lịch `CHECKED_IN` mới được bắt đầu khám.

-   Chỉ lịch `IN_PROGRESS` mới được hoàn tất khám và chuyển sang chờ thanh toán.

-   Chỉ lịch `CONFIRMED` mới có thể đánh dấu `NO_SHOW`.

### Main Flow

1.  Staff xem danh sách lịch hẹn của phòng khám.

2.  Staff chọn một lịch hẹn.

3.  Staff xác nhận lịch hẹn: `PENDING` → `CONFIRMED`.

4.  Khi khách đến, staff check-in: `CONFIRMED` → `CHECKED_IN`.

5.  Staff bắt đầu khám/chăm sóc: `CHECKED_IN` → `IN_PROGRESS`.

6.  Staff hoàn tất khám: `IN_PROGRESS` → `WAITING_PAYMENT`, hệ thống tự tạo payment trạng thái `PENDING`.

### Alternative Flow

A1 - Khách không đến  
→ Staff đánh dấu `NO_SHOW` từ trạng thái `CONFIRMED`.

### Exception Flow

E1 - Staff thuộc phòng khám khác  
→ Hệ thống trả về lỗi không có quyền.

----------

# UC04 - Quản lý phòng khám

| Thuộc tính | Mô tả |
|---|---|
| Use case ID | UC04 |
| Actor chính | Admin |
| Mô tả | Admin tạo, xem, cập nhật và xóa mềm phòng khám |

### Pre-conditions

-   Admin đã đăng nhập

-   User có role `ADMIN`

### Post-conditions

-   Phòng khám được tạo/cập nhật/vô hiệu hóa

### Input

-   name

-   address

-   phone

-   email

-   is_active

### Output

-   clinicId

-   Thông tin phòng khám

### Business Rules

-   Chỉ admin được tạo/cập nhật/xóa mềm phòng khám.

-   `name` không được để trống.

-   `address` không được để trống.

-   Xóa phòng khám là soft delete bằng `is_active = false`.

### Main Flow

1.  Admin mở màn hình quản lý phòng khám.

2.  Admin nhập thông tin phòng khám.

3.  Hệ thống validate dữ liệu.

4.  Hệ thống lưu thông tin.

5.  Hệ thống trả về phòng khám đã tạo/cập nhật.

### Exception Flow

E1 - User không phải admin  
→ Hệ thống trả về lỗi không có quyền.

----------

# UC05 - Quản lý nhân viên phòng khám

| Thuộc tính | Mô tả |
|---|---|
| Use case ID | UC05 |
| Actor chính | Admin |
| Mô tả | Admin tạo và quản lý tài khoản staff của phòng khám |

### Pre-conditions

-   Admin đã đăng nhập

-   Phòng khám tồn tại

### Post-conditions

-   Tài khoản staff được tạo/cập nhật/khóa

### Input

-   username

-   email

-   password

-   full_name

-   phone

-   address

-   clinic_id

-   is_active

### Output

-   staffId

-   Thông tin staff

### Business Rules

-   Chỉ admin được quản lý staff.

-   Staff bắt buộc phải thuộc một phòng khám.

-   Username và email không được trùng.

-   Khi tạo staff, role được gán là `CLINIC_STAFF`.

-   Xóa staff là khóa tài khoản bằng `is_active = false`.

### Main Flow

1.  Admin mở màn hình quản lý nhân viên.

2.  Admin nhập thông tin staff và chọn phòng khám.

3.  Hệ thống kiểm tra phòng khám tồn tại.

4.  Hệ thống validate username, email, password.

5.  Hệ thống tạo tài khoản staff.

### Exception Flow

E1 - Clinic không tồn tại  
→ Hệ thống trả về lỗi không tìm thấy phòng khám.

----------

# UC06 - Quản lý dịch vụ

| Thuộc tính | Mô tả |
|---|---|
| Use case ID | UC06 |
| Actor chính | Admin |
| Mô tả | Admin quản lý danh mục dịch vụ của từng phòng khám |

### Pre-conditions

-   Admin đã đăng nhập

-   Phòng khám tồn tại

### Post-conditions

-   Dịch vụ được tạo/cập nhật/vô hiệu hóa

### Input

-   clinic_id

-   name

-   service_type

-   description

-   price

-   duration_minutes

-   is_active

### Output

-   serviceId

-   Thông tin dịch vụ

### Business Rules

-   Chỉ admin được tạo/cập nhật/xóa mềm dịch vụ.

-   Service phải thuộc một clinic.

-   `service_type` chỉ nhận `EXAM`, `GROOMING`, `VACCINE`, `OTHER`.

-   `price` phải lớn hơn 0.

-   `duration_minutes` phải lớn hơn 0.

-   Xóa dịch vụ là soft delete bằng `is_active = false`.

### Main Flow

1.  Admin chọn phòng khám.

2.  Admin nhập thông tin dịch vụ.

3.  Hệ thống validate dữ liệu.

4.  Hệ thống lưu dịch vụ.

### Exception Flow

E1 - Giá hoặc thời lượng không hợp lệ  
→ Hệ thống trả về lỗi validate.

----------

# UC07 - Tạo và quản lý bệnh án

| Thuộc tính | Mô tả |
|---|---|
| Use case ID | UC07 |
| Actor chính | Phòng khám/Groomer |
| Actor phụ | Chủ thú cưng |
| Mô tả | Staff tạo bệnh án sau khi khám/chăm sóc |

### Pre-conditions

-   Staff đã đăng nhập

-   Lịch hẹn tồn tại và thuộc phòng khám của staff

-   Lịch hẹn ở trạng thái phù hợp để tạo bệnh án

### Post-conditions

-   Bệnh án được tạo và gắn với lịch hẹn

### Input

-   symptoms

-   diagnosis

-   treatment

-   note

### Output

-   medicalRecordId

-   Thông tin bệnh án

### Business Rules

-   Một lịch hẹn chỉ có tối đa một bệnh án.

-   Staff chỉ được thao tác bệnh án thuộc phòng khám của mình.

-   `symptoms` không được để trống.

-   `diagnosis` không được để trống.

-   Chủ thú cưng chỉ được xem bệnh án của pet thuộc sở hữu của mình.

### Main Flow

1.  Staff mở chi tiết lịch hẹn.

2.  Staff nhập triệu chứng, chẩn đoán, hướng điều trị và ghi chú.

3.  Hệ thống kiểm tra quyền staff.

4.  Hệ thống tạo bệnh án gắn với appointment, pet, clinic và staff.

5.  Hệ thống trả về bệnh án vừa tạo.

### Alternative Flow

A1 - Staff cập nhật bệnh án  
→ Hệ thống kiểm tra quyền và cập nhật thông tin.

### Exception Flow

E1 - Lịch hẹn đã có bệnh án  
→ Hệ thống trả về lỗi thao tác không hợp lệ.

----------

# UC08 - Kê đơn và quản lý thuốc

| Thuộc tính | Mô tả |
|---|---|
| Use case ID | UC08 |
| Actor chính | Phòng khám/Groomer |
| Actor phụ | Chủ thú cưng |
| Mô tả | Staff quản lý thuốc, tạo đơn thuốc và thêm thuốc vào đơn |

### Pre-conditions

-   Staff đã đăng nhập

-   Staff đã được gán phòng khám

-   Bệnh án tồn tại

-   Thuốc thuộc phòng khám của staff

### Post-conditions

-   Đơn thuốc được tạo/cập nhật

-   Tồn kho thuốc được điều chỉnh

### Input

-   medical_record_id

-   note

-   medicine_id

-   quantity

-   dosage

-   frequency

-   duration_days

-   instruction

### Output

-   prescriptionId

-   prescriptionItemId

### Business Rules

-   Staff chỉ được thao tác thuốc và đơn thuốc thuộc phòng khám của mình.

-   Một bệnh án chỉ có tối đa một đơn thuốc.

-   Một thuốc chỉ xuất hiện một lần trong cùng đơn thuốc.

-   `quantity` phải lớn hơn 0.

-   `duration_days` phải lớn hơn 0.

-   Khi thêm thuốc vào đơn, tồn kho phải đủ.

-   Khi thêm/cập nhật/xóa thuốc trong đơn, tồn kho được cập nhật tương ứng.

-   Chủ thú cưng chỉ được xem đơn thuốc thuộc bệnh án của pet mình sở hữu.

### Main Flow

1.  Staff tạo hoặc mở đơn thuốc từ bệnh án.

2.  Staff chọn thuốc trong kho của phòng khám.

3.  Staff nhập số lượng, liều dùng, tần suất, số ngày dùng và hướng dẫn.

4.  Hệ thống kiểm tra thuốc hợp lệ và tồn kho đủ.

5.  Hệ thống trừ tồn kho và lưu chi tiết đơn thuốc.

6.  Hệ thống trả về đơn thuốc kèm danh sách thuốc.

### Alternative Flow

A1 - Staff cập nhật số lượng thuốc trong đơn  
→ Hệ thống điều chỉnh tồn kho theo phần chênh lệch.

### Exception Flow

E1 - Tồn kho không đủ  
→ Hệ thống trả về lỗi số lượng thuốc tồn kho không đủ.

----------

# UC09 - Thanh toán dịch vụ

| Thuộc tính | Mô tả |
|---|---|
| Use case ID | UC09 |
| Actor chính | Chủ thú cưng |
| Actor phụ | Phòng khám/Groomer |
| Mô tả | Chủ thú cưng thanh toán cho lịch hẹn đã khám xong và đang chờ thanh toán |

### Pre-conditions

-   Chủ thú cưng đã đăng nhập

-   Lịch hẹn thuộc về chủ thú cưng

-   Lịch hẹn có trạng thái `WAITING_PAYMENT`

-   Lịch hẹn đã có payment `PENDING` do hệ thống tạo sau khi staff hoàn tất khám

### Post-conditions

-   Nếu xác nhận thanh toán mock online thành công, trạng thái chuyển sang `PAID`

-   Lịch hẹn chuyển sang `COMPLETED`

### Input

-   paymentId

### Output

-   paymentId

-   amount

-   status

-   transaction_code

### Business Rules

-   Pet-owner chỉ được thanh toán lịch hẹn/payment của mình.

-   Chỉ lịch hẹn `WAITING_PAYMENT` mới được thanh toán.

-   Mỗi lịch hẹn chỉ có một payment.

-   Frontend không gửi `amount`; backend tự tính tổng tiền.

-   Công thức hiện tại: `service.price + tổng(quantity * medicine.price)` trong đơn thuốc nếu có.

-   Payment method hiện hỗ trợ `MOCK_ONLINE` và `CASH` trong model.

-   Xác nhận thanh toán hiện áp dụng cho `MOCK_ONLINE`.

### Main Flow

1.  Chủ thú cưng mở lịch hẹn đang `WAITING_PAYMENT`.

2.  Frontend lấy `payment.id` từ response appointment.

3.  Chủ thú cưng xác nhận thanh toán mock online.

4.  Hệ thống kiểm tra payment thuộc user hiện tại và đang `PENDING`.

5.  Hệ thống cập nhật payment sang `PAID`, ghi `paid_at` và `transaction_code`.

6.  Hệ thống cập nhật appointment sang `COMPLETED`.

### Alternative Flow

A1 - Payment đã tồn tại  
→ Hệ thống báo lịch hẹn này đã có thanh toán.

### Exception Flow

E1 - Lịch hẹn chưa hoàn tất  
→ Hệ thống trả về lỗi chỉ có thể thanh toán lịch hẹn đang chờ thanh toán.

----------

# UC10 - Admin xem báo cáo hệ thống

| Thuộc tính | Mô tả |
|---|---|
| Use case ID | UC10 |
| Actor chính | Admin |
| Mô tả | Admin xem báo cáo tổng quan, doanh thu và hiệu quả phòng khám |

### Pre-conditions

-   Admin đã đăng nhập

-   User có role `ADMIN`

### Post-conditions

-   Admin nhận dữ liệu báo cáo hệ thống

### Input

-   date_from

-   date_to

-   group_by

### Output

-   total_revenue

-   paid_payment_count

-   appointment_status

-   revenue series

-   clinic report

### Business Rules

-   Chỉ admin được xem báo cáo hệ thống.

-   Doanh thu chỉ tính payment có trạng thái `PAID`.

-   `date_from` phải nhỏ hơn hoặc bằng `date_to`.

-   Báo cáo doanh thu hỗ trợ group theo `day` hoặc `month`.

-   Báo cáo không tạo bảng riêng, dữ liệu được aggregate từ bảng nghiệp vụ.

### Main Flow

1.  Admin mở màn hình báo cáo.

2.  Admin chọn khoảng ngày nếu cần.

3.  Admin chọn loại báo cáo: tổng quan, doanh thu hoặc phòng khám.

4.  Hệ thống kiểm tra quyền admin.

5.  Hệ thống aggregate dữ liệu từ appointment, payment, clinic, service, user và pet.

6.  Hệ thống trả về dữ liệu báo cáo.

### Alternative Flow

A1 - Admin không chọn khoảng ngày  
→ Hệ thống trả về báo cáo toàn bộ dữ liệu.

### Exception Flow

E1 - `date_from` lớn hơn `date_to`  
→ Hệ thống trả về lỗi validate.

----------

## 6. Đặc tả luồng nghiệp vụ - Pet Care

----------

## 6.1 Luồng đặt lịch khám/grooming

**Mục tiêu:** Cho phép chủ thú cưng đặt lịch khám/grooming tại phòng khám phù hợp.

### Bước 1 - Frontend

Người dùng nhập/chọn:

-   Thú cưng

-   Phòng khám

-   Dịch vụ

-   Ngày và giờ hẹn

-   Ghi chú

### Bước 2 - API

Frontend gọi API:

```http
POST /api/appointments/
```

Payload:

```json
{
  "pet_id": 1,
  "clinic_id": 1,
  "service_id": 1,
  "appointment_time": "2026-05-20T09:00:00+07:00",
  "note": "Khám sức khỏe định kỳ"
}
```

### Bước 3 - Backend

-   Kiểm tra pet thuộc user hiện tại.

-   Kiểm tra phòng khám đang hoạt động.

-   Kiểm tra dịch vụ hợp lệ tại phòng khám.

-   Kiểm tra appointment time lớn hơn hiện tại.

-   Kiểm tra slot không trùng lịch đang hoạt động của phòng khám.

-   Tạo Appointment với trạng thái `PENDING`.

### Bước 4 - Kết quả

-   Trả về thông tin lịch hẹn.

-   Staff phòng khám có thể xác nhận lịch hẹn.

----------

## 6.2 Luồng xử lý lịch hẹn tại phòng khám

**Mục tiêu:** Staff xử lý lịch hẹn từ lúc xác nhận đến lúc hoàn tất.

### Bước 1 - API xác nhận lịch

```http
POST /api/appointments/{appointment_id}/confirm/
```

Điều kiện:

-   Staff thuộc cùng phòng khám với appointment.

-   Appointment đang ở trạng thái `PENDING`.

Kết quả:

-   Appointment chuyển sang `CONFIRMED`.

### Bước 2 - API check-in

```http
POST /api/appointments/{appointment_id}/check-in/
```

Điều kiện:

-   Appointment đang ở trạng thái `CONFIRMED`.

Kết quả:

-   Appointment chuyển sang `CHECKED_IN`.

### Bước 3 - API bắt đầu khám

```http
POST /api/appointments/{appointment_id}/start/
```

Điều kiện:

-   Appointment đang ở trạng thái `CHECKED_IN`.

Kết quả:

-   Appointment chuyển sang `IN_PROGRESS`.

### Bước 4 - API hoàn tất

```http
POST /api/appointments/{appointment_id}/complete/
```

Điều kiện:

-   Appointment đang ở trạng thái `IN_PROGRESS`.

Kết quả:

-   Appointment chuyển sang `WAITING_PAYMENT`.

-   Hệ thống tự tạo payment trạng thái `PENDING`.

----------

## 6.3 Luồng tạo bệnh án

**Mục tiêu:** Lưu thông tin khám, chẩn đoán và điều trị cho thú cưng.

### Bước 1 - Frontend

Staff nhập:

-   Triệu chứng

-   Chẩn đoán

-   Hướng điều trị

-   Ghi chú

### Bước 2 - API

```http
POST /api/appointments/{appointment_id}/medical-record/
```

Payload:

```json
{
  "symptoms": "Ho nhẹ, bỏ ăn",
  "diagnosis": "Viêm đường hô hấp nhẹ",
  "treatment": "Theo dõi và dùng thuốc",
  "note": "Tái khám sau 7 ngày nếu không giảm"
}
```

### Bước 3 - Backend

-   Kiểm tra staff thuộc phòng khám của appointment.

-   Kiểm tra appointment hợp lệ.

-   Kiểm tra appointment chưa có medical record.

-   Gắn record với appointment, pet, clinic và staff.

### Bước 4 - Kết quả

-   Trả về medical record.

-   Cho phép tiếp tục kê đơn thuốc.

----------

## 6.4 Luồng kê đơn thuốc

**Mục tiêu:** Tạo đơn thuốc và quản lý thuốc trong đơn.

### Bước 1 - Tạo đơn thuốc

```http
POST /api/medical-records/{medical_record_id}/prescription/
```

Payload:

```json
{
  "note": "Uống thuốc sau ăn"
}
```

### Bước 2 - Thêm thuốc vào đơn

```http
POST /api/prescriptions/{prescription_id}/items/
```

Payload:

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

### Bước 3 - Backend

-   Kiểm tra prescription thuộc phòng khám của staff.

-   Kiểm tra medicine thuộc phòng khám của staff và đang hoạt động.

-   Kiểm tra thuốc chưa tồn tại trong đơn.

-   Kiểm tra tồn kho đủ.

-   Trừ tồn kho và lưu prescription item.

### Bước 4 - Kết quả

-   Trả về chi tiết thuốc trong đơn.

-   Chủ thú cưng có thể xem đơn thuốc theo bệnh án của pet mình.

----------

## 6.5 Luồng thanh toán

**Mục tiêu:** Chủ thú cưng thanh toán dịch vụ khám/grooming và thuốc nếu có.

### Bước 1 - Frontend

Người dùng:

-   Chọn lịch hẹn đang `WAITING_PAYMENT`.

-   Lấy `payment.id` từ response appointment.

### Bước 2 - Xác nhận thanh toán mock online

```http
POST /api/payments/{payment_id}/confirm/
```

### Bước 3 - Kết quả

-   Payment chuyển sang `PAID`.

-   Hệ thống ghi `paid_at`.

-   Hệ thống sinh `transaction_code`.

-   Appointment chuyển sang `COMPLETED`.

----------

## 6.6 Luồng admin xem báo cáo

**Mục tiêu:** Admin theo dõi tình hình vận hành và doanh thu hệ thống.

### Bước 1 - Báo cáo tổng quan

```http
GET /api/admin/reports/overview/?date_from=2026-05-01&date_to=2026-05-31
```

Dữ liệu trả về:

-   Tổng doanh thu

-   Số payment đã thanh toán

-   Số lịch hẹn theo trạng thái

-   Số chủ thú cưng mới

-   Số thú cưng mới

-   Tổng số phòng khám và dịch vụ

### Bước 2 - Báo cáo doanh thu theo ngày/tháng

```http
GET /api/admin/reports/revenue/?group_by=day
```

Hoặc:

```http
GET /api/admin/reports/revenue/?group_by=month
```

Dữ liệu trả về:

-   Doanh thu theo từng ngày/tháng

-   Số payment đã thanh toán theo từng ngày/tháng

-   Tổng doanh thu trong khoảng lọc

### Bước 3 - Báo cáo theo phòng khám

```http
GET /api/admin/reports/clinics/
```

Dữ liệu trả về:

-   Số lịch hẹn theo phòng khám

-   Số lịch hẹn đã hoàn tất

-   Số payment đã thanh toán

-   Doanh thu theo phòng khám

### Bước 4 - Backend

-   Kiểm tra user có role `ADMIN`.

-   Validate `date_from`, `date_to`, `group_by`.

-   Aggregate dữ liệu từ `payments`, `appointments`, `clinics`, `services`, `users`, `pets`.

-   Trả về dữ liệu báo cáo.

----------

## 7. Non-functional Requirements

### 7.1 Security

-   API sử dụng JWT access token cho các chức năng cần đăng nhập.

-   Các API nghiệp vụ phải kiểm tra role.

-   Staff phải bị giới hạn theo `clinic_id`.

-   Pet-owner phải bị giới hạn theo dữ liệu sở hữu.

-   Password được lưu dưới dạng hash thông qua Django authentication.

-   Khi đổi mật khẩu, hệ thống phải kiểm tra mật khẩu hiện tại, validate mật khẩu mới và chỉ lưu mật khẩu dưới dạng hash.

### 7.2 Data Integrity

-   Dữ liệu quan trọng không bị xóa cứng qua API.

-   Appointment, medical record, prescription và payment phải giữ được lịch sử nghiệp vụ.

-   Payment amount được tính ở backend để tránh chỉnh sửa từ frontend.

-   Prescription item có unique constraint theo prescription và medicine.

### 7.3 Maintainability

-   Backend chia theo các lớp: controller, serializer, service, repository, model.

-   Business logic chính nằm trong service.

-   Serializer chịu trách nhiệm validate input.

-   Repository chịu trách nhiệm truy vấn dữ liệu.

### 7.4 Testability

-   Các module chính có unit test và integration test.

-   Test bao phủ controller, service, serializer và API integration.

-   Các nghiệp vụ payment và report có test riêng.

----------

## 8. Out of Scope / Future Improvements

Các chức năng sau có thể mở rộng sau giai đoạn hiện tại:

-   Tích hợp cổng thanh toán thật như VNPay hoặc MoMo.

-   Notification nhắc lịch khám/tiêm/grooming.

-   Quản lý giờ làm việc chi tiết của từng phòng khám.

-   Gợi ý slot thay thế khi lịch bị trùng.

-   Audit log chi tiết ai sửa gì, khi nào.

-   Dashboard trực tiếp trong Django Admin UI.

-   Báo cáo top dịch vụ, top thuốc, tỷ lệ hủy/no-show nâng cao.
