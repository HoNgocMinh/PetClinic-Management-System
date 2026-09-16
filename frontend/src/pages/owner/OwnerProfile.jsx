import { useContext, useEffect, useMemo, useState } from "react";
import { Alert, Badge, Button, Card, Col, Container, Form, Row, Spinner } from "react-bootstrap";
import { FaCalendarCheck, FaEnvelope, FaMapMarkerAlt, FaPaw, FaPhoneAlt, FaUserCircle } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import cookie from "react-cookies";
import toast from "react-hot-toast";

import { authApis, endpoint } from "../../configs/Apis";
import { MyDipatcherContext, MyUserContext } from "../../configs/MyContexts";

const EMPTY_PROFILE = {
    full_name: "",
    phone: "",
    address: "",
};

const roleLabels = {
    PET_OWNER: "Chủ thú cưng",
    CLINIC_STAFF: "Nhân viên phòng khám",
    ADMIN: "Quản trị viên",
};

const formatDateTime = (value) => {
    if (!value) return "Chưa có dữ liệu";

    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "Chưa có dữ liệu";

    return date.toLocaleString("vi-VN", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
};

const getInitials = (name) => {
    if (!name) return "U";

    return name
        .trim()
        .split(/\s+/)
        .slice(-2)
        .map(part => part[0])
        .join("")
        .toUpperCase();
};

const OwnerProfile = () => {
    const currentUser = useContext(MyUserContext);
    const dispatch = useContext(MyDipatcherContext);
    const navigate = useNavigate();

    const [profile, setProfile] = useState(currentUser || null);
    const [form, setForm] = useState(EMPTY_PROFILE);
    const [pets, setPets] = useState([]);
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [editing, setEditing] = useState(false);

    useEffect(() => {
        const loadProfile = async () => {
            try {
                setLoading(true);

                const [profileRes, petsRes, appointmentsRes] = await Promise.allSettled([
                    authApis().get(endpoint['current_user']),
                    authApis().get(endpoint['pets']),
                    authApis().get(endpoint['appointments']),
                ]);

                if (profileRes.status === "fulfilled") {
                    const userData = profileRes.value.data.data || profileRes.value.data;
                    setProfile(userData);
                    setForm({
                        full_name: userData.full_name || "",
                        phone: userData.phone || "",
                        address: userData.address || "",
                    });
                    cookie.save("user", userData, { path: "/" });
                    dispatch({ type: "login", payload: userData });
                } else {
                    toast.error("Không thể tải thông tin hồ sơ.");
                }

                if (petsRes.status === "fulfilled") {
                    setPets(petsRes.value.data.data || petsRes.value.data || []);
                }

                if (appointmentsRes.status === "fulfilled") {
                    setAppointments(appointmentsRes.value.data.data || appointmentsRes.value.data || []);
                }
            } catch {
                toast.error("Không thể tải trang hồ sơ.");
            } finally {
                setLoading(false);
            }
        };

        loadProfile();
    }, [dispatch]);

    const upcomingAppointments = useMemo(() => {
        const upcomingStatuses = ["PENDING", "CONFIRMED", "WAITING_PAYMENT"];
        return appointments.filter(app => upcomingStatuses.includes(app.status));
    }, [appointments]);

    const latestAppointment = useMemo(() => {
        return [...appointments]
            .filter(app => app.appointment_time)
            .sort((a, b) => new Date(b.appointment_time) - new Date(a.appointment_time))[0];
    }, [appointments]);

    const handleChange = (field, value) => {
        setForm(prev => ({ ...prev, [field]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            setSaving(true);
            const res = await authApis().put(endpoint['current_user'], form);
            const userData = res.data.data || res.data;

            setProfile(userData);
            setForm({
                full_name: userData.full_name || "",
                phone: userData.phone || "",
                address: userData.address || "",
            });
            cookie.save("user", userData, { path: "/" });
            dispatch({ type: "login", payload: userData });
            setEditing(false);
            toast.success("Cập nhật hồ sơ thành công.");
        } catch (ex) {
            const errors = ex.response?.data?.errors;
            if (errors) {
                const firstKey = Object.keys(errors)[0];
                toast.error(errors[firstKey][0]);
            } else {
                toast.error(ex.response?.data?.message || "Không thể cập nhật hồ sơ.");
            }
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <Container className="text-center mt-5">
                <Spinner animation="border" variant="success" />
            </Container>
        );
    }

    if (!profile) {
        return (
            <Container className="mt-5">
                <Alert variant="warning">Bạn cần đăng nhập để xem hồ sơ cá nhân.</Alert>
            </Container>
        );
    }

    return (
        <Container className="mt-4 mb-5 owner-profile-page">
            <Row className="g-4">
                <Col lg={4}>
                    <Card className="shadow-sm border-0 owner-profile-card">
                        <Card.Body className="text-center p-4">
                            <div className="owner-profile-avatar mx-auto mb-3">
                                {getInitials(profile.full_name || profile.username)}
                            </div>
                            <h3 className="h5 fw-bold mb-1">{profile.full_name || profile.username}</h3>
                            <p className="text-muted mb-3">@{profile.username}</p>
                            <Badge bg="success" className="px-3 py-2">
                                {roleLabels[profile.role] || profile.role}
                            </Badge>

                            <div className="owner-profile-contact text-start mt-4">
                                <div>
                                    <FaEnvelope className="text-success" />
                                    <span>{profile.email || "Chưa cập nhật email"}</span>
                                </div>
                                <div>
                                    <FaPhoneAlt className="text-success" />
                                    <span>{profile.phone || "Chưa cập nhật số điện thoại"}</span>
                                </div>
                                <div>
                                    <FaMapMarkerAlt className="text-success" />
                                    <span>{profile.address || "Chưa cập nhật địa chỉ"}</span>
                                </div>
                            </div>
                        </Card.Body>
                    </Card>
                </Col>

                <Col lg={8}>
                    <Row className="g-3 mb-4">
                        <Col md={4}>
                            <Card className="shadow-sm border-0 owner-profile-stat">
                                <Card.Body>
                                    <FaPaw className="text-success mb-2" />
                                    <div className="owner-profile-stat-value">{pets.length}</div>
                                    <div className="text-muted small">Thú cưng đã đăng ký</div>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col md={4}>
                            <Card className="shadow-sm border-0 owner-profile-stat">
                                <Card.Body>
                                    <FaCalendarCheck className="text-success mb-2" />
                                    <div className="owner-profile-stat-value">{upcomingAppointments.length}</div>
                                    <div className="text-muted small">Lịch hẹn sắp tới</div>
                                </Card.Body>
                            </Card>
                        </Col>
                        <Col md={4}>
                            <Card className="shadow-sm border-0 owner-profile-stat">
                                <Card.Body>
                                    <FaUserCircle className="text-success mb-2" />
                                    <div className="owner-profile-stat-value">{profile.is_active ? "OK" : "Khóa"}</div>
                                    <div className="text-muted small">Trạng thái tài khoản</div>
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>

                    <Card className="shadow-sm border-0 mb-4">
                        <Card.Header className="bg-dark text-white d-flex justify-content-between align-items-center py-3">
                            <h5 className="mb-0 fw-bold">Hồ sơ cá nhân</h5>
                            {!editing && (
                                <div className="d-flex gap-2 flex-wrap justify-content-end">
                                    <Button variant="outline-light" size="sm" onClick={() => navigate("/change-password")}>
                                        Đổi mật khẩu
                                    </Button>
                                    <Button variant="success" size="sm" onClick={() => setEditing(true)}>
                                        Chỉnh sửa
                                    </Button>
                                </div>
                            )}
                        </Card.Header>
                        <Card.Body className="p-4">
                            <Form onSubmit={handleSubmit}>
                                <Row>
                                    <Col md={6}>
                                        <Form.Group className="mb-3">
                                            <Form.Label className="small fw-bold">Tên đăng nhập</Form.Label>
                                            <Form.Control value={profile.username || ""} disabled />
                                        </Form.Group>
                                    </Col>
                                    <Col md={6}>
                                        <Form.Group className="mb-3">
                                            <Form.Label className="small fw-bold">Email</Form.Label>
                                            <Form.Control value={profile.email || ""} disabled />
                                        </Form.Group>
                                    </Col>
                                </Row>

                                <Form.Group className="mb-3">
                                    <Form.Label className="small fw-bold">Họ và tên</Form.Label>
                                    <Form.Control
                                        value={form.full_name}
                                        disabled={!editing}
                                        required
                                        onChange={e => handleChange("full_name", e.target.value)}
                                    />
                                </Form.Group>

                                <Form.Group className="mb-3">
                                    <Form.Label className="small fw-bold">Số điện thoại</Form.Label>
                                    <Form.Control
                                        value={form.phone}
                                        disabled={!editing}
                                        onChange={e => handleChange("phone", e.target.value)}
                                    />
                                </Form.Group>

                                <Form.Group className="mb-3">
                                    <Form.Label className="small fw-bold">Địa chỉ</Form.Label>
                                    <Form.Control
                                        as="textarea"
                                        rows={3}
                                        value={form.address}
                                        disabled={!editing}
                                        onChange={e => handleChange("address", e.target.value)}
                                    />
                                </Form.Group>

                                {editing && (
                                    <div className="d-flex justify-content-end gap-2">
                                        <Button
                                            variant="outline-secondary"
                                            type="button"
                                            onClick={() => {
                                                setForm({
                                                    full_name: profile.full_name || "",
                                                    phone: profile.phone || "",
                                                    address: profile.address || "",
                                                });
                                                setEditing(false);
                                            }}
                                            disabled={saving}
                                        >
                                            Hủy
                                        </Button>
                                        <Button variant="success" type="submit" disabled={saving}>
                                            {saving ? "Đang lưu..." : "Lưu thay đổi"}
                                        </Button>
                                    </div>
                                )}
                            </Form>
                        </Card.Body>
                    </Card>

                    <Card className="shadow-sm border-0">
                        <Card.Header className="bg-light py-3">
                            <h5 className="mb-0 fw-bold text-success">Tổng quan chăm sóc</h5>
                        </Card.Header>
                        <Card.Body className="p-4">
                            <Row className="g-3">
                                <Col md={6}>
                                    <div className="owner-profile-summary">
                                        <div className="small text-muted">Thú cưng gần đây</div>
                                        <div className="fw-bold">
                                            {pets[0]?.name || "Chưa có thú cưng"}
                                        </div>
                                        <div className="text-muted small">
                                            {pets[0]?.species || "Hãy thêm thú cưng để bắt đầu đặt lịch khám."}
                                        </div>
                                    </div>
                                </Col>
                                <Col md={6}>
                                    <div className="owner-profile-summary">
                                        <div className="small text-muted">Lịch hẹn gần nhất</div>
                                        <div className="fw-bold">
                                            {latestAppointment?.clinic_name || "Chưa có lịch hẹn"}
                                        </div>
                                        <div className="text-muted small">
                                            {formatDateTime(latestAppointment?.appointment_time)}
                                        </div>
                                    </div>
                                </Col>
                            </Row>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default OwnerProfile;
