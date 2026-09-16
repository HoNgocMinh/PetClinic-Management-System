import React, { useEffect, useState } from "react";
import { Container, Table, Badge, Spinner, Tab, Tabs, Card, Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import moment from "moment";
import { authApis, endpoint } from "../../configs/Apis";
import MedicalRecordDetailModal from "../../component/MedicalRecordDetailModal";

const MyAppointments = () => {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showViewDetail, setShowViewDetail] = useState(false);
    const [selectedRecordId, setSelectedRecordId] = useState(null);
    const navigate = useNavigate();

    const loadAppointments = async () => {
        try {
            setLoading(true);
            const res = await authApis().get(endpoint['appointments']);
            setAppointments(res.data.data || res.data);
        } catch (ex) {
            toast.error("Không thể tải danh sách lịch hẹn.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadAppointments();
    }, []);

    const getStatusBadge = (status) => {
        switch (status) {
            case "PENDING": return <Badge bg="warning" text="dark">Chờ xác nhận</Badge>;
            case "CONFIRMED": return <Badge bg="success">Đã xác nhận</Badge>;
            case "CHECKED_IN": return <Badge bg="info">Đã đến phòng khám</Badge>;
            case "IN_PROGRESS": return <Badge bg="primary">Đang khám</Badge>;
            case "WAITING_PAYMENT": return <Badge style={{ backgroundColor: "#f97316", color: "#fff" }}>Chờ thanh toán</Badge>;
            case "COMPLETED": return <Badge bg="success">Hoàn thành</Badge>;
            case "CANCELLED": return <Badge bg="danger">Đã hủy</Badge>;
            case "NO_SHOW": return <Badge bg="dark">Vắng mặt</Badge>;
            default: return <Badge bg="light" text="dark">{status}</Badge>;
        }
    };

    const handleCancel = async (appId) => {
        if (window.confirm("Bạn có chắc chắn muốn hủy lịch hẹn này?")) {
            try {
                await authApis().delete(endpoint['appointment_detail'](appId));
                toast.success("Đã hủy lịch hẹn.");
                loadAppointments();
            } catch (ex) {
                toast.error(ex.response?.data?.message || "Không thể hủy lịch.");
            }
        }
    };

    const handleViewRecord = (recordId) => {
        setSelectedRecordId(recordId);
        setShowViewDetail(true);
    };

    const handlePay = (paymentId) => {
        if (!paymentId) {
            toast.error("Chưa tìm thấy thông tin thanh toán.");
            return;
        }
        navigate(`/payments/${paymentId}/checkout`);
    };

    const renderTable = (data) => (
        <Table responsive hover className="mt-3 align-middle">
            <thead className="table-light">
                <tr>
                    <th>Thú cưng</th>
                    <th>Phòng khám</th>
                    <th>Dịch vụ</th>
                    <th>Thời gian</th>
                    <th>Trạng thái</th>
                    <th>Hành động</th>
                </tr>
            </thead>
            <tbody>
                {data.map((app) => (
                    <tr key={app.id}>
                        <td className="fw-bold">{app.pet_name}</td>
                        <td>{app.clinic_name}</td>
                        <td>{app.service_name}</td>
                        <td>{moment(app.appointment_time).format("DD/MM/YYYY HH:mm")}</td>
                        <td>{getStatusBadge(app.status)}</td>
                        <td>
                            {app.status === "PENDING" && (
                                <Button variant="outline-danger" size="sm" onClick={() => handleCancel(app.id)}>
                                    Hủy
                                </Button>
                            )}
                            {app.status === "WAITING_PAYMENT" && (
                                <Button
                                    variant="warning"
                                    size="sm"
                                    className="text-white"
                                    onClick={() => handlePay(app.payment?.id)}
                                >
                                    Thanh toán
                                </Button>
                            )}
                            {app.status === "COMPLETED" && app.medical_record_id && (
                                <Button
                                    variant="outline-primary"
                                    size="sm"
                                    onClick={() => handleViewRecord(app.medical_record_id)}
                                >
                                    Xem hồ sơ
                                </Button>
                            )}
                        </td>
                    </tr>
                ))}
            </tbody>
        </Table>
    );

    if (loading) {
        return (
            <Container className="text-center mt-5">
                <Spinner animation="border" variant="success" />
            </Container>
        );
    }

    return (
        <Container className="mt-4 mb-5">
            <h2 className="mb-4 text-success fw-bold">Lịch hẹn của tôi</h2>

            <Tabs defaultActiveKey="all" className="mb-3 custom-tabs">
                <Tab eventKey="all" title="Tất cả">
                    {renderTable(appointments)}
                </Tab>
                <Tab eventKey="upcoming" title="Sắp tới">
                    {renderTable(appointments.filter(app => ["PENDING", "CONFIRMED", "WAITING_PAYMENT"].includes(app.status)))}
                </Tab>
                <Tab eventKey="finished" title="Đã xong/Hủy">
                    {renderTable(appointments.filter(app => ["COMPLETED", "CANCELLED", "NO_SHOW"].includes(app.status)))}
                </Tab>
            </Tabs>

            {appointments.length === 0 && (
                <Card className="text-center p-5 border-0 bg-light">
                    <p className="text-muted">Bạn chưa có lịch hẹn nào.</p>
                </Card>
            )}
            <MedicalRecordDetailModal
                recordId={selectedRecordId}
                show={showViewDetail}
                onHide={() => setShowViewDetail(false)}
                isOwner={true}
            />
        </Container>
    );
};

export default MyAppointments;
