import { useState, useRef, useEffect } from "react";
import { Container, Row, Col, Form, FloatingLabel, Button, Alert } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import Apis, { endpoint } from "../../configs/Apis";
import MySpinner from "../../component/layout/MySpinner";

const Register = () => {
    const [user, setUser] = useState({});
    const [msg, setMsg] = useState();
    const [loading, setLoading] = useState(false);
    const avatar = useRef();
    const nav = useNavigate();

    const setState = (value, field) => setUser({ ...user, [field]: value });

    const register = async (e) => {
        e.preventDefault();
        setMsg(null);

        if (user.password !== user.confirm) {
            setMsg("Xác nhận mật khẩu không khớp.");
            return;
        }

        try {
            setLoading(true);
            const { confirm, ...registerData } = user;
            const res = await Apis.post(endpoint['register'], registerData);

            if (res.status === 201 || res.status === 200) {
                toast.success("Đăng ký thành công!");
                nav("/login");
            }
        } catch (ex) {
            console.error("Full Error:", ex.response?.data);
            const errorData = ex.response?.data;

            if (errorData && errorData.errors) {
                // Lấy danh sách các trường bị lỗi (ví dụ: ["password", "email"])
                const fields = Object.keys(errorData.errors);
                // Lấy lỗi đầu tiên của trường đầu tiên
                const firstField = fields[0];
                const firstError = errorData.errors[firstField][0];
                setMsg(firstError);
            } else if (errorData && errorData.message) {
                setMsg(errorData.message);
            } else {
                setMsg("Đã có lỗi xảy ra. Vui lòng thử lại!");
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container fluid className="p-0 bg-light">
            <Row className="justify-content-center align-items-center m-0 py-5" style={{ minHeight: "85vh" }}>
                <Col lg={7} md={10} sm={12}>
                    <div className="p-4 shadow-lg rounded bg-white">
                        <h2 className="text-center text-success mb-4 fw-bold">TẠO TÀI KHOẢN MỚI</h2>
                        {msg && <Alert variant="danger" className="text-center py-2">{msg}</Alert>}

                        <Form onSubmit={register}>
                            <Row>
                                {/* Hàng 1: Thông tin tài khoản */}
                                <Col md={6} className="mb-3">
                                    <FloatingLabel label="Tên đăng nhập">
                                        <Form.Control type="text" required value={user.username || ''} onChange={e => setState(e.target.value, 'username')} />
                                    </FloatingLabel>
                                </Col>
                                <Col md={6} className="mb-3">
                                    <FloatingLabel label="Địa chỉ Email">
                                        <Form.Control type="email" required value={user.email || ''} onChange={e => setState(e.target.value, 'email')} />
                                    </FloatingLabel>
                                </Col>

                                {/* Hàng 2: Bảo mật */}
                                <Col md={6} className="mb-3">
                                    <FloatingLabel label="Mật khẩu (từ 6 ký tự)">
                                        <Form.Control type="password" required value={user.password || ''} onChange={e => setState(e.target.value, 'password')} />
                                    </FloatingLabel>
                                </Col>
                                <Col md={6} className="mb-3">
                                    <FloatingLabel label="Xác nhận mật khẩu">
                                        <Form.Control type="password" required value={user.confirm || ''} onChange={e => setState(e.target.value, 'confirm')} />
                                    </FloatingLabel>
                                </Col>

                                {/* Hàng 3: Thông tin cá nhân */}
                                <Col md={12} className="mb-3">
                                    <FloatingLabel label="Họ và tên đầy đủ">
                                        <Form.Control type="text" required value={user.full_name || ''} onChange={e => setState(e.target.value, 'full_name')} />
                                    </FloatingLabel>
                                </Col>

                                {/* Hàng 4: Liên lạc */}
                                <Col md={4} className="mb-3">
                                    <FloatingLabel label="Số điện thoại">
                                        <Form.Control type="text" value={user.phone || ''} onChange={e => setState(e.target.value, 'phone')} />
                                    </FloatingLabel>
                                </Col>
                                <Col md={8} className="mb-3">
                                    <FloatingLabel label="Địa chỉ">
                                        <Form.Control type="text" value={user.address || ''} onChange={e => setState(e.target.value, 'address')} />
                                    </FloatingLabel>
                                </Col>

                                <Col md={12} className="mb-4">
                                    <Form.Group>
                                        <Form.Label className="small fw-bold text-muted">Ảnh đại diện:</Form.Label>
                                        <Form.Control ref={avatar} type="file" accept="image/*" size="sm" />
                                    </Form.Group>
                                </Col>
                            </Row>

                            <Button type="submit" variant="success" className="w-100 py-2 fw-bold shadow-sm" disabled={loading}>
                                {loading ? <MySpinner /> : "ĐĂNG KÝ NGAY"}
                            </Button>
                        </Form>
                    </div>
                </Col>
            </Row>
        </Container>
    );
};

export default Register;
