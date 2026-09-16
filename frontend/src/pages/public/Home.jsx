import { Col, Container, Row, Card, Button } from "react-bootstrap";
import { useLocation, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { FaStethoscope, FaSyringe, FaHospital, FaVial, FaCut, FaPaw } from 'react-icons/fa';

// Nhớ đảm bảo bạn có ảnh ở đường dẫn: src/assets/images/hero-image.png
import HeroPhoto from "../../assets/images/hero-image.png"; 
import "./styles/Home.css"; 

const Home = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [message, setMessage] = useState(location.state?.message || "");

    const services = [
        { id: 1, title: "Khám tổng quát", desc: "Thăm khám, chẩn đoán và điều trị bệnh lý", icon: <FaStethoscope size={40} /> },
        { id: 2, title: "Tiêm phòng", desc: "Tiêm vaccine và tẩy giun định kỳ", icon: <FaSyringe size={40} /> },
        { id: 3, title: "Phẫu thuật", desc: "Phẫu thuật triệt sản, ngoại khoa an toàn", icon: <FaHospital size={40} /> },
        { id: 4, title: "Xét nghiệm", desc: "Xét nghiệm máu, siêu âm, X-quang", icon: <FaVial size={40} /> },
        { id: 5, title: "Spa & Grooming", desc: "Tắm gội, cắt tỉa lông và vệ sinh toàn diện", icon: <FaCut size={40} /> },
        { id: 6, title: "Lưu trú", desc: "Chăm sóc nội trú nội trú khi chủ vắng nhà", icon: <FaPaw size={40} /> },
    ];

    useEffect(() => {
        if (message) {
            const timer = setTimeout(() => {
                setMessage("");
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [message]);

    return (
        <>
            <div className="hero-banner py-5 bg-dog-tan">
                <Container>
                    <Row className="align-items-center">
                        <Col md={6} className="mb-4 mb-md-0 hero-text-block">
                            <h1 className="display-4 fw-bold text-uppercase mb-4">
                                Hệ thống chăm sóc<br/>thú y 2DEL
                            </h1>
                            <p className="lead mb-4 fw-normal">
                                Nơi tin cậy để thăm khám, chẩn đoán, điều trị nội trú và ngoại trú cho thú cưng.
                            </p>
                            <Button 
                                variant="dark" 
                                size="lg" 
                                className="px-5 py-2 rounded-pill fw-bold hero-btn-custom"
                                onClick={() => navigate('/booking')}
                            >
                                Đặt lịch ngay
                            </Button>
                        </Col>

                        <Col md={6} className="text-center text-md-end">
                            <img 
                                src={HeroPhoto} 
                                alt="Thú y 2DEL - Chăm sóc thú cưng" 
                                className="img-fluidrounded"
                                style={{ 
                                    maxWidth: '100%', 
                                    height: 'auto',
                                    filter: 'drop-shadow(0px 0px 10px rgba(0, 0, 0, 0.1))' 
                                }}
                            />
                        </Col>
                    </Row>
                </Container>
            </div>

            <div className="py-5">
                <Container>
                    <h2 className="text-center mb-5 section-title fw-bold text-dog-brown">Dịch vụ của chúng tôi</h2>
                    <Row xs={1} sm={2} md={3} className="g-4">
                        {services.map((service) => (
                            <Col key={service.id}>
                                <Card className="h-100 text-center service-card shadow-sm border-0 bg-dog-cream">
                                    <Card.Body className="p-4">
                                        <div className="service-icon mb-3 text-active">
                                            {service.icon}
                                        </div>
                                        <Card.Title className="fw-bold mb-3">{service.title}</Card.Title>
                                        <Card.Text className="text-muted">
                                            {service.desc}
                                        </Card.Text>
                                    </Card.Body>
                                </Card>
                            </Col>
                        ))}
                    </Row>
                </Container>
            </div>
        </>
    );
};

export default Home;
