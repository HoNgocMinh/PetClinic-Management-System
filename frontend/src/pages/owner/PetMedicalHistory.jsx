import React, { useEffect, useState } from "react";
import { Container, Table, Button, Badge, Spinner, Card, Breadcrumb } from "react-bootstrap";
import { useParams, useNavigate } from "react-router-dom";
import { authApis, endpoint } from "../../configs/Apis";
import MedicalRecordDetailModal from "../../component/MedicalRecordDetailModal"; 
import moment from "moment";

const PetMedicalHistory = () => {
    const { petId } = useParams();
    const [records, setRecords] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedRecordId, setSelectedRecordId] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const nav = useNavigate();
    const isOwnerPath = window.location.pathname.includes('/my-pets/');

    useEffect(() => {
        const fetchHistory = async () => {
            setLoading(true);
            try {
                const apiPath = isOwnerPath
                    ? endpoint['owner_pet_medical_records'](petId)
                    : endpoint['pet_medical_records'](petId);

                console.log("Calling API:", apiPath);

                const res = await authApis().get(apiPath);

                const data = res.data.data || res.data;
                setRecords(data);
            } catch (ex) {
                console.error("Lỗi tải bệnh án:", ex);
            } finally {
                setLoading(false);
            }
        };
        if (petId) fetchHistory();
    }, [petId, isOwnerPath]);

    const handleViewDetail = (id) => {
        setSelectedRecordId(id);
        setShowModal(true);
    };

    if (loading) return <div className="text-center mt-5"><Spinner animation="border" /></div>;

    return (
        <Container className="mt-4">
            <Breadcrumb>
                <Breadcrumb.Item onClick={() => nav(-1)}>Quay lại</Breadcrumb.Item>
                <Breadcrumb.Item active>Lịch sử bệnh án</Breadcrumb.Item>
            </Breadcrumb>

            <Card className="shadow-sm border-0">
                <Card.Header className="bg-primary text-white py-3">
                    <h5 className="mb-0">Lịch Sử Điều Trị Của Thú Cưng</h5>
                </Card.Header>
                <Card.Body>
                    <Table responsive hover>
                        <thead>
                            <tr>
                                <th>Ngày khám</th>
                                <th>Bác sĩ phụ trách</th>
                                <th>Chẩn đoán</th>
                                <th>Thao tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            {records.length > 0 ? records.map(r => (
                                <tr key={r.id}>
                                    <td>{moment(r.created_at).format("DD/MM/YYYY HH:mm")}</td>
                                    <td>{r.staff_name}</td>
                                    <td>
                                        <Badge bg="info" className="text-dark">{r.diagnosis}</Badge>
                                    </td>
                                    <td>
                                        <Button size="sm" variant="outline-primary" onClick={() => handleViewDetail(r.id)}>
                                            Xem chi tiết
                                        </Button>
                                    </td>
                                </tr>
                            )) : (
                                <tr>
                                    <td colSpan="4" className="text-center text-muted py-4">Chưa có lịch sử khám bệnh nào.</td>
                                </tr>
                            )}
                        </tbody>
                    </Table>
                </Card.Body>
            </Card>

            <MedicalRecordDetailModal
                recordId={selectedRecordId}
                show={showModal}
                onHide={() => setShowModal(false)}
                isOwner={isOwnerPath}
            />
        </Container>
    );
};

export default PetMedicalHistory;
