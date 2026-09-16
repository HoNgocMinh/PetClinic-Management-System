import { useEffect, useState, useRef } from "react";
import { Container, Row, Col, Card, Button, Modal, Form, FloatingLabel } from "react-bootstrap";
import { authApis, endpoint } from "../../configs/Apis";
import MySpinner from "../../component/layout/MySpinner";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";

import dogAvatar from "../../assets/images/dog-placeholder.png";
import catAvatar from "../../assets/images/cat-placeholder.png";
import otherAvatar from "../../assets/images/other-pet-placeholder.png";


const Pet = () => {
    const navigate = useNavigate();
    const DEFAULT_AVATARS = {
        DOG: dogAvatar,
        CAT: catAvatar,
        OTHER: otherAvatar
    };
    const formatDate = (dateString) => {
        if (!dateString) return "Chưa cập nhật";
        const [year, month, day] = dateString.split("-");
        return `${day}-${month}-${year}`;
    };

    const [pets, setPets] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showModal, setShowModal] = useState(false);
    const [newPet, setNewPet] = useState({
        name: "",
        species: "DOG", 
        breed: "",
        gender: "MALE",
        birth_date: "",
        weight: "",
        note: ""
    });

    const loadPets = async () => {
        try {
            setLoading(true);
            let res = await authApis().get(endpoint['pets']);

            console.log("Dữ liệu Pets trả về:", res.data); 

            const data = res.data.data || res.data;

            if (Array.isArray(data)) {
                setPets(data);
            } else {
                console.error("Dữ liệu không phải mảng:", data);
                setPets([]);
            }
        } catch (ex) {
            console.error(ex);
            toast.error("Không thể tải danh sách thú cưng");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadPets();
    }, []);

    // 2. Xử lý thêm thú cưng mới
    const addPet = async (e) => {
        e.preventDefault();

        try {
            setLoading(true);
            await authApis().post(endpoint['pets'], newPet);

            toast.success("Thêm thú cưng thành công!");
            setShowModal(false);
            loadPets();
        } catch (ex) {
            console.error(ex);
            const errorData = ex.response?.data;

            if (errorData && errorData.errors) {
                const fields = Object.keys(errorData.errors);
                const firstError = errorData.errors[fields[0]][0];
                toast.error(firstError);
            } else {
                toast.error("Đã có lỗi xảy ra. Vui lòng thử lại!");
            }
        } finally {
            setLoading(false);
        }
    }


    return (
        <Container className="mt-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h2 className="text-success fw-bold">THÚ CƯNG CỦA TÔI</h2>
                <Button variant="primary" onClick={() => setShowModal(true)}>+ Thêm Thú Cưng</Button>
            </div>

            {loading && <MySpinner />}
            <Row>
                {Array.isArray(pets) && pets.length > 0 ? (
                    pets.map(p => (
                        <Col key={p.id} md={4} className="mb-4">
                        </Col>
                    ))
                ) : (
                    <Col className="text-center mt-5">
                        <p className="text-muted">Bạn chưa có thú cưng nào. Hãy thêm mới nhé!</p>
                    </Col>
                )}
            </Row>
            <Row>
                {pets.map(p => (
                    <Col key={p.id} md={4} className="mb-4">
                        <Card className="shadow-sm h-100">
                            <Card.Img
                                variant="top"
                                src={DEFAULT_AVATARS[p.species] || DEFAULT_AVATARS.OTHER}
                                alt={p.name}
                                style={{ height: "200px", objectFit: "cover", backgroundColor: "#f8f9fa" }}
                            />
                            <Card.Body>
                                <Card.Title className="fw-bold text-primary">{p.name}</Card.Title>

                                <Card.Text as="div">
                                    <div className="mb-1">
                                        <b>Loài:</b> {p.species === 'DOG' ? 'Chó' : p.species === 'CAT' ? 'Mèo' : 'Khác'}
                                    </div>
                                    <div className="mb-1">
                                        <b>Giới tính:</b> {p.gender === 'MALE' ? 'Đực' : 'Cái'}
                                    </div>
                                    <div className="mb-1">
                                        <b>Ngày sinh:</b> {formatDate(p.birth_date) || "Chưa cập nhật"}
                                    </div>
                                    {p.weight && (
                                        <div className="mb-1">
                                            <b>Cân nặng:</b> {p.weight} kg
                                        </div>
                                    )}
                                </Card.Text>

                                <Button
                                    variant="outline-success"
                                    size="sm"
                                    className="w-100 mt-2"
                                    onClick={() => navigate(`/my-pets/${p.id}/history`)}
                                >
                                    Xem hồ sơ y tế
                                </Button>
                            </Card.Body>
                        </Card>
                    </Col>
                ))}
            </Row>

            <Modal show={showModal} onHide={() => setShowModal(false)} centered>
                <Modal.Header closeButton>
                    <Modal.Title>Đăng ký thú cưng mới</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form onSubmit={addPet}>
                        <FloatingLabel label="Tên thú cưng" className="mb-3">
                            <Form.Control type="text" required value={newPet.name}
                                onChange={e => setNewPet({ ...newPet, name: e.target.value })} />
                        </FloatingLabel>

                        <Row className="mb-3">
                            <Col md={6}>
                                <Form.Group>
                                    <Form.Label className="small fw-bold">Loài</Form.Label>
                                    <Form.Select value={newPet.species}
                                        onChange={e => setNewPet({ ...newPet, species: e.target.value })}>
                                        <option value="DOG">Chó (Dog)</option>
                                        <option value="CAT">Mèo (Cat)</option>
                                        <option value="OTHER">Khác (Other)</option>
                                    </Form.Select>
                                </Form.Group>
                            </Col>
                            <Col md={6}>
                                <Form.Group>
                                    <Form.Label className="small fw-bold">Giới tính</Form.Label>
                                    <Form.Select value={newPet.gender}
                                        onChange={e => setNewPet({ ...newPet, gender: e.target.value })}>
                                        <option value="MALE">Đực (Male)</option>
                                        <option value="FEMALE">Cái (Female)</option>
                                    </Form.Select>
                                </Form.Group>
                            </Col>
                        </Row>

                        <FloatingLabel label="Giống (Ví dụ: Poodle, Chihuahua...)" className="mb-3">
                            <Form.Control type="text" value={newPet.breed}
                                onChange={e => setNewPet({ ...newPet, breed: e.target.value })} />
                        </FloatingLabel>

                        <Row className="mb-3">
                            <Col md={6}>
                                <FloatingLabel label="Ngày sinh">
                                    <Form.Control type="date" value={newPet.birth_date}
                                        onChange={e => setNewPet({ ...newPet, birth_date: e.target.value })} />
                                </FloatingLabel>
                            </Col>
                            <Col md={6}>
                                <FloatingLabel label="Cân nặng (kg)">
                                    <Form.Control type="number" step="0.1" value={newPet.weight}
                                        onChange={e => setNewPet({ ...newPet, weight: e.target.value })} />
                                </FloatingLabel>
                            </Col>
                        </Row>

                        <FloatingLabel label="Ghi chú sức khỏe" className="mb-3">
                            <Form.Control as="textarea" style={{ height: '80px' }} value={newPet.note}
                                onChange={e => setNewPet({ ...newPet, note: e.target.value })} />
                        </FloatingLabel>


                        <Button type="submit" variant="success" className="w-100 py-2 fw-bold" disabled={loading}>
                            {loading ? <MySpinner /> : "XÁC NHẬN THÊM"}
                        </Button>
                    </Form>
                </Modal.Body>
            </Modal>
        </Container>
    );
}

export default Pet;
