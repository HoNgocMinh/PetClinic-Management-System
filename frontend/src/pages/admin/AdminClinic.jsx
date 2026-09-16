import React, { useEffect, useState } from "react";
import { Container, Table, Button, Modal, Form, Card, Spinner } from "react-bootstrap";
import { authApis, endpoint } from "../../configs/Apis";
import toast from "react-hot-toast";

const initialClinic = { 
    name: "", 
    address: "", 
    phone: "",   
    email: "", 
    is_active: true 
};

const AdminClinic = () => {
    const [clinics, setClinics] = useState([]);
    const [show, setShow] = useState(false);
    const [loading, setLoading] = useState(false);
    const [currentClinic, setCurrentClinic] = useState(initialClinic);
    
    const loadClinics = async () => {
        try {
            setLoading(true);
            const res = await authApis().get(endpoint['clinics']);
            const data = res.data.data || res.data;
            setClinics(Array.isArray(data) ? data : []);
        } catch (ex) {
            toast.error("Không thể tải danh sách phòng khám");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { loadClinics(); }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const payload = {
                name: currentClinic.name,
                address: currentClinic.address,
                phone: currentClinic.phone,
                email: currentClinic.email
            };

            if (currentClinic.id) {
                await authApis().put(`${endpoint['clinics']}${currentClinic.id}/`, payload);
                toast.success("Cập nhật phòng khám thành công");
            } else {
                await authApis().post(endpoint['clinics'], payload);
                toast.success("Thêm phòng khám mới thành công");
            }
            setShow(false);
            loadClinics();
        } catch (ex) {
            toast.error(ex.response?.data?.message || "Thao tác thất bại");
        }
    };

    // Chức năng xóa mềm theo API
    const handleDelete = async (id) => {
        if (window.confirm("Bạn có chắc chắn muốn xóa phòng khám này?")) {
            try {
                await authApis().delete(`${endpoint['clinics']}${id}/`);
                toast.success("Xóa phòng khám thành công");
                loadClinics();
            } catch (ex) {
                toast.error("Không thể xóa phòng khám");
            }
        }
    };

    return (
        <Container className="mt-4">
            <Card className="shadow-sm border-0">
                <Card.Header className="bg-primary text-white d-flex justify-content-between align-items-center py-3">
                    <h5 className="mb-0 fw-bold">QUẢN LÝ DANH SÁCH PHÒNG KHÁM</h5>
                    <Button variant="light" size="sm" className="fw-bold" onClick={() => { setCurrentClinic(initialClinic); setShow(true); }}>
                        + THÊM CHI NHÁNH
                    </Button>
                </Card.Header>
                <Card.Body>
                    {loading && clinics.length === 0 ? (
                        <div className="text-center my-5"><Spinner animation="border" variant="primary" /></div>
                    ) : (
                        <Table responsive hover className="align-middle">
                            <thead className="table-light">
                                <tr>
                                  
                                    <th>Tên phòng khám</th>
                                    <th>Địa chỉ</th>
                                    <th>Liên hệ (Phone/Email)</th>
                                    <th className="text-center">Thao tác</th>
                                </tr>
                            </thead>
                            <tbody>
                                {clinics.map(c => (
                                    <tr key={c.id}>
                                      
                                        <td className="fw-bold text-primary">{c.name}</td>
                                        <td>{c.address}</td>
                                        <td>
                                            <div>{c.phone}</div>
                                            <small className="text-muted">{c.email}</small>
                                        </td>
                                        <td className="text-center">
                                            <Button variant="outline-warning" size="sm" className="me-2" 
                                                onClick={() => { setCurrentClinic(c); setShow(true); }}>
                                                Sửa
                                            </Button>
                                            <Button variant="outline-danger" size="sm" 
                                                onClick={() => handleDelete(c.id)}>
                                                Xóa
                                            </Button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    )}
                </Card.Body>
            </Card>

            <Modal show={show} onHide={() => setShow(false)} centered>
                <Modal.Header closeButton className="bg-light">
                    <Modal.Title className="h6 fw-bold">{currentClinic.id ? "CẬP NHẬT CHI NHÁNH" : "THÊM CHI NHÁNH MỚI"}</Modal.Title>
                </Modal.Header>
                <Form onSubmit={handleSubmit}>
                    <Modal.Body>
                        <Form.Group className="mb-3">
                            <Form.Label className="small fw-bold">Tên phòng khám</Form.Label>
                            <Form.Control type="text" value={currentClinic.name || ""} 
                                onChange={(e) => setCurrentClinic({...currentClinic, name: e.target.value})} required />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label className="small fw-bold">Địa chỉ</Form.Label>
                            <Form.Control type="text" value={currentClinic.address || ""} 
                                onChange={(e) => setCurrentClinic({...currentClinic, address: e.target.value})} required />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label className="small fw-bold">Số điện thoại</Form.Label>
                            <Form.Control type="text" value={currentClinic.phone || ""} 
                                onChange={(e) => setCurrentClinic({...currentClinic, phone: e.target.value})} required />
                        </Form.Group>
                        <Form.Group className="mb-3">
                            <Form.Label className="small fw-bold">Email</Form.Label>
                            <Form.Control type="email" value={currentClinic.email || ""} 
                                onChange={(e) => setCurrentClinic({...currentClinic, email: e.target.value})} required />
                        </Form.Group>
                    </Modal.Body>
                    <Modal.Footer className="bg-light border-0">
                        <Button variant="link" className="text-decoration-none text-muted" onClick={() => setShow(false)}>Hủy</Button>
                        <Button variant="primary" type="submit" className="px-4">Lưu dữ liệu</Button>
                    </Modal.Footer>
                </Form>
            </Modal>
        </Container>
    );
};

export default AdminClinic;
