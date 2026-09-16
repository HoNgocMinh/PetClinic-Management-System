import React, { useEffect, useState } from "react";
import { Container, Table, Button, Modal, Form, Card, Badge, Spinner, Col, Row } from "react-bootstrap";
import { authApis, endpoint } from "../../configs/Apis";
import toast from "react-hot-toast";

const AdminStaff = () => {
    const [staffs, setStaffs] = useState([]);
    const [clinics, setClinics] = useState([]);
    const [loading, setLoading] = useState(false);
    const [show, setShow] = useState(false);

    const [currentStaff, setCurrentStaff] = useState({
        username: "", email: "", password: "", full_name: "",
        phone: "", address: "", clinic_id: "", is_active: true
    });

    const loadData = async () => {
        try {
            setLoading(true);
            const resStaff = await authApis().get(endpoint['admin_staffs']);
            setStaffs(resStaff.data.data || resStaff.data);

            const resClinic = await authApis().get(endpoint['clinics']);
            setClinics(resClinic.data.data || resClinic.data);
        } catch (ex) {
            toast.error("Không thể tải dữ liệu nhân sự");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { loadData(); }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            if (currentStaff.id) {
                await authApis().put(`${endpoint['admin_staffs']}${currentStaff.id}/`, currentStaff);
                toast.success("Cập nhật nhân viên thành công");
            } else {
                await authApis().post(endpoint['admin_staffs'], currentStaff);
                toast.success("Tạo tài khoản nhân viên thành công");
            }
            setShow(false);
            loadData();
        } catch (ex) {
            console.error("Full Error Response:", ex.response?.data);

            const errorMsg = ex.response?.data?.message || "Dữ liệu không hợp lệ";
            const detailErrors = ex.response?.data?.errors;

            if (detailErrors) {
                const firstKey = Object.keys(detailErrors)[0];
                toast.error(`${firstKey}: ${detailErrors[firstKey][0]}`);
            } else {
                toast.error(errorMsg);
            }
        }
    };

    const handleToggleStatus = async (staff) => {
        const newStatus = !staff.is_active;
        const action = newStatus ? "Mở khóa" : "Khóa";

        if (window.confirm(`Xác nhận ${action} tài khoản nhân viên này?`)) {
            try {
                await authApis().put(`${endpoint['admin_staffs']}${staff.id}/`, {
                    ...staff,       
                    is_active: newStatus 
                });

                toast.success(`${action} tài khoản thành công!`);
                loadData(); 
            } catch (ex) {
                console.error(ex);
                toast.error(`Không thể ${action} tài khoản.`);
            }
        }
    };

    return (
        <Container className="mt-4">
            <Card className="shadow-sm border-0">
                <Card.Header className="bg-dark text-white d-flex justify-content-between align-items-center py-3">
                    <h5 className="mb-0 fw-bold">QUẢN LÝ TÀI KHOẢN NHÂN VIÊN</h5>
                    <Button variant="success" size="sm" onClick={() => { setCurrentStaff({ username: "", email: "", password: "", full_name: "", phone: "", address: "", clinic_id: "", is_active: true }); setShow(true); }}>
                        + TẠO NHÂN VIÊN MỚI
                    </Button>
                </Card.Header>
                <Card.Body>
                    <Table responsive hover className="align-middle">
                        <thead className="table-light">
                            <tr>
                                <th>Họ tên / Username</th>
                                <th>Liên hệ</th>
                                <th>Phòng khám</th>
                                <th>Trạng thái</th>
                                <th>Thao tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            {staffs.map(s => (
                                <tr key={s.id}>
                                    <td>
                                        <div className="fw-bold">{s.full_name}</div>
                                        <small className="text-muted">@{s.username}</small>
                                    </td>
                                    <td>
                                        <div>{s.email}</div>
                                        <small>{s.phone}</small>
                                    </td>
                                    <td><Badge bg="primary">{s.clinic_name || "N/A"}</Badge></td>
                                    <td>
                                        {s.is_active ? <Badge bg="success">Đang hoạt động</Badge> : <Badge bg="danger">Đã khóa</Badge>}
                                    </td>
                                    <td>
                                        <Button variant="outline-warning" size="sm" className="me-2" onClick={() => { setCurrentStaff(s); setShow(true); }}>Sửa</Button>
                                        <Button
                                            variant={s.is_active ? "outline-danger" : "outline-success"}
                                            size="sm"
                                            onClick={() => handleToggleStatus(s)} // Truyền nguyên object s
                                        >
                                            {s.is_active ? "Khóa tài khoản" : "Mở khóa"}
                                        </Button>                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </Table>
                </Card.Body>
            </Card>

            <Modal show={show} onHide={() => setShow(false)} size="lg" centered>
                <Modal.Header closeButton><Modal.Title className="h6 fw-bold">THÔNG TIN NHÂN VIÊN</Modal.Title></Modal.Header>
                <Form onSubmit={handleSubmit}>
                    <Modal.Body>
                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label className="small fw-bold">Username</Form.Label>
                                    <Form.Control type="text" value={currentStaff.username} onChange={e => setCurrentStaff({ ...currentStaff, username: e.target.value })} disabled={currentStaff.id} required />
                                </Form.Group>
                            </Col>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label className="small fw-bold">Mật khẩu</Form.Label>
                                    <Form.Control type="password" placeholder={currentStaff.id ? "(Để trống nếu không đổi)" : "Nhập mật khẩu"} onChange={e => setCurrentStaff({ ...currentStaff, password: e.target.value })} required={!currentStaff.id} />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Form.Group className="mb-3">
                            <Form.Label className="small fw-bold">Họ và tên</Form.Label>
                            <Form.Control type="text" value={currentStaff.full_name} onChange={e => setCurrentStaff({ ...currentStaff, full_name: e.target.value })} required />
                        </Form.Group>
                        <Row>
                            <Col md={6}><Form.Group className="mb-3"><Form.Label className="small fw-bold">Email</Form.Label><Form.Control type="email" value={currentStaff.email} onChange={e => setCurrentStaff({ ...currentStaff, email: e.target.value })} required /></Form.Group></Col>
                            <Col md={6}><Form.Group className="mb-3"><Form.Label className="small fw-bold">Số điện thoại</Form.Label><Form.Control type="text" value={currentStaff.phone} onChange={e => setCurrentStaff({ ...currentStaff, phone: e.target.value })} required /></Form.Group></Col>
                        </Row>
                        <Form.Group className="mb-3">
                            <Form.Label className="small fw-bold">Phòng khám trực thuộc</Form.Label>
                            <Form.Select value={currentStaff.clinic_id} onChange={e => setCurrentStaff({ ...currentStaff, clinic_id: e.target.value })} required>
                                <option value="">-- Chọn phòng khám --</option>
                                {clinics.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                            </Form.Select>
                        </Form.Group>
                    </Modal.Body>
                    <Modal.Footer><Button variant="secondary" onClick={() => setShow(false)}>Đóng</Button><Button variant="primary" type="submit">Lưu thông tin</Button></Modal.Footer>
                </Form>
            </Modal>
        </Container>
    );
};

export default AdminStaff;
