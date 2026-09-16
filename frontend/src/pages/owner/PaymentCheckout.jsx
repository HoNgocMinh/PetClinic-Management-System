import { Alert, Badge, Button, Card, Col, Container, ListGroup, Row, Spinner } from "react-bootstrap";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import moment from "moment";
import toast from "react-hot-toast";
import { authApis, endpoint } from "../../configs/Apis";

const formatCurrency = (value) => {
    const amount = Number(value || 0);
    return amount.toLocaleString("vi-VN", {
        style: "currency",
        currency: "VND",
    });
};

const PaymentCheckout = () => {
    const { paymentId } = useParams();
    const navigate = useNavigate();
    const [payment, setPayment] = useState(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);

    const canPay = useMemo(() => payment?.status === "PENDING", [payment]);

    useEffect(() => {
        const loadPayment = async () => {
            try {
                const res = await authApis().get(endpoint['payment_detail'](paymentId));
                setPayment(res.data.data || res.data);
            } catch (ex) {
                toast.error(ex.response?.data?.message || "Không thể tải thông tin thanh toán.");
            } finally {
                setLoading(false);
            }
        };

        loadPayment();
    }, [paymentId]);

    const handleConfirmPayment = async () => {
        try {
            setSubmitting(true);
            const res = await authApis().post(endpoint['payment_vnpay_create_url'](paymentId));
            const paymentUrl = res.data.data?.payment_url;
            if (!paymentUrl) {
                toast.error("Không tạo được liên kết thanh toán.");
                return;
            }
            window.location.href = paymentUrl;
        } catch (ex) {
            toast.error(ex.response?.data?.message || "Không thể tạo thanh toán VNPAY.");
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <Container className="text-center py-5">
                <Spinner animation="border" variant="success" />
            </Container>
        );
    }

    if (!payment) {
        return (
            <Container className="py-5">
                <Alert variant="danger">Không tìm thấy thông tin thanh toán.</Alert>
            </Container>
        );
    }

    return (
        <Container className="py-5">
            <Row className="justify-content-center">
                <Col lg={8}>
                    <div className="mb-4">
                        <h2 className="fw-bold text-success mb-2">Xác nhận thanh toán</h2>
                        <p className="text-muted mb-0">Vui lòng kiểm tra thông tin trước khi chuyển sang VNPAY.</p>
                    </div>

                    <Card className="border-0 shadow-sm payment-checkout-card">
                        <Card.Body className="p-4">
                            <div className="d-flex justify-content-between align-items-start gap-3 mb-4">
                                <div>
                                    <h5 className="fw-bold mb-1">Thông tin thanh toán</h5>
                                    <span className="text-muted">Phương thức thanh toán: VNPAY</span>
                                </div>
                                <Badge bg={canPay ? "warning" : "secondary"} text={canPay ? "dark" : undefined}>
                                    {canPay ? "Chờ thanh toán" : payment.status}
                                </Badge>
                            </div>

                            <ListGroup variant="flush" className="payment-checkout-list">
                                <ListGroup.Item className="d-flex justify-content-between px-0">
                                    <span className="text-muted">Thú cưng</span>
                                    <strong>{payment.pet_name}</strong>
                                </ListGroup.Item>
                                <ListGroup.Item className="d-flex justify-content-between px-0">
                                    <span className="text-muted">Dịch vụ</span>
                                    <strong>{payment.service_name}</strong>
                                </ListGroup.Item>
                                <ListGroup.Item className="d-flex justify-content-between px-0">
                                    <span className="text-muted">Phòng khám</span>
                                    <strong>{payment.clinic_name}</strong>
                                </ListGroup.Item>
                                <ListGroup.Item className="d-flex justify-content-between px-0">
                                    <span className="text-muted">Thời gian lịch hẹn</span>
                                    <strong>{moment(payment.appointment_time).format("DD/MM/YYYY HH:mm")}</strong>
                                </ListGroup.Item>
                                <ListGroup.Item className="d-flex justify-content-between align-items-center px-0 pt-4">
                                    <span className="fw-bold">Tổng thanh toán</span>
                                    <span className="payment-checkout-total">{formatCurrency(payment.amount)}</span>
                                </ListGroup.Item>
                            </ListGroup>

                            <div className="d-flex flex-column flex-sm-row gap-3 justify-content-end mt-4">
                                <Button variant="outline-secondary" onClick={() => navigate("/appointments")}>
                                    Quay lại
                                </Button>
                                <Button
                                    variant="success"
                                    disabled={!canPay || submitting}
                                    onClick={handleConfirmPayment}
                                >
                                    {submitting ? "Đang chuyển đến VNPAY..." : "Xác nhận thanh toán"}
                                </Button>
                            </div>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default PaymentCheckout;
