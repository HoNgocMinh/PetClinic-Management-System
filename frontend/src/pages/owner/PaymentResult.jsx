import { Button, Card, Col, Container, Row, Spinner } from "react-bootstrap";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import Apis, { endpoint } from "../../configs/Apis";

const PaymentResult = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const [verifying, setVerifying] = useState(true);
    const [verifiedSuccess, setVerifiedSuccess] = useState(false);

    const rawSuccess = useMemo(
        () => searchParams.get("vnp_ResponseCode") === "00",
        [searchParams],
    );

    useEffect(() => {
        const verifyPayment = async () => {
            try {
                const params = Object.fromEntries(searchParams.entries());
                const res = await Apis.get(endpoint['payment_vnpay_return'], { params });
                setVerifiedSuccess(Boolean(res.data.data?.is_success));
            } catch (ex) {
                setVerifiedSuccess(false);
            } finally {
                setVerifying(false);
            }
        };

        verifyPayment();
    }, [searchParams]);

    const isSuccess = !verifying && verifiedSuccess;

    return (
        <Container className="py-5">
            <Row className="justify-content-center">
                <Col md={8} lg={6}>
                    <Card className="payment-result-card text-center border-0 shadow-sm">
                        <Card.Body className="p-5">
                            {verifying ? (
                                <>
                                    <Spinner animation="border" variant="success" className="mb-4" />
                                    <h2 className="fw-bold mb-3">Đang xác nhận thanh toán</h2>
                                    <p className="text-muted mb-0">
                                        Hệ thống đang kiểm tra kết quả giao dịch từ VNPAY.
                                    </p>
                                </>
                            ) : (
                                <>
                                    <div className={`payment-result-icon ${isSuccess ? "success" : "failed"}`}>
                                        {isSuccess ? "✓" : "!"}
                                    </div>
                                    <h2 className={`fw-bold mb-3 ${isSuccess ? "text-success" : "text-danger"}`}>
                                        {isSuccess ? "Thanh toán thành công" : "Thanh toán chưa hoàn tất"}
                                    </h2>
                                    <p className="text-muted mb-4">
                                        {isSuccess
                                            ? "Cảm ơn bạn. Lịch hẹn của bạn đã được cập nhật sang trạng thái Hoàn thành."
                                            : rawSuccess
                                                ? "VNPAY trả về thành công nhưng hệ thống chưa xác nhận được giao dịch. Vui lòng kiểm tra lại lịch hẹn sau ít phút."
                                                : "Giao dịch chưa được hoàn tất hoặc đã bị hủy. Bạn có thể quay lại lịch hẹn để thanh toán lại."}
                                    </p>
                                    <div className="d-flex flex-column flex-sm-row gap-3 justify-content-center">
                                        <Button variant="success" className="px-4" onClick={() => navigate("/")}>
                                            Trang chủ
                                        </Button>
                                        <Button variant="outline-primary" className="px-4" onClick={() => navigate("/appointments")}>
                                            Lịch hẹn của tôi
                                        </Button>
                                    </div>
                                </>
                            )}
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default PaymentResult;
