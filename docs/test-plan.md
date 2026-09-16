# Test Plan - Backend 2DEL Pet Care

## 1. Thông tin tài liệu

| Mục | Nội dung |
|---|---|
| Dự án | Hệ thống quản lý thú cưng/phòng khám thú y 2DEL |
| Phạm vi tài liệu | Backend testing: unit test, integration test và manual API test |
| Không thuộc phạm vi | Frontend UI, frontend build, frontend lint, kiểm thử giao diện React |
| Tài liệu liên quan | `docs/requirements.md`, `docs/api-docs.md`, `docs/manual-test-cases-2del.xlsx`, `docs/test-report.md` |
| Công cụ chính | `pytest`, `pytest-django`, Django REST Framework test client, Postman/manual API client |

## 2. Mục tiêu kiểm thử

Mục tiêu của kế hoạch kiểm thử là xác nhận backend đáp ứng đúng các yêu cầu nghiệp vụ trong `docs/requirements.md`, đặc biệt là các luồng có rủi ro cao về dữ liệu, phân quyền và thanh toán.

Các mục tiêu cụ thể:

- Xác minh API trả đúng format response chuẩn: `success`, `message`, `data` hoặc `errors`.
- Xác minh validate input ở tầng serializer hoạt động đúng với dữ liệu hợp lệ và không hợp lệ.
- Xác minh business rule ở tầng service, bao gồm phân quyền theo role, owner chỉ thao tác dữ liệu của mình, staff chỉ thao tác dữ liệu thuộc clinic được gán.
- Xác minh các luồng nghiệp vụ chính qua integration test: auth, pet, clinic/service, appointment, medical record, prescription, medicine, payment và report.
- Xác minh manual API test bao phủ các kịch bản nghiệp vụ end-to-end quan trọng mà unit/integration test không thể hiện đầy đủ ở góc nhìn người kiểm thử.
- Xác minh các lỗi nghiêm trọng về phân quyền, trạng thái lịch hẹn, tồn kho thuốc, thanh toán và báo cáo được phát hiện trước khi bàn giao.

## 3. Phạm vi kiểm thử

### 3.1. In scope

| Nhóm | Nội dung kiểm thử |
|---|---|
| Authentication & User | Đăng ký, đăng nhập, refresh token, logout, profile, đổi mật khẩu, quản lý staff |
| Authorization | Phân quyền `PET_OWNER`, `CLINIC_STAFF`, `ADMIN`; chặn truy cập sai role |
| Pet | Tạo, xem, cập nhật, xóa mềm hồ sơ thú cưng; kiểm tra quyền sở hữu |
| Clinic & Service | Quản lý phòng khám, dịch vụ, soft delete, validate clinic/service active |
| Appointment | Đặt lịch, cập nhật, hủy, staff confirm/check-in/start/complete/no-show, kiểm tra slot trùng |
| Medical Record | Tạo, xem, cập nhật bệnh án; kiểm tra appointment status hợp lệ và clinic ownership |
| Prescription | Tạo đơn thuốc, thêm/sửa/xóa thuốc trong đơn, kiểm tra trùng thuốc và tồn kho |
| Medicine | Quản lý thuốc trong phạm vi clinic của staff, validate tên trùng và số lượng/giá |
| Payment | Tạo payment, tính amount, tạo URL VNPAY, xử lý VNPAY return/IPN thành công/thất bại |
| Report | Báo cáo tổng quan, doanh thu theo ngày/tháng, báo cáo clinic; chỉ tính payment `PAID` |
| Common layer | Response helper, exception handler, custom exception, permission class, base model |

### 3.2. Out of scope

- Kiểm thử UI React, layout, responsive, toast, loading state và route trên trình duyệt.
- Kiểm thử build/lint frontend.
- Kiểm thử hiệu năng tải lớn, stress test hoặc security penetration test chuyên sâu.
- Kiểm thử tích hợp với cổng VNPAY production.
- Kiểm thử gửi email/SMS hoặc các bên thứ ba chưa có trong source code.

## 4. Chiến lược kiểm thử

Backend được kiểm thử theo ba lớp:

