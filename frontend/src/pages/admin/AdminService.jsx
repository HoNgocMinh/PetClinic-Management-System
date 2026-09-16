import React, { useEffect, useState } from "react";
import { Container, Table, Button, Modal, Form, Card, Row, Col, Spinner, Badge } from "react-bootstrap";
import { authApis, endpoint } from "../../configs/Apis";
import toast from "react-hot-toast";

const AdminService = () => {
    const [clinics, setClinics] = useState([]);
    const [selectedClinicId, setSelectedClinicId] = useState("");
    const [services, setServices] = useState([]);
    const [show, setShow] = useState(false);
    const [loading, setLoading] = useState(false);

    const [currentService, setCurrentService] = useState({
        name: "", price: "", description: "", service_type: "EXAM",
        duration_minutes: 60, is_active: true
    });

    // --- Load danh sách phòng khám ---
    useEffect(() => {
        const loadClinics = async () => {
            try {
                const res = await authApis().get(endpoint['clinics']);
                setClinics(res.data.data || res.data);
            } catch (ex) {
                toast.error("Không thể tải danh sách phòng khám");
            }
        };
        loadClinics();
    }, []);

    // --- Load danh sách dịch vụ theo phòng khám ---
    const loadServicesByClinic = async () => {
        if (!selectedClinicId) {
            setServices([]);
            return;
        }
        try {
            setLoading(true);
            const res = await authApis().get(`${endpoint['clinics']}${selectedClinicId}/services/`);
            const data = res.data.data || res.data;
            setServices(Array.isArray(data) ? data : []);
        } catch (ex) {
            console.error("Lỗi tải danh mục dịch vụ:", ex); // chỉ log, không show toast
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadServicesByClinic();
    }, [selectedClinicId]);

    // --- Thay đổi trạng thái dịch vụ ---
    const handleToggleStatus = async (service) => {
        const action = service.is_active ? "Tắt" : "Bật lại";
        if (window.confirm(`Bạn có chắc muốn ${action} dịch vụ này?`)) {
            try {
                await authApis().put(`${endpoint['services']}${service.id}/`, {
                    ...service,
                    is_active: !service.is_active
                });
                toast.success(`Đã ${action} dịch vụ`);
                loadServicesByClinic().catch(err => console.error("Lỗi reload dịch vụ:", err));
            } catch (ex) {
                toast.error("Không thể thay đổi trạng thái");
            }
        }
    };

    // --- Thêm/Cập nhật dịch vụ ---
    const handleSubmit = async (e) => {
        e.preventDefault();

        const duration = parseInt(currentService.duration_minutes);
        if (!duration || duration < 60) {
            toast.error("Thời lượng tối thiểu phải là 60 phút!");
            return;
        }

        const payload = {
            name: currentService.name,
service_type: currentService.service_type,
            description: currentService.description,
            price: currentService.price.toString(),
            duration_minutes: duration,
        };

        if (currentService.id) {
            payload.is_active = currentService.is_active;
        } else {
            payload.clinic_id = parseInt(selectedClinicId);
        }

        try {
            if (currentService.id) {
                await authApis().put(`${endpoint['services']}${currentService.id}/`, payload);
                toast.success("Cập nhật dịch vụ thành công!");
            } else {
                await authApis().post(endpoint['services'], payload);
                toast.success("Thêm dịch vụ thành công!");
            }

            setShow(false);

            if (selectedClinicId) {
                loadServicesByClinic().catch(err => console.error("Lỗi reload dịch vụ:", err));
            }
        } catch (apiError) {
            console.error("Lỗi API:", apiError.response?.data || apiError);
            const message = apiError.response?.data?.message || "Có lỗi xảy ra, vui lòng kiểm tra lại";
            toast.error(message);
        }
    };

    return (
        <Container className="mt-4">
            <Card className="shadow-sm border-0 mb-4">
                <Card.Body className="bg-light">
                    <Row className="align-items-center">
                        <Col md={4}><h5 className="mb-0 fw-bold text-primary">QUẢN LÝ DỊCH VỤ</h5></Col>
                        <Col md={5}>
                            <Form.Select value={selectedClinicId} onChange={(e) => setSelectedClinicId(e.target.value)}>
                                <option value="">-- Chọn phòng khám để quản lý --</option>
                                {clinics.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                            </Form.Select>
                        </Col>
                        <Col md={3} className="text-end">
                            <Button variant="primary" disabled={!selectedClinicId} onClick={() => {
                                setCurrentService({ name: "", price: "", description: "", service_type: "EXAM", duration_minutes: 60, is_active: true });
                                setShow(true);
                            }}>+ Thêm dịch vụ</Button>
                        </Col>
                    </Row>
                </Card.Body>
            </Card>

            {selectedClinicId ? (
                <Card className="border-0 shadow-sm">
                    {loading ? (
                        <div className="text-center py-5"><Spinner animation="border" /></div>
                    ) : services.length > 0 ? (
                        <Table responsive hover className="align-middle mb-0">
                            <thead className="table-dark">
                                <tr>
<th>Tên dịch vụ</th>
                                    <th>Loại</th>
                                    <th>Thời lượng</th>
                                    <th>Giá niêm yết</th>
                                    <th>Trạng thái</th>
                                    <th>Thao tác</th>
                                </tr>
                            </thead>
                            <tbody>
                                {services.map(s => (
                                    <tr key={s.id}>
                                        <td className="fw-bold">{s.name}</td>
                                        <td><Badge bg="secondary">{s.service_type}</Badge></td>
                                        <td>{s.duration_minutes} phút</td>
                                        <td className="text-danger fw-bold">{Number(s.price).toLocaleString('vi-VN')} đ</td>
                                        <td>{s.is_active ? <Badge bg="success">Hoạt động</Badge> : <Badge bg="danger">Ngừng</Badge>}</td>
                                        <td>
                                            <Button variant="outline-warning" size="sm" onClick={() => { setCurrentService(s); setShow(true); }}>Sửa</Button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    ) : (
                        <div className="text-center py-5 text-muted">Phòng khám này hiện chưa có dịch vụ nào.</div>
                    )}
                </Card>
            ) : null}

            <Modal show={show} onHide={() => setShow(false)} centered size="lg">
                <Form onSubmit={handleSubmit}>
                    <Modal.Header closeButton>
                        <Modal.Title>{currentService.id ? "Cập nhật dịch vụ" : "Thêm dịch vụ mới"}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <Row>
                            <Col md={8}>
                                <Form.Group className="mb-3">
                                    <Form.Label className="fw-bold">Tên dịch vụ</Form.Label>
                                    <Form.Control value={currentService.name} onChange={e => setCurrentService({ ...currentService, name: e.target.value })} required />
                                </Form.Group>
                            </Col>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label className="fw-bold">Loại</Form.Label>
                                    <Form.Select value={currentService.service_type} onChange={e => setCurrentService({ ...currentService, service_type: e.target.value })}>
                                        <option value="EXAM">Khám bệnh</option>
<option value="GROOMING">Grooming</option>
                                        <option value="VACCINE">Tiêm chủng</option>
                                        <option value="OTHER">Khác</option>
                                    </Form.Select>
                                </Form.Group>
                            </Col>
                        </Row>
                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label className="fw-bold">Giá dịch vụ (VNĐ)</Form.Label>
                                    <Form.Control type="number" value={currentService.price} onChange={e => setCurrentService({ ...currentService, price: e.target.value })} required />
                                </Form.Group>
                            </Col>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label className="fw-bold">Thời lượng (Phút)</Form.Label>
                                    <Form.Control type="number" value={currentService.duration_minutes} onChange={e => setCurrentService({ ...currentService, duration_minutes: e.target.value })} required />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Form.Group className="mb-3">
                            <Form.Label className="fw-bold">Mô tả chi tiết</Form.Label>
                            <Form.Control as="textarea" rows={3} value={currentService.description} onChange={e => setCurrentService({ ...currentService, description: e.target.value })} />
                        </Form.Group>
                        {currentService.id && (
                            <Form.Check type="switch" label="Trạng thái hoạt động" checked={currentService.is_active} onChange={e => setCurrentService({ ...currentService, is_active: e.target.checked })} />
                        )}
                    </Modal.Body>
                    <Modal.Footer>
                        <Button variant="primary" type="submit">Lưu dữ liệu</Button>
                    </Modal.Footer>
                </Form>
            </Modal>
        </Container>
    );
};

export default AdminService;
