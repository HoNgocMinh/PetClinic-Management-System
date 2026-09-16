import { useEffect, useState } from "react";
import { Badge, Button, Card, Col, Container, Form, Row, Spinner, Table } from "react-bootstrap";
import toast from "react-hot-toast";
import { authApis, endpoint } from "../../configs/Apis";

const statusLabels = {
    PENDING: "Chờ xác nhận",
    CONFIRMED: "Đã xác nhận",
    CHECKED_IN: "Đã đến phòng khám",
    IN_PROGRESS: "Đang khám",
    WAITING_PAYMENT: "Chờ thanh toán",
    COMPLETED: "Hoàn thành",
    CANCELLED: "Đã hủy",
    NO_SHOW: "Vắng mặt",
};

const formatCurrency = (value) => {
    const amount = Number(value || 0);
    return amount.toLocaleString("vi-VN", {
        style: "currency",
        currency: "VND",
    });
};

const AdminReports = () => {
    const [overview, setOverview] = useState(null);
    const [revenue, setRevenue] = useState(null);
    const [clinicReport, setClinicReport] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        date_from: "",
        date_to: "",
        group_by: "day",
    });

    const buildQueryParams = (nextFilters) => {
        const params = {};
        if (nextFilters.date_from) params.date_from = nextFilters.date_from;
        if (nextFilters.date_to) params.date_to = nextFilters.date_to;
        return params;
    };

    const loadReports = async (nextFilters = filters) => {
        const nextQueryParams = buildQueryParams(nextFilters);
        try {
            setLoading(true);
            const [overviewRes, revenueRes, clinicRes] = await Promise.all([
                authApis().get(endpoint['admin_report_overview'], { params: nextQueryParams }),
                authApis().get(endpoint['admin_report_revenue'], {
                    params: { ...nextQueryParams, group_by: nextFilters.group_by },
                }),
                authApis().get(endpoint['admin_report_clinics'], { params: nextQueryParams }),
            ]);

            setOverview(overviewRes.data.data || overviewRes.data);
            setRevenue(revenueRes.data.data || revenueRes.data);
            setClinicReport(clinicRes.data.data || clinicRes.data);
        } catch (ex) {
            toast.error(ex.response?.data?.message || "Không thể tải báo cáo.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadReports();
    }, []);

    const handleFilterChange = (field, value) => {
        setFilters(prev => ({ ...prev, [field]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        loadReports();
    };

    const handleReset = () => {
        const resetFilters = { date_from: "", date_to: "", group_by: "day" };
        setFilters(resetFilters);
        loadReports(resetFilters);
    };

    const maxRevenue = Math.max(
        ...((revenue?.series || []).map(item => Number(item.revenue || 0))),
        0,
    );

    const kpiCards = [
        { label: "Tổng doanh thu", value: formatCurrency(overview?.total_revenue), tone: "success" },
        { label: "Thanh toán thành công", value: overview?.paid_payment_count || 0, tone: "primary" },
        { label: "Tổng lịch hẹn", value: overview?.appointment_count || 0, tone: "info" },
        { label: "Chủ nuôi mới", value: overview?.new_pet_owner_count || 0, tone: "warning" },
        { label: "Thú cưng mới", value: overview?.new_pet_count || 0, tone: "secondary" },
        { label: "Dịch vụ", value: overview?.service_count || 0, tone: "dark" },
    ];

    return (
        <Container className="py-4">
            <div className="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-4">
                <div>
                    <h2 className="fw-bold text-success mb-1">Báo cáo hệ thống</h2>
                    <p className="text-muted mb-0">Theo dõi doanh thu, lịch hẹn và hiệu suất phòng khám.</p>
                </div>
                <Form onSubmit={handleSubmit} className="admin-report-filter">
                    <Row className="g-2 align-items-end">
                        <Col sm={6} lg="auto">
                            <Form.Label className="small fw-bold">Từ ngày</Form.Label>
                            <Form.Control
                                type="date"
                                value={filters.date_from}
                                onChange={(e) => handleFilterChange("date_from", e.target.value)}
                            />
                        </Col>
                        <Col sm={6} lg="auto">
                            <Form.Label className="small fw-bold">Đến ngày</Form.Label>
                            <Form.Control
                                type="date"
                                value={filters.date_to}
                                onChange={(e) => handleFilterChange("date_to", e.target.value)}
                            />
                        </Col>
                        <Col sm={6} lg="auto">
                            <Form.Label className="small fw-bold">Nhóm doanh thu</Form.Label>
                            <Form.Select
                                value={filters.group_by}
                                onChange={(e) => handleFilterChange("group_by", e.target.value)}
                            >
                                <option value="day">Theo ngày</option>
                                <option value="month">Theo tháng</option>
                            </Form.Select>
                        </Col>
                        <Col sm={6} lg="auto" className="d-flex gap-2">
                            <Button type="submit" variant="success">Lọc</Button>
                            <Button type="button" variant="outline-secondary" onClick={handleReset}>Đặt lại</Button>
                        </Col>
                    </Row>
                </Form>
            </div>

            {loading ? (
                <div className="text-center py-5">
                    <Spinner animation="border" variant="success" />
                </div>
            ) : (
                <>
                    <Row className="g-3 mb-4">
                        {kpiCards.map(card => (
                            <Col md={6} xl={4} key={card.label}>
                                <Card className="border-0 shadow-sm admin-report-card">
                                    <Card.Body>
                                        <div className="d-flex justify-content-between align-items-start">
                                            <div>
                                                <div className="text-muted small fw-semibold">{card.label}</div>
                                                <div className="fs-3 fw-bold mt-2">{card.value}</div>
                                            </div>
                                            <Badge bg={card.tone}>Live</Badge>
                                        </div>
                                    </Card.Body>
                                </Card>
                            </Col>
                        ))}
                    </Row>

                    <Row className="g-4 mb-4">
                        <Col lg={8}>
                            <Card className="border-0 shadow-sm h-100">
                                <Card.Header className="bg-white py-3">
                                    <h5 className="mb-0 fw-bold">Biểu đồ doanh thu</h5>
                                </Card.Header>
                                <Card.Body>
                                    {(revenue?.series || []).length === 0 ? (
                                        <div className="text-center text-muted py-5">Chưa có doanh thu trong khoảng thời gian này.</div>
                                    ) : (
                                        <div className="revenue-chart">
                                            {revenue.series.map(item => {
                                                const itemRevenue = Number(item.revenue || 0);
                                                const height = maxRevenue > 0 ? Math.max((itemRevenue / maxRevenue) * 180, 12) : 12;
                                                return (
                                                    <div className="revenue-chart-item" key={item.period}>
                                                        <div className="revenue-chart-value">{formatCurrency(item.revenue)}</div>
                                                        <div className="revenue-chart-bar-wrap">
                                                            <div className="revenue-chart-bar" style={{ height }} />
                                                        </div>
                                                        <div className="revenue-chart-label">{item.period}</div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    )}
                                </Card.Body>
                            </Card>
                        </Col>

                        <Col lg={4}>
                            <Card className="border-0 shadow-sm h-100">
                                <Card.Header className="bg-white py-3">
                                    <h5 className="mb-0 fw-bold">Trạng thái lịch hẹn</h5>
                                </Card.Header>
                                <Card.Body>
                                    {Object.entries(overview?.appointment_status || {}).map(([status, count]) => (
                                        <div className="d-flex justify-content-between align-items-center py-2 border-bottom" key={status}>
                                            <span>{statusLabels[status] || status}</span>
                                            <Badge bg="light" text="dark">{count}</Badge>
                                        </div>
                                    ))}
                                </Card.Body>
                            </Card>
                        </Col>
                    </Row>

                    <Card className="border-0 shadow-sm">
                        <Card.Header className="bg-white py-3">
                            <h5 className="mb-0 fw-bold">Hiệu suất phòng khám</h5>
                        </Card.Header>
                        <Card.Body>
                            <Table responsive hover className="align-middle mb-0">
                                <thead className="table-light">
                                    <tr>
                                        <th>Phòng khám</th>
                                        <th className="text-end">Lịch hẹn</th>
                                        <th className="text-end">Hoàn thành</th>
                                        <th className="text-end">Thanh toán</th>
                                        <th className="text-end">Doanh thu</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {(clinicReport?.clinics || []).map(clinic => (
                                        <tr key={clinic.clinic_id}>
                                            <td className="fw-bold">{clinic.clinic_name}</td>
                                            <td className="text-end">{clinic.appointment_count}</td>
                                            <td className="text-end">{clinic.completed_appointment_count}</td>
                                            <td className="text-end">{clinic.paid_payment_count}</td>
                                            <td className="text-end fw-bold text-success">{formatCurrency(clinic.revenue)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </Table>
                        </Card.Body>
                    </Card>
                </>
            )}
        </Container>
    );
};

export default AdminReports;
