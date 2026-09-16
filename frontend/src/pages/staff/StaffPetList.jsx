import React, { useEffect, useState } from "react";
import { Container, Table, Button, Spinner, InputGroup, Form } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { authApis, endpoint } from "../../configs/Apis";
import toast from "react-hot-toast";

const StaffPetList = () => {
    const [pets, setPets] = useState([]);
    const [loading, setLoading] = useState(false);
    const [q, setQ] = useState("");
    const navigate = useNavigate();

    const loadPets = async () => {
        try {
            setLoading(true);
            const res = await authApis().get(endpoint['pets'], {
                params: { q: q }
            });
            const data = res.data.data || res.data;
            setPets(Array.isArray(data) ? data : []);
        } catch (ex) {
            console.error("Lỗi 403 hoặc lỗi tải:", ex);
            if (ex.response?.status === 403) {
                toast.error("Bạn không có quyền truy cập danh sách của chi nhánh này.");
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadPets();
    }, [q]); 

    if (loading) return <div className="text-center mt-5"><Spinner animation="border" /></div>;
    return (
        <Container className="mt-4">
            <h2 className="text-primary fw-bold mb-4">DANH SÁCH THÚ CƯNG HỆ THỐNG</h2>
            <Form.Control
                placeholder="Tìm tên Pet hoặc Chủ nuôi..."
                className="mb-3"
                onChange={(e) => setQ(e.target.value)}
            />
            <Table striped bordered hover>
                <thead>
                    <tr>
                        <th>Tên Pet</th>
                        <th>Chủ nuôi</th>
                        <th>Loài</th>
                        <th>Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    {pets.map(p => (
                        <tr key={p.id}>
                            <td>{p.name}</td>
                            <td>{p.owner_name}</td>
                            <td>{p.species}</td>
                            <td>
                                <Button
                                    variant="info"
                                    size="sm"
                                    onClick={() => navigate(`/staff/pets/${p.id}/history`)} // Path Staff
                                >
                                    Lịch sử bệnh án
                                </Button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        </Container>
    );
};

export default StaffPetList;