| Lớp kiểm thử | Mục đích | Công cụ | Vị trí |
|---|---|---|---|
| Unit test | Kiểm tra từng service, serializer, controller/helper độc lập | `pytest`, `pytest-mock`, DRF serializer | `backend/src/tests/unit` |
| Integration test | Kiểm tra API endpoint, database test, authentication, permission và luồng nghiệp vụ | `pytest-django`, DRF `APIClient` | `backend/src/tests/integration` |
| Manual API test | Kiểm tra thủ công các luồng nghiệp vụ theo vai trò và dữ liệu thực tế | Postman hoặc API client tương đương | `docs/manual-test-cases-2del.xlsx` |

Nguyên tắc kiểm thử:

- Unit test tập trung vào logic nhỏ, dễ cô lập và dễ xác định nguyên nhân lỗi.
- Integration test xác minh request/response, database state và permission theo đúng URL/API.
- Manual API test dùng để rà soát luồng nghiệp vụ hoàn chỉnh, đặc biệt với role, trạng thái appointment và thanh toán VNPAY sandbox.
- Không đưa frontend vào tiêu chí pass/fail của test plan này.

## 5. Môi trường kiểm thử

| Thành phần | Cấu hình |
|---|---|
| OS | Windows |
| Backend runtime | Python 3.13+ |
| Framework | Django 6.0.3, Django REST Framework 3.17.1 |
| Auth | `djangorestframework-simplejwt` |
| Test framework | `pytest`, `pytest-django`, `pytest-cov`, `pytest-mock`, `factory_boy`, `Faker`, `freezegun` |
| Database test | Theo `config.test_settings` qua `pytest.ini` |
| Payment sandbox | VNPAY sandbox config qua environment settings |
| API base URL khi manual | `http://127.0.0.1:8000/api` |

