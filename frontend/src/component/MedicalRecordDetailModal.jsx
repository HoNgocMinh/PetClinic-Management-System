import React, { useState, useEffect } from "react";
import { Modal, Table, Row, Col, Badge, Spinner, Alert } from "react-bootstrap";
import { authApis, endpoint } from "../configs/Apis";

const MedicalRecordDetailModal = ({ recordId, appId, show, onHide, isOwner = false }) => {
    const [data, setData] = useState({ record: null, prescription: null });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (show && recordId) {
            const fetchFullDetail = async () => {
                setLoading(true);
                try {
                    const recordUrl = isOwner
                        ? endpoint['owner_medical_record_detail'](recordId)
                        : endpoint['medical_record_detail'](recordId);

                    const presUrl = isOwner
                        ? endpoint['owner_medical_record_prescription'](recordId)
                        : endpoint['medical_record_prescription'](recordId);

                    const [resRec, resPres] = await Promise.all([
                        authApis().get(recordUrl),
                        authApis().get(presUrl).catch(() => null) // Đơn thuốc có thể trống
                    ]);

                    setData({
                        record: resRec.data.data || resRec.data,
                        prescription: resPres ? (resPres.data.data || resPres.data) : null
                    });
                } catch (ex) {
                    toast.error("Không thể tải hồ sơ bệnh án.");
                } finally {
                    setLoading(false);
                }
            };
            fetchFullDetail();
        }
    }, [recordId, show, isOwner]);

    return (
        <Modal show={show} onHide={onHide} size="lg" centered>
            <Modal.Header closeButton className="bg-light">
                <Modal.Title>Chi tiết ca khám #{recordId}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {loading ? (
                    <div className="text-center p-5"><Spinner animation="grow" /></div>
                ) : data.record ? (
                    <>
                        <Row className="mb-3">
                            <Col md={6}>
                                <p className="mb-1 text-muted small">Triệu chứng</p>
                                <p className="fw-bold">{data.record.symptoms}</p>
                            </Col>
                            <Col md={6}>
                                <p className="mb-1 text-muted small">Chẩn đoán</p>
                                <Badge bg="danger" className="fs-6">{data.record.diagnosis}</Badge>
                            </Col>
                        </Row>
                        <hr />
                        <div className="mb-3">
                            <p className="mb-1 text-muted small">Hướng điều trị</p>
                            <p>{data.record.treatment || "Không có hướng dẫn bổ sung"}</p>
                        </div>

                        <h6 className="mt-4 mb-3 text-primary fw-bold">💊 Đơn thuốc đính kèm</h6>
                        {data.prescription && data.prescription.items?.length > 0 ? (
                            <Table striped bordered hover size="sm">
                                <thead className="table-secondary">
                                    <tr>
                                        <th>Tên thuốc</th>
                                        <th>SL</th>
                                        <th>Liều dùng/Tần suất</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.prescription.items.map(item => (
                                        <tr key={item.id}>
                                            <td>{item.medicine_name}</td>
                                            <td>{item.quantity} {item.medicine_unit}</td>
                                            <td>{item.dosage} - {item.frequency} (Dùng {item.duration_days} ngày)</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </Table>
                        ) : (
                            <Alert variant="warning" className="small">Ca khám này không kê thuốc hoặc đơn thuốc chưa được khởi tạo.</Alert>
                        )}
                    </>
                ) : <p className="text-center">Không tải được dữ liệu.</p>}
            </Modal.Body>
        </Modal>
    );
};

export default MedicalRecordDetailModal;