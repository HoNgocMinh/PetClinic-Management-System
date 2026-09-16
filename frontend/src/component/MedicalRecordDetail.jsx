import React, { useEffect, useState } from "react";
import { Card, ListGroup, Row, Col, Badge, Button, Modal } from "react-bootstrap";
import { authApis, endpoint } from "../configs/Apis";
import PrescriptionDetail from "./PrescriptionDetail"; 

const MedicalRecordDetail = ({ recordId, show, onHide }) => {
    const [record, setRecord] = useState(null);
    const [showPrescription, setShowPrescription] = useState(false);

    useEffect(() => {
        if (recordId && show) {
            const loadDetail = async () => {
                try {
                    const res = await authApis().get(endpoint['owner_medical_record_detail'](recordId));
                    setRecord(res.data.data || res.data);
                } catch (ex) {
                    console.error("Lỗi tải hồ sơ bệnh án");
                }
            };
            loadDetail();
        }
    }, [recordId, show]);

    if (!record) return null;

    return (
        <>
            <Modal show={show} onHide={onHide} size="lg" centered>
                <Modal.Header closeButton className="bg-success text-white">
                    <Modal.Title>CHI TIẾT HỒ SƠ BỆNH ÁN</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Row className="mb-3">
                        <Col md={6}><strong>Thú cưng:</strong> {record.pet_name}</Col>
                        <Col md={6}><strong>Ngày khám:</strong> {new Date(record.created_at).toLocaleDateString()}</Col>
                    </Row>
                    <Card className="mb-3 border-0 bg-light">
                        <Card.Body>
                            <h6 className="fw-bold text-success">Thông tin lâm sàng</h6>
                            <p><strong>Cân nặng:</strong> {record.weight} kg | <strong>Nhiệt độ:</strong> {record.temperature} °C</p>
                            <hr />
                            <p><strong>Chẩn đoán:</strong> {record.diagnosis}</p>
                            <p><strong>Lời dặn bác sĩ:</strong> {record.treatment_plan || "Không có ghi chú thêm"}</p>
                        </Card.Body>
                    </Card>
                    <div className="text-center">
                        <Button variant="outline-primary" onClick={() => setShowPrescription(true)}>
                            Xem đơn thuốc đi kèm
                        </Button>
                    </div>
                </Modal.Body>
            </Modal>

            {/* Modal Đơn thuốc */}
            <PrescriptionDetail 
                recordId={recordId} 
                show={showPrescription} 
                onHide={() => setShowPrescription(false)} 
            />
        </>
    );
};

export default MedicalRecordDetail;