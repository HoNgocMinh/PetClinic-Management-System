import React, { useEffect, useState } from "react";
import { Container, Table, Button, Badge, Spinner, Card } from "react-bootstrap";
import { authApis, endpoint } from "../../configs/Apis";
import toast from "react-hot-toast";
import moment from "moment";
import ExaminationForm from "../../component/ExaminationForm";
import MedicalRecordDetailModal from "../../component/MedicalRecordDetailModal";

const StaffAppointmentList = () => {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showViewDetail, setShowViewDetail] = useState(false);
    const [selectedRecordId, setSelectedRecordId] = useState(null);

    const [selectedApp, setSelectedApp] = useState(null);
    const [showExam, setShowExam] = useState(false);

    const loadAppointments = async () => {
        try {
            setLoading(true);
            const res = await authApis().get(endpoint['staff_clinic_appointments']);
            const data = res.data.data || res.data;
            setAppointments(
                [...data].sort((a, b) => new Date(b.appointment_time) - new Date(a.appointment_time))
            );
        } catch (ex) {
            toast.error("Không thể tải danh sách lịch hẹn của phòng khám.");
        } finally {
            setLoading(false);
        }
    };



    useEffect(() => {
        loadAppointments();
    }, []);

    const updateStatus = async (id, actionEndpoint, successMsg) => {
        try {
            await authApis().post(actionEndpoint(id));
            toast.success(successMsg);
            loadAppointments();
        } catch (ex) {
            toast.error(ex.response?.data?.message || "Thao tác thất bại");
        }
    };

    const getStatusBadge = (status) => {
        const statusMap = {
            "PENDING": { bg: "warning", text: "Chờ duyệt" },
            "CONFIRMED": { bg: "success", text: "Đã xác nhận" },
            "CHECKED_IN": { bg: "info", text: "Đã đến" },
            "IN_PROGRESS": { bg: "primary", text: "Đang khám" },
            "WAITING_PAYMENT": { bg: "payment", text: "Chờ thanh toán" },
            "COMPLETED": { bg: "success", text: "Hoàn thành" },
            "CANCELLED": { bg: "danger", text: "Đã hủy" },
            "NO_SHOW": { bg: "dark", text: "Vắng mặt" }
        };
        const s = statusMap[status] || { bg: "light", text: status };
        if (s.bg === "payment") {
            return <Badge style={{ backgroundColor: "#f97316", color: "#fff" }}>{s.text}</Badge>;
        }
        return <Badge bg={s.bg}>{s.text}</Badge>;
    };

    const handleViewRecord = async (appId) => {
        try {
            const res = await authApis().get(endpoint['appointment_medical_record'](appId));
            const record = res.data.data || res.data;
            setSelectedRecordId(record.id);
            setShowViewDetail(true);
        } catch (ex) {
            toast.error("Không tìm thấy hồ sơ cho lịch hẹn này.");
        }
    };

    if (loading) return <Container className="text-center mt-5"><Spinner animation="border" /></Container>;

    return (
        <Container className="mt-4">
            <h2 className="mb-4 fw-bold text-primary">QUẢN LÝ LỊCH HẸN PHÒNG KHÁM</h2>
            <Card className="shadow-sm border-0">
                <Table responsive hover className="mb-0 align-middle">
                    <thead className="table-primary">
                        <tr>
                            <th>Khách hàng</th>
                            <th>Thú cưng</th>
                            <th>Dịch vụ</th>
                            <th>Thời gian</th>
                            <th>Trạng thái</th>
                            <th>Thao tác</th>
                        </tr>
                    </thead>
                    <tbody>
                        {appointments.map(app => (
                            <tr key={app.id}>
                                <td>{app.owner_full_name || app.owner_username}</td>
                                <td>{app.pet_name}</td>
                                <td>{app.service_name}</td>
                                <td>{moment(app.appointment_time).format("DD/MM HH:mm")}</td>
                                <td>{getStatusBadge(app.status)}</td>
                                <td>
                                    {app.status === "PENDING" && (
                                        <>
                                            <Button size="sm" variant="success" className="me-2"
                                                onClick={() => updateStatus(app.id, endpoint['appointment_confirm'], "Đã xác nhận")}>
                                                Xác nhận
                                            </Button>

                                        </>
                                    )}

                                    {app.status === "CONFIRMED" && (
                                        <>
                                            <Button size="sm" variant="info" className="me-2 text-white"
                                                onClick={() => updateStatus(app.id, endpoint['appointment_check_in'], "Đã check-in")}>
                                                Tiếp đón
                                            </Button>
                                            <Button size="sm" variant="outline-dark"
                                                onClick={() => updateStatus(app.id, endpoint['appointment_no_show'], "Đã đánh dấu vắng mặt")}>
                                                Vắng mặt
                                            </Button>
                                        </>
                                    )}

                                    {app.status === "CHECKED_IN" && (
                                        <Button size="sm" variant="primary"
                                            onClick={() => updateStatus(app.id, endpoint['appointment_start'], "Bắt đầu ca khám")}>
                                            Bắt đầu khám
                                        </Button>
                                    )}

                                    {app.status === "IN_PROGRESS" && (
                                        <Button size="sm" variant="outline-primary" onClick={() => {
                                            setSelectedApp(app);
                                            setShowExam(true);
                                        }}>
                                            Nhập kết quả
                                        </Button>
                                    )}

                                    {app.status === "COMPLETED" && (
                                        <Button size="sm" variant="info" className="text-white" onClick={() => handleViewRecord(app.id)}>
                                            Xem hồ sơ
                                        </Button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </Table>
            </Card>

            <MedicalRecordDetailModal
                recordId={selectedRecordId}
                show={showViewDetail}
                onHide={() => setShowViewDetail(false)}
            />

            {selectedApp && (
                <ExaminationForm
                    appointment={selectedApp}
                    show={showExam}
                    onHide={() => setShowExam(false)}
                    onComplete={loadAppointments}
                />
            )}
        </Container>
    );
};

export default StaffAppointmentList;
