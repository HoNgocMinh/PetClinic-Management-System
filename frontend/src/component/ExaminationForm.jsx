import { useState, useEffect } from "react";
import { Modal, Form, Button, Row, Col, Table } from "react-bootstrap";
import { authApis, endpoint } from "../configs/Apis";
import toast from "react-hot-toast";

const ExaminationForm = ({ appointment, show, onHide, onComplete }) => {
    const [step, setStep] = useState(1); // 1: Bệnh án, 2: Kê đơn
    const [loading, setLoading] = useState(false);
    const [prescriptionId, setPrescriptionId] = useState(null);
    const [medicines, setMedicines] = useState([]);
    const [recordData, setRecordData] = useState({ symptoms: "", diagnosis: "", treatment: "", note: "" });
    const [prescriptionItems, setPrescriptionItems] = useState([]);

    const fetchMedicines = async () => {
        try {
            const res = await authApis().get(endpoint['medicines']);
            setMedicines(res.data.data || res.data || []);
        } catch {
            toast.error("Không thể tải danh sách thuốc.");
        }
    };

    const fetchExistingPrescription = async (recordId) => {
        try {
            const res = await authApis().get(endpoint['medical_record_prescription'](recordId));
            const data = res.data.data || res.data;
            setPrescriptionId(data.id);
        } catch (ex) {
            console.error("Lỗi lấy đơn thuốc cũ:", ex);
        }
    };

    useEffect(() => {
        if (show && appointment?.medical_record_id) {
            setStep(2);
            fetchExistingPrescription(appointment.medical_record_id);
            fetchMedicines();
        } else {
            setStep(1);
            setRecordData({ symptoms: "", diagnosis: "", treatment: "", note: "" });
            setMedicines([]);
        }
    }, [show, appointment]);
    const handleSubmitRecord = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const resRecord = await authApis().post(endpoint['appointment_medical_record'](appointment.id), recordData);
            const newRecord = resRecord.data.data || resRecord.data;

            const resPres = await authApis().post(endpoint['medical_record_prescription'](newRecord.id), { note: "Kê đơn tại quầy" });
            setPrescriptionId(resPres.data.id || resPres.data.data.id);

            setStep(2);
            fetchMedicines();
            toast.success("Đã lưu bệnh án. Bạn có thể kê thuốc hoặc bỏ qua bước này!");
        } catch {
            toast.error("Lỗi khi lưu bệnh án.");
        } finally {
            setLoading(false);
        }
    };

    const handleAddMedicine = (e) => {
        const medId = e.target.value;
        if (!medId) return;
        const medicine = medicines.find(m => m.id === parseInt(medId));
        if (prescriptionItems.some(item => item.medicine_id === medicine.id)) {
            return toast.error("Thuốc này đã có trong danh sách!");
        }
        const newItem = {
            medicine_id: medicine.id,
            medicine_name: medicine.name,
            unit: medicine.unit,
            quantity: 1,
            dosage: "",
            frequency: "",
            duration_days: 1,
            instruction: ""
        };
        setPrescriptionItems([...prescriptionItems, newItem]);
    };

    const handleItemChange = (index, field, value) => {
        const updatedItems = [...prescriptionItems];
        updatedItems[index][field] = value;
        setPrescriptionItems(updatedItems);
    };

    const removeItem = (index) => {
        setPrescriptionItems(prescriptionItems.filter((_, i) => i !== index));
    };

    const handleFinalize = async () => {
        setLoading(true);
        try {
            if (prescriptionItems.length > 0) {
                const promises = prescriptionItems.map(item =>
                    authApis().post(endpoint['prescription_items'](prescriptionId), {
                        medicine_id: item.medicine_id,
                        quantity: item.quantity,
                        dosage: item.dosage || "Theo chỉ dẫn",
                        frequency: item.frequency || "1 lần/ngày",
                        duration_days: item.duration_days,
                        instruction: item.instruction
                    })
                );
                await Promise.all(promises);
            }
            await authApis().post(endpoint['appointment_complete'](appointment.id));
            toast.success("Đã chốt ca khám thành công!");
            onComplete();
            onHide();
        } catch {
            toast.error("Lỗi khi lưu dữ liệu ca khám.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal show={show} onHide={onHide} size="xl" backdrop="static">
            <Modal.Header closeButton>
                <Modal.Title>
                    {step === 1 ? `Khám bệnh: ${appointment.pet_name}` : `Kê đơn cho: ${appointment.pet_name}`}
                </Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {step === 1 ? (
                    <Form onSubmit={handleSubmitRecord}>
                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label className="fw-bold">Triệu chứng</Form.Label>
                                    <Form.Control as="textarea" rows={3} required value={recordData.symptoms}
                                        onChange={e => setRecordData({ ...recordData, symptoms: e.target.value })} />
                                </Form.Group>
                            </Col>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label className="fw-bold">Chẩn đoán</Form.Label>
                                    <Form.Control as="textarea" rows={3} required value={recordData.diagnosis}
                                        onChange={e => setRecordData({ ...recordData, diagnosis: e.target.value })} />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Form.Group className="mb-3">
                            <Form.Label className="fw-bold">Hướng điều trị</Form.Label>
                            <Form.Control as="textarea" rows={2} value={recordData.treatment}
                                onChange={e => setRecordData({ ...recordData, treatment: e.target.value })} />
                        </Form.Group>
                        <Button variant="primary" type="submit" className="w-100 py-2" disabled={loading}>
                            {loading ? "Đang xử lý..." : "Lưu bệnh án & Chuyển sang kê đơn"}
                        </Button>
                    </Form>
                ) : (
                    <div>
                        <div className="mb-4 p-3 bg-light border rounded">
                            <Form.Label className="fw-bold text-primary">Chọn thuốc từ kho (tùy chọn):</Form.Label>
                            <Form.Select onChange={handleAddMedicine} value="">
                                <option value="">-- Click để thêm thuốc --</option>
                                {medicines.map(m => (
                                    <option key={m.id} value={m.id}>
                                        {m.name} - Tồn kho: {m.stock_quantity} {m.unit}
                                    </option>
                                ))}
                            </Form.Select>
                        </div>

                        <Table responsive bordered hover>
                            <thead className="table-dark">
                                <tr>
                                    <th>Tên thuốc</th>
                                    <th>Số lượng</th>
                                    <th>Liều dùng</th>
                                    <th>Tần suất</th>
                                    <th>Số ngày</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                {prescriptionItems.length > 0 ? prescriptionItems.map((item, index) => (
                                    <tr key={item.medicine_id}>
                                        <td className="align-middle"><strong>{item.medicine_name}</strong></td>
                                        <td><Form.Control type="number" min="1" value={item.quantity} onChange={e => handleItemChange(index, 'quantity', e.target.value)} /></td>
                                        <td><Form.Control value={item.dosage} placeholder="1 viên..." onChange={e => handleItemChange(index, 'dosage', e.target.value)} /></td>
                                        <td><Form.Control value={item.frequency} placeholder="Sáng/Chiều..." onChange={e => handleItemChange(index, 'frequency', e.target.value)} /></td>
                                        <td><Form.Control type="number" min="1" value={item.duration_days} onChange={e => handleItemChange(index, 'duration_days', e.target.value)} /></td>
                                        <td><Button variant="outline-danger" size="sm" onClick={() => removeItem(index)}>X</Button></td>
                                    </tr>
                                )) : (
                                    <tr><td colSpan="6" className="text-center text-muted p-4">Chưa chọn thuốc nào. Có thể bỏ qua bước này.</td></tr>
                                )}
                            </tbody>
                        </Table>

                        <div className="d-flex gap-2 mt-4">
                            <Button variant="secondary" className="flex-grow-1" onClick={onHide}>Hủy bỏ</Button>
                            <Button variant="success" className="flex-grow-2 w-50" onClick={handleFinalize} disabled={loading}>
                                {loading ? "Đang lưu..." : "Xác nhận & Hoàn tất"}
                            </Button>
                        </div>
                    </div>
                )}
            </Modal.Body>
        </Modal>
    );
};

export default ExaminationForm;
