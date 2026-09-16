import { useContext } from "react";
import { Navbar, Nav, Container, NavDropdown } from "react-bootstrap";
import { NavLink, useNavigate } from "react-router-dom";
import { MyUserContext, MyDipatcherContext } from "../../configs/MyContexts";
import "./styles/Header.css";

const Header = () => {
    const user = useContext(MyUserContext);
    const dispatch = useContext(MyDipatcherContext);
    const nav = useNavigate();

    const logout = () => {
        dispatch({ type: "logout" });
        nav("/login");
    };

    return (
        <Navbar bg="dark" variant="dark" expand="lg" className="py-3 shadow-sm sticky-top">
            <Container>
                <Navbar.Brand as={NavLink} to="/" className="fw-bold fs-4 me-5">
                    THÚ Y 2DEL
                </Navbar.Brand>

                <Navbar.Toggle aria-controls="basic-navbar-nav" />

                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto custom-nav">
                        {user && user.role === "CLINIC_STAFF" && (
                            <>
                                <Nav.Link as={NavLink} to="/staff/appointments" className="mx-2 fw-semibold text-warning">
                                    Quản lý lịch hẹn
                                </Nav.Link>
                                <Nav.Link as={NavLink} to="/staff/medicines" className="mx-2 fw-semibold">
                                    Quản lý thuốc
                                </Nav.Link>
                            </>
                        )}

                        {user && user.role === "PET_OWNER" && (
                            <>
                                <Nav.Link as={NavLink} to="/pets" className="mx-2 fw-semibold">
                                    Thú cưng của tôi
                                </Nav.Link>
                                <Nav.Link as={NavLink} to="/appointments" className="mx-2 fw-semibold">
                                    Lịch hẹn của tôi
                                </Nav.Link>
                            </>
                        )}

                        {user && user.role === "ADMIN" && (
                            <>
                                <Nav.Link as={NavLink} to="/admin/reports" className="mx-2 fw-semibold">
                                    Báo cáo
                                </Nav.Link>
                                <Nav.Link as={NavLink} to="/admin/clinics" className="mx-2 fw-semibold">
                                    Phòng khám
                                </Nav.Link>
                                <Nav.Link as={NavLink} to="/admin/staffs" className="mx-2 fw-semibold">
                                    Nhân viên
                                </Nav.Link>
                                <Nav.Link as={NavLink} to="/admin/services" className="mx-2 fw-semibold">
                                    Dịch vụ
                                </Nav.Link>
                            </>
                        )}
                    </Nav>

                    <Nav className="align-items-center">
                        {user === null ? (
                            <>
                                <Nav.Link as={NavLink} to="/login" className="fw-bold text-white mx-2">
                                    Đăng nhập
                                </Nav.Link>
                                <Nav.Link as={NavLink} to="/register" className="btn btn-outline-success text-white px-3 fw-bold">
                                    Đăng ký
                                </Nav.Link>
                            </>
                        ) : (
                            <NavDropdown
                                title={<span className="fw-bold text-success">Chào, {user.full_name || user.username}</span>}
                                id="user-dropdown"
                                align="end"
                            >
                                <NavDropdown.Item as={NavLink} to="/profile">Hồ sơ cá nhân</NavDropdown.Item>
                                <NavDropdown.Item as={NavLink} to="/change-password">Đổi mật khẩu</NavDropdown.Item>

                                {user.is_superuser && (
                                    <NavDropdown.Item href="http://localhost:8000/admin/" target="_blank">
                                        Hệ thống Admin (Django)
                                    </NavDropdown.Item>
                                )}

                                <NavDropdown.Divider />
                                <NavDropdown.Item onClick={logout} className="text-danger fw-bold">
                                    Đăng xuất
                                </NavDropdown.Item>
                            </NavDropdown>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default Header;
