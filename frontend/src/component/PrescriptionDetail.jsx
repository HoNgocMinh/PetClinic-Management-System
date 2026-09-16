
const PrescriptionDetail = ({ recordId, show, onHide }) => {
    const [prescription, setPrescription] = useState(null);

    useEffect(() => {
        if (recordId && show) {
            const loadPrescription = async () => {
                try {
                    const res = await authApis().get(endpoint['owner_medical_record_prescription'](recordId));
                    setPrescription(res.data.data || res.data);
                } catch (ex) {
                    console.error("Hồ sơ này chưa có đơn thuốc");
                }
            };
            loadPrescription();
        }
    }, [recordId, show]);

    return (
        <Modal show={show} onHide={onHide} centered>
            <Modal.Header closeButton>
                <Modal.Title>Đơn thuốc</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {prescription ? (
                    <ListGroup variant="flush">
                        {prescription.items.map((item, idx) => (
                            <ListGroup.Item key={idx}>
                                <div className="fw-bold text-primary">{item.medicine_name}</div>
                                <small>Số lượng: {item.quantity} | Cách dùng: {item.instruction}</small>
                            </ListGroup.Item>
                        ))}
                    </ListGroup>
                ) : <p className="text-center text-muted">Không tìm thấy thông tin đơn thuốc.</p>}
            </Modal.Body>
        </Modal>
    );
};