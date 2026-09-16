import React, { useEffect, useState } from "react";
import { Container, Table, Button, Form, Modal, Badge, Card, Spinner, Row, Col } from "react-bootstrap";
import { authApis, endpoint } from "../../configs/Apis";
import toast from "react-hot-toast";

const MedicineManagement = () => {
    const [medicines, setMedicines] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showUpdateModal, setShowUpdateModal] = useState(false);
    const [selectedMedicine, setSelectedMedicine] = useState(null);
    const [newQuantity, setNewQuantity] = useState(0);
    const [showAddModal, setShowAddModal] = useState(false);
    const [newMedicine, setNewMedicine] = useState({
        name: "",
        unit: "",
        description: "",
        stock_quantity: 0,
        price: 0
    });
    const handleAddChange = (e) => {
        const { name, value } = e.target;
        setNewMedicine(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleAddMedicine = async (e) => {
        e.preventDefault();
        try {
            // Kiểm tra validate cơ bản trước khi gửi
            if (!newMedicine.name.trim() || !newMedicine.unit.trim()) {
                toast.error("Tên thuốc và đơn vị không được để trống.");
                return;
            }

            await authApis().post(endpoint['medicines'], newMedicine);
            toast.success("Thêm thuốc mới thành công!");

            // Reset form và đóng modal
            setNewMedicine({ name: "", unit: "", description: "", stock_quantity: 0, price: 0 });
            setShowAddModal(false);
            loadMedicines(); // Tải lại danh sách
        } catch (ex) {
            const errorMsg = ex.response?.data?.message || "Không thể thêm thuốc mới.";
            toast.error(errorMsg);
        }
    };

    const loadMedicines = async () => {
        try {
            setLoading(true);
            const res = await authApis().get(endpoint['medicines']);
            setMedicines(res.data.data || res.data);
        } catch (ex) {
            toast.error("Không thể tải danh sách thuốc.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadMedicines();
    }, []);

    const handleOpenUpdate = (med) => {
        setSelectedMedicine(med);
        setNewQuantity(0); // Mặc định số lượng nhập thêm là 0
        setShowUpdateModal(true);
    };

    const handleUpdateStock = async () => {
        if (newQuantity <= 0) {
            toast.error("Vui lòng nhập số lượng hợp lệ.");
            return;
        }
        try {
            // Backend PATCH hoặc PUT vào medicines/{id}/ để cập nhật stock_quantity
            const updatedStock = selectedMedicine.stock_quantity + parseInt(newQuantity);
            await authApis().patch(endpoint['medicine_detail'](selectedMedicine.id), {
                stock_quantity: updatedStock
            });
            toast.success(`Đã cập nhật kho cho ${selectedMedicine.name}`);
            setShowUpdateModal(false);
            loadMedicines();
        } catch (ex) {
            toast.error("Cập nhật thất bại.");
        }
    };

    if (loading) return <Container className="text-center mt-5"><Spinner animation="border" variant="primary" /></Container>;

    return (
        <Container className="mt-4">
            <Row className="mb-4 align-items-center">
                <Col>
                    <h2 className="text-primary fw-bold">QUẢN LÝ KHO THUỐC</h2>
                </Col>
                <Col className="text-end">
                    <Button variant="primary" className="me-2" onClick={() => setShowAddModal(true)}>
                        <i className="bi bi-plus-circle me-1"></i> Thêm thuốc mới
                    </Button>
                    <Button variant="success" onClick={loadMedicines}>Làm mới</Button>
                </Col>
            </Row>
            {/* MODAL THÊM THUỐC MỚI */}
            <Modal show={showAddModal} onHide={() => setShowAddModal(false)} size="lg" centered>
                <Modal.Header closeButton className="bg-primary text-white">
                    <Modal.Title>Thêm Thuốc Mới Vào Kho</Modal.Title>
                </Modal.Header>
                <Form onSubmit={handleAddMedicine}>
                    <Modal.Body>
                        <Row>
                            <Col md={8}>
                                <Form.Group className="mb-3">
                                    <Form.Label className="fw-bold">Tên thuốc</Form.Label>
                                    <Form.Control
                                        type="text"
                                        name="name"
                                        placeholder="Ví dụ: Paracetamol 500mg"
                                        value={newMedicine.name}
                                        onChange={handleAddChange}
                                        required
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label className="fw-bold">Đơn vị</Form.Label>
                                    <Form.Control
                                        type="text"
                                        name="unit"
                                        placeholder="Viên, Chai, Gói..."
                                        value={newMedicine.unit}
                                        onChange={handleAddChange}
                                        required
                                    />
                                </Form.Group>
                            </Col>
                        </Row>

                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label className="fw-bold">Số lượng nhập kho ban đầu</Form.Label>
                                    <Form.Control
                                        type="number"
                                        name="stock_quantity"
                                        min="0"
                                        value={newMedicine.stock_quantity}
                                        onChange={handleAddChange}
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label className="fw-bold">Đơn giá (VNĐ)</Form.Label>
                                    <Form.Control
                                        type="number"
                                        name="price"
                                        min="0"
                                        value={newMedicine.price}
                                        onChange={handleAddChange}
                                    />
                                </Form.Group>
                            </Col>
                        </Row>

                        <Form.Group className="mb-3">
                            <Form.Label className="fw-bold">Mô tả / Ghi chú</Form.Label>
                            <Form.Control
                                as="textarea"
                                rows={3}
                                name="description"
                                placeholder="Cách dùng, thành phần hoặc lưu ý bảo quản..."
                                value={newMedicine.description}
                                onChange={handleAddChange}
                            />
                        </Form.Group>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button variant="secondary" onClick={() => setShowAddModal(false)}>Hủy</Button>
                        <Button variant="primary" type="submit">Lưu thông tin</Button>
                    </Modal.Footer>
                </Form>
            </Modal>

            <Card className="border-0 shadow-sm">
                <Table responsive hover className="align-middle mb-0">
                    <thead className="bg-light">
                        <tr>
                            <th>ID</th>
                            <th>Tên thuốc</th>
                            <th>Đơn vị</th>
                            <th>Đơn giá (VNĐ)</th>
                            <th>Tồn kho</th>
                            <th>Trạng thái</th>
                            <th>Thao tác</th>
                        </tr>
                    </thead>
                    <tbody>
                        {medicines.map(med => (
                            <tr key={med.id}>
                                <td>#{med.id}</td>
                                <td className="fw-bold">{med.name}</td>
                                <td>{med.unit}</td>
                                <td>{Number(med.price).toLocaleString('vi-VN')}</td>                                <td>
                                    <span className={med.stock_quantity < 10 ? "text-danger fw-bold" : ""}>
                                        {med.stock_quantity}
                                    </span>
                                </td>
                                <td>
                                    {med.stock_quantity > 10 ? (
                                        <Badge bg="success">Còn hàng</Badge>
                                    ) : med.stock_quantity > 0 ? (
                                        <Badge bg="warning" text="dark">Sắp hết</Badge>
                                    ) : (
                                        <Badge bg="danger">Hết hàng</Badge>
                                    )}
                                </td>
                                <td>
                                    <Button size="sm" variant="outline-primary" onClick={() => handleOpenUpdate(med)}>
                                        Nhập hàng
                                    </Button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </Table>
            </Card>

            {/* Modal Nhập thêm thuốc */}
            <Modal show={showUpdateModal} onHide={() => setShowUpdateModal(false)} centered>
                <Modal.Header closeButton>
                    <Modal.Title>Nhập thêm: {selectedMedicine?.name}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form.Group>
                        <Form.Label>Số lượng tồn hiện tại: <strong>{selectedMedicine?.stock_quantity}</strong></Form.Label>
                        <Form.Control
                            type="number"
                            placeholder="Nhập số lượng muốn thêm..."
                            value={newQuantity}
                            onChange={(e) => setNewQuantity(e.target.value)}
                        />
                        <Form.Text className="text-muted">
                            Tổng tồn kho mới sẽ là: {selectedMedicine?.stock_quantity + (parseInt(newQuantity) || 0)}
                        </Form.Text>
                    </Form.Group>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={() => setShowUpdateModal(false)}>Hủy</Button>
                    <Button variant="primary" onClick={handleUpdateStock}>Xác nhận nhập</Button>
                </Modal.Footer>
            </Modal>
        </Container>
    );
};

export default MedicineManagement;
