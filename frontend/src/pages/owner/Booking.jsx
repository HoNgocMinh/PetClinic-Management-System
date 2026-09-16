import { useEffect, useState } from "react";
import { Container, Form, Button, Row, Col, Card, FloatingLabel, Alert } from "react-bootstrap";
import { authApis, endpoint } from "../../configs/Apis";
import MySpinner from "../../component/layout/MySpinner";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";

// Danh sách các khung giờ cố định (ca 60 phút)
const TIME_SLOTS = [
    "08:00", "09:00", "10:00", "11:00",
    "13:00", "14:00", "15:00", "16:00", "17:00"
];

const Booking = () => {
    const [pets, setPets] = useState([]);
    const [clinics, setClinics] = useState([]);
    const [services, setServices] = useState([]);
    const [loading, setLoading] = useState(false);
    const nav = useNavigate();

    // State trung gian để quản lý việc chọn thời gian
    const [selectedDate, setSelectedDate] = useState("");
    const [selectedTime, setSelectedTime] = useState("");

    const [bookingData, setBookingData] = useState({
        pet_id: "",
        clinic_id: "",
        service_id: "",
        appointment_time: "",
        note: ""
    });

    // 1. Load danh sách Thú cưng và Phòng khám[cite: 4, 6]
    useEffect(() => {
        const loadInitialData = async () => {
            try {
                const [petRes, clinicRes] = await Promise.all([
                    authApis().get(endpoint['pets']),
                    authApis().get(endpoint['clinics'])
                ]);
                setPets(petRes.data.data || petRes.data);
                setClinics(clinicRes.data.data || clinicRes.data);
            } catch (ex) {
                toast.error("Không thể tải dữ liệu ban đầu.");
            }
        };
        loadInitialData();
    }, []);

    // 2. Load dịch vụ theo phòng khám đã chọn[cite: 4, 6]
    useEffect(() => {
        if (bookingData.clinic_id) {
            const loadServices = async () => {
                try {
                    const res = await authApis().get(endpoint['services_by_clinic'](bookingData.clinic_id));
                    setServices(res.data.data || res.data);
                } catch (ex) {
                    toast.error("Không thể tải danh sách dịch vụ.");
                }
            };
            loadServices();
        } else {
            setServices([]);
        }
    }, [bookingData.clinic_id]);

    // 3. Logic ghép Ngày và Giờ thành định dạng chuẩn ISO cho Backend
    useEffect(() => {
        if (selectedDate && selectedTime) {
            setBookingData(prev => ({
                ...prev,
                appointment_time: `${selectedDate}T${selectedTime}:00`
            }));
        }
    }, [selectedDate, selectedTime]);

    const handleBooking = async (e) => {
        e.preventDefault();
        try {
            setLoading(true);
            await authApis().post(endpoint['appointments'], bookingData);
            toast.success("Đặt lịch thành công!");
            nav("/appointments");
        } catch (ex) {
            const errorData = ex.response?.data;
            // Backend trả về lỗi trùng lịch trong trường 'message' hoặc 'errors'[cite: 11]
            if (errorData?.message) {
                toast.error(errorData.message); // Hiển thị "Khung giờ này bị trùng..."
            } else if (errorData?.errors) {
                const firstErr = Object.values(errorData.errors)[0][0];
                toast.error(firstErr);
            } else {
                toast.error("Không thể đặt lịch, vui lòng thử khung giờ khác.");
            }
        } finally {
            setLoading(false);
        }
    };

    // Xử lý khi chưa có thú cưng
    if (pets.length === 0 && !loading) {
        return (
            <Container className="mt-5 text-center">
                <Card className="p-5 shadow-sm border-0">
                    <h3 className="text-muted">Bạn chưa đăng ký thú cưng nào!</h3>
                    <p>Vui lòng đăng ký thú cưng trước khi đặt lịch khám.</p>
                    <div className="mt-3">
                        <Button variant="primary" onClick={() => nav("/pets")}>
                            Đăng ký thú cưng ngay
                        </Button>
                    </div>
                </Card>
            </Container>
        );
    }

    return (
        <Container className="mt-5 mb-5">
            <Row className="justify-content-center">
                <Col md={8} lg={6}>
                    <Card className="shadow-lg border-0">
                        <Card.Body className="p-4">
                            <h2 className="text-center text-success mb-4 fw-bold">ĐẶT LỊCH KHÁM BỆNH</h2>

                            <Alert variant="success" className="text-center">
                                <small>Lịch khám cố định <b>60 phút/ca</b>. Vui lòng chọn khung giờ chẵn.</small>
                            </Alert>

                            <Form onSubmit={handleBooking}>
                                {/* Chọn Thú Cưng[cite: 1, 3] */}
                                <Form.Group className="mb-3">
                                    <Form.Label className="fw-bold">Chọn thú cưng</Form.Label>
                                    <Form.Select required value={bookingData.pet_id}
                                        onChange={e => setBookingData({ ...bookingData, pet_id: e.target.value })}>
                                        <option value="">-- Chọn thú cưng --</option>
                                        {pets.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                                    </Form.Select>
                                </Form.Group>

                                {/* Chọn Phòng Khám */}
                                <Form.Group className="mb-3">
                                    <Form.Label className="fw-bold">Chọn phòng khám</Form.Label>
                                    <Form.Select required value={bookingData.clinic_id}
                                        onChange={e => setBookingData({ ...bookingData, clinic_id: e.target.value, service_id: "" })}>
                                        <option value="">-- Chọn phòng khám --</option>
                                        {clinics.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                                    </Form.Select>
                                </Form.Group>

                                {/* Chọn Dịch Vụ[cite: 2, 4] */}
                                <Form.Group className="mb-3">
                                    <Form.Label className="fw-bold">Dịch vụ</Form.Label>
                                    <Form.Select required disabled={!bookingData.clinic_id} value={bookingData.service_id}
                                        onChange={e => setBookingData({ ...bookingData, service_id: e.target.value })}>
                                        <option value="">-- Chọn dịch vụ --</option>
                                        {services.map(s => (
                                            <option key={s.id} value={s.id}>
                                                {s.name} ({parseFloat(s.price).toLocaleString()}đ - {s.duration_minutes}p)
                                            </option>
                                        ))}
                                    </Form.Select>
                                </Form.Group>

                                {/* Chọn Ngày và Giờ riêng biệt[cite: 3, 5] */}
                                <Row className="mb-3">
                                    <Col md={6}>
                                        <Form.Group>
                                            <Form.Label className="fw-bold">Ngày khám</Form.Label>
                                            <Form.Control
                                                type="date"
                                                required
                                                min={new Date().toISOString().split("T")[0]}
                                                onChange={e => setSelectedDate(e.target.value)}
                                            />
                                        </Form.Group>
                                    </Col>
                                    <Col md={6}>
                                        <Form.Group>
                                            <Form.Label className="fw-bold">Khung giờ</Form.Label>
                                            <Form.Select required onChange={e => setSelectedTime(e.target.value)}>
                                                <option value="">-- Giờ --</option>
                                                {TIME_SLOTS.map(slot => (
                                                    <option key={slot} value={slot}>{slot}</option>
                                                ))}
                                            </Form.Select>
                                        </Form.Group>
                                    </Col>
                                </Row>

                                {/* Ghi Chú[cite: 1, 3] */}
                                <FloatingLabel label="Triệu chứng/Ghi chú" className="mb-4">
                                    <Form.Control as="textarea" style={{ height: '100px' }}
                                        onChange={e => setBookingData({ ...bookingData, note: e.target.value })} />
                                </FloatingLabel>

                                <Button variant="success" type="submit" className="w-100 py-2 fw-bold" disabled={loading}>
                                    {loading ? <MySpinner /> : "XÁC NHẬN ĐẶT LỊCH"}
                                </Button>
                            </Form>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default Booking;