File cấu hình test:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.test_settings
testpaths = src/tests
python_files = tests.py test_*.py *_tests.py
addopts = -ra --strict-markers --strict-config
```

## 6. Dữ liệu kiểm thử

### 6.1. Nhóm người dùng

| Role | Mục đích sử dụng |
|---|---|
| `PET_OWNER` | Đăng ký, đăng nhập, quản lý pet, đặt lịch, xem bệnh án, thanh toán |
| `CLINIC_STAFF` | Xem lịch thuộc clinic, xử lý appointment, tạo bệnh án, kê đơn, quản lý thuốc |
| `ADMIN` | Quản lý clinic, service, staff và xem báo cáo |

### 6.2. Dữ liệu nghiệp vụ chính

| Entity | Dữ liệu cần có |
|---|---|
| Clinic | Clinic active và inactive để kiểm tra filter/soft delete |
| Service | Dịch vụ thuộc clinic, có `price`, `duration_minutes`, `service_type` hợp lệ |
| Pet | Pet active thuộc owner A và pet thuộc owner B để kiểm tra phân quyền |
| Appointment | Các trạng thái `PENDING`, `CONFIRMED`, `CHECKED_IN`, `IN_PROGRESS`, `WAITING_PAYMENT`, `COMPLETED`, `CANCELLED`, `NO_SHOW` |
| Medical Record | Bệnh án gắn với appointment đủ điều kiện |
| Medicine | Thuốc active/inactive, tồn kho đủ và không đủ |
| Prescription | Đơn thuốc có item, item trùng medicine, item vượt tồn kho |
| Payment | Payment `PENDING`, `PAID`, `FAILED`, `CANCELLED`, có và không có `paid_at` |

### 6.3. Quy tắc dữ liệu ngày giờ

- Appointment time hợp lệ phải lớn hơn thời điểm hiện tại.
- Test case dùng ngày cố định trong quá khứ phải kỳ vọng backend reject.
- Báo cáo theo ngày dùng `date_from <= date_to`; trường hợp ngược lại phải bị validate lỗi.

## 7. Ma trận kiểm thử theo module

| Module | Unit test cần có | Integration test cần có | Manual API test cần có |
|---|---|---|---|
| Auth/User | Serializer register/login/change password; service register/login/profile; controller response | Register, login, profile, change password, protected endpoint without token | Đăng ký, đăng nhập, đổi mật khẩu, login bằng mật khẩu cũ/mới |
| Permission | Permission class theo role, exception handler | Owner/staff/admin truy cập đúng và sai quyền | Dùng token sai role gọi API owner/staff/admin |
| Pet | Validate name/species/gender/birth_date/weight; service owner check | CRUD pet, soft delete, owner không xem pet người khác | Owner tạo/sửa/xóa pet, owner khác bị chặn |
| Clinic/Service | Validate clinic/service; soft delete; service active rule | Admin CRUD clinic/service, public/staff list service nếu có | Admin tạo clinic/service, xóa mềm, tạo service với price/duration invalid |
| Appointment | Time conflict, status transition, owner/staff permission | Create/list/detail/update/cancel; staff confirm/check-in/start/complete/no-show | Owner đặt lịch, trùng slot, hủy; staff xử lý luồng trạng thái |
| Medical Record | Appointment status allowed, duplicate record, clinic permission | Create/get/update record; owner xem lịch sử pet | Staff tạo bệnh án, tạo sai trạng thái, tạo trùng |
| Medicine | Validate name/unit/stock/price; duplicate active medicine; clinic permission | Staff CRUD medicine theo clinic | Staff tạo thuốc, tạo trùng tên, cập nhật tồn kho |
| Prescription | Duplicate prescription/item, stock deduction/restore, clinic permission | Create prescription, add/update/delete item | Tạo đơn, thêm thuốc, vượt tồn kho, thêm trùng thuốc |
| Payment | Amount calculation, owner permission, VNPAY signature, return/IPN handling | Create payment, create payment URL, VNPAY return/IPN success/fail | Tạo URL VNPAY, callback thành công/thất bại, kiểm tra appointment status |
| Report | Date range validation, revenue filter, grouping day/month | Overview, revenue, clinic report | Admin xem báo cáo, date range invalid, chỉ tính payment PAID |
| Common | Response format, custom exceptions, base model timestamp | Error response qua API khi validate/business/permission fail | Đối chiếu response lỗi/thành công theo format chuẩn |

## 8. Kịch bản kiểm thử trọng yếu

### 8.1. Authentication và account

| Mã | Kịch bản | Expected result |
|---|---|---|
| AUTH-01 | Register PET_OWNER với dữ liệu hợp lệ | API trả `201`, `success=true`, user có role `PET_OWNER`, không trả password |
| AUTH-02 | Register username/email đã tồn tại | API trả lỗi `400`, không tạo user mới |
| AUTH-03 | Login đúng username/password | API trả access token, refresh token và thông tin user |
| AUTH-04 | Login sai password hoặc user inactive | API trả `401`, không sinh token |
| AUTH-05 | Đổi mật khẩu đúng old password | API trả thành công, password cũ không login được, password mới login được |
| AUTH-06 | Gọi API protected không có token | API trả `401` |

### 8.2. Phân quyền và ownership

| Mã | Kịch bản | Expected result |
|---|---|---|
| SEC-01 | Owner A xem pet/appointment của Owner B | API trả lỗi quyền hoặc business error, không lộ dữ liệu |
| SEC-02 | Staff clinic B thao tác appointment clinic A | API trả `403` |
| SEC-03 | PET_OWNER hoặc CLINIC_STAFF gọi API admin | API trả `403` |
| SEC-04 | Staff chưa gán clinic gọi API clinic-scoped | API trả lỗi business phù hợp |

### 8.3. Appointment workflow

| Mã | Kịch bản | Expected result |
|---|---|---|
| APP-01 | Owner tạo lịch với pet/clinic/service hợp lệ và thời gian tương lai | Appointment được tạo với status `PENDING` |
| APP-02 | Owner tạo lịch trong quá khứ | API trả `400` do `appointment_time` không hợp lệ |
| APP-03 | Owner tạo lịch trùng slot clinic | API trả `400`, không tạo appointment mới |
| APP-04 | Owner cập nhật lịch `PENDING` | Cập nhật thành công nếu thời gian mới hợp lệ và không trùng slot |
| APP-05 | Owner hủy lịch `PENDING` | Status chuyển `CANCELLED` |
| APP-06 | Staff confirm/check-in/start/complete | Status chuyển `PENDING -> CONFIRMED -> CHECKED_IN -> IN_PROGRESS -> WAITING_PAYMENT`, tạo payment `PENDING` |
| APP-07 | Staff no-show lịch `CONFIRMED` | Status chuyển `NO_SHOW` |

### 8.4. Medical record, prescription và medicine

| Mã | Kịch bản | Expected result |
|---|---|---|
| MR-01 | Staff tạo bệnh án cho appointment đủ điều kiện | Record gắn đúng appointment, pet, clinic và staff |
| MR-02 | Staff tạo bệnh án cho appointment `PENDING` | API trả `400` |
| MR-03 | Tạo bệnh án trùng appointment | API trả lỗi, chỉ có một bệnh án cho một appointment |
| MED-01 | Staff tạo thuốc mới trong clinic | Medicine active được tạo đúng stock và price |
| MED-02 | Staff tạo thuốc trùng tên active | API trả lỗi trùng thuốc |
| PRES-01 | Tạo prescription cho medical record chưa có đơn | Prescription được tạo đúng clinic/staff |
| PRES-02 | Thêm medicine vào prescription với quantity hợp lệ | Item được tạo, tồn kho giảm đúng |
| PRES-03 | Thêm quantity vượt tồn kho | API trả lỗi tồn kho không đủ |
| PRES-04 | Thêm trùng medicine trong cùng prescription | API trả lỗi trùng item |

### 8.5. Payment và report

| Mã | Kịch bản | Expected result |
|---|---|---|
| PAY-01 | Tạo payment cho appointment `WAITING_PAYMENT` | Payment `PENDING` được tạo với amount do backend tính |
| PAY-02 | Tạo payment cho appointment không thuộc owner | API trả `403` |
| PAY-03 | Tạo VNPAY URL cho payment `PENDING` | API trả payment URL có signed query |
| PAY-04 | VNPAY return/IPN success code `00` | Payment chuyển `PAID`, appointment chuyển `COMPLETED`, lưu transaction code |
| PAY-05 | VNPAY return/IPN fail code khác `00` | Payment không được tính là paid; appointment không chuyển `COMPLETED` |
| REP-01 | Admin xem overview report | Trả tổng doanh thu, số payment paid, trạng thái appointment và số liệu tổng quan |
| REP-02 | Admin xem revenue report group by day/month | Chỉ cộng payment `PAID` có `paid_at` |
| REP-03 | `date_from > date_to` | API trả `400` validate date range |

## 9. Manual API testing

Manual test không kiểm tra giao diện. Người kiểm thử gọi API trực tiếp bằng Postman hoặc API client tương đương theo `docs/api-docs.md` và ghi kết quả vào `docs/manual-test-cases-2del.xlsx`.

Quy trình manual đề xuất:

1. Chuẩn bị database test/demo sạch hoặc dataset đã biết trước.
2. Tạo token cho ba role: `PET_OWNER`, `CLINIC_STAFF`, `ADMIN`.
3. Chạy nhóm test theo thứ tự phụ thuộc dữ liệu: Auth -> Admin setup -> Pet -> Appointment -> Staff workflow -> Medical record -> Prescription/Medicine -> Payment -> Report.
4. Với mỗi case, ghi `Actual Result`, `Status`, module và ghi chú nếu kết quả khác expected.
5. Với các case lỗi, xác nhận cả HTTP status code và body response.

Checklist bắt buộc khi manual:

- Token đúng role được dùng cho đúng API.
- Dữ liệu owner/staff/clinic khác nhau để kiểm tra phân quyền.
- Appointment time phải là thời gian tương lai, trừ case kiểm thử lỗi quá khứ.
- Payment amount phải được đối chiếu với service price và prescription items.
- Report chỉ được đối chiếu với payment `PAID`, không tính `PENDING`, `FAILED`, `CANCELLED`.

## 10. Lệnh chạy kiểm thử

Chạy toàn bộ backend test:

```bash
cd backend
venv\Scripts\activate
pytest
```

Chạy unit test:

```bash
cd backend
venv\Scripts\activate
pytest src/tests/unit
```

Chạy integration test:

```bash
cd backend
venv\Scripts\activate
pytest src/tests/integration
```

Chạy test theo module:

```bash
cd backend
venv\Scripts\activate
pytest src/tests/integration/test_appointment_api.py
pytest src/tests/unit/services/test_payment_service.py
```

Chạy coverage backend:

```bash
cd backend
venv\Scripts\activate
pytest --cov=src --cov-report=term-missing
```

## 11. Tiêu chí pass/fail

### 11.1. Entry criteria

- Source code backend đã ổn định tại nhánh kiểm thử.
- Migration chạy được trên database test.
- Environment variables cho JWT/database/VNPAY sandbox đã được cấu hình khi chạy manual payment.
- API documentation và test case manual đã được cập nhật theo endpoint hiện tại.

### 11.2. Exit criteria

| Tiêu chí | Yêu cầu |
|---|---|
| Unit test | 100% test unit pass |
| Integration test | 100% test integration pass |
| Critical/High defect | Không còn lỗi mở liên quan đến authentication, authorization, mất dữ liệu, sai payment hoặc sai report |
| Manual API test | Các luồng trọng yếu đạt hoặc có giải thích rõ nếu khác expected do dữ liệu/ngày giờ |
| Coverage | Đạt ngưỡng tối thiểu của môn học/nhóm; khuyến nghị >= 80% cho backend |
| Regression | Chạy lại test liên quan sau khi sửa logic appointment, payment, permission hoặc report |

### 11.3. Fail criteria

Một build/test run bị xem là fail nếu có ít nhất một điều kiện sau:

- Có unit hoặc integration test fail.
- API protected cho phép truy cập sai role hoặc sai owner/clinic.
- Appointment chuyển sai thứ tự trạng thái nghiệp vụ.
- Payment success không đồng bộ với appointment `COMPLETED`, hoặc payment fail vẫn bị tính doanh thu.
- Report cộng doanh thu từ payment không phải `PAID`.
- Manual API test phát hiện lỗi critical/high chưa được xử lý.

## 12. Quản lý defect

Mỗi defect cần ghi tối thiểu:

| Trường | Mô tả |
|---|---|
| Defect ID | Mã lỗi duy nhất, ví dụ `DEF-AUTH-001` |
| Module | Auth, Pet, Appointment, Payment, Report... |
| Severity | Critical, High, Medium, Low |
| Steps to reproduce | Các bước gọi API hoặc chạy test |
| Expected result | Kết quả đúng theo requirement/source rule |
| Actual result | Kết quả thực tế |
| Evidence | Response body, log, test output hoặc ảnh nếu có |
| Status | Open, In Progress, Fixed, Retest, Closed |

Mức độ lỗi:

| Severity | Định nghĩa |
|---|---|
| Critical | Lỗi bảo mật/phân quyền nghiêm trọng, mất dữ liệu, payment/report sai nghiêm trọng |
| High | Lỗi làm hỏng luồng nghiệp vụ chính nhưng có thể cô lập |
| Medium | Lỗi validate, message hoặc edge case có workaround |
| Low | Lỗi tài liệu, format response/message nhỏ, không ảnh hưởng nghiệp vụ chính |

## 13. Rủi ro và biện pháp giảm thiểu

| Rủi ro | Ảnh hưởng | Biện pháp |
|---|---|---|
| Sai phân quyền owner/staff/admin | Lộ dữ liệu hoặc thao tác sai quyền | Bắt buộc có unit permission và integration negative test |
| Sai trạng thái appointment | Hỏng luồng khám/thanh toán | Test đầy đủ state transition và trạng thái không hợp lệ |
| Sai tính amount payment | Thu tiền sai | Unit test `_calculate_amount`, integration với prescription items |
| Sai xử lý VNPAY callback | Payment/appointment không đồng bộ | Test return/IPN success, fail, invalid signature, invalid amount |
| Báo cáo tính sai doanh thu | Số liệu admin sai | Test chỉ tính payment `PAID` có `paid_at` |
| Dữ liệu ngày giờ cũ trong manual case | Case hợp lệ bị backend reject | Manual tester phải cập nhật appointment time tương lai trước khi chạy |
| Database test không sạch | Kết quả không lặp lại | Dùng pytest database isolation và seed data rõ ràng |

## 14. Deliverables

| Artifact | Mục đích |
|---|---|
| `backend/src/tests/unit` | Bộ unit test backend |
| `backend/src/tests/integration` | Bộ integration test backend |
| `docs/manual-test-cases-2del.xlsx` | Bộ manual API test case và kết quả chạy thủ công |
| `docs/test-report.md` | Báo cáo kết quả kiểm thử |
| Coverage report | Bằng chứng coverage backend nếu được yêu cầu |

## 15. Kết luận

Test plan này chỉ tập trung vào backend và ba hình thức kiểm thử: unit, integration và manual API. Phần frontend được loại khỏi phạm vi để phù hợp yêu cầu kiểm thử hiện tại.

Khi áp dụng test plan, nhóm cần ưu tiên các module có rủi ro cao: authentication/authorization, appointment workflow, prescription/medicine stock, payment VNPAY và report doanh thu. Đây là các khu vực có ảnh hưởng trực tiếp đến bảo mật, toàn vẹn dữ liệu và kết quả nghiệp vụ của hệ thống.
