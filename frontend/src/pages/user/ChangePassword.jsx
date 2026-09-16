import { useState } from "react";
import { Button, Form, Modal } from "react-bootstrap";
import { FaEye, FaEyeSlash, FaLock } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import { authApis, endpoint } from "../../configs/Apis";

const EMPTY_FORM = {
    old_password: "",
    new_password: "",
    confirm_password: "",
};

const ChangePassword = () => {
    const navigate = useNavigate();
    const [form, setForm] = useState(EMPTY_FORM);
    const [saving, setSaving] = useState(false);
    const [showPasswords, setShowPasswords] = useState(false);

    const handleClose = () => {
        navigate("/profile");
    };

    const handleChange = (field, value) => {
        setForm(prev => ({ ...prev, [field]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (form.new_password !== form.confirm_password) {
            toast.error("Mật khẩu xác nhận không khớp.");
            return;
        }

        try {
            setSaving(true);
            await authApis().put(endpoint['change_password'], form);
            toast.success("Đổi mật khẩu thành công.");
            setForm(EMPTY_FORM);
            navigate("/profile");
        } catch (ex) {
            const errors = ex.response?.data?.errors;
            if (errors) {
                const firstKey = Object.keys(errors)[0];
                toast.error(errors[firstKey][0]);
            } else {
                toast.error(ex.response?.data?.message || "Không thể đổi mật khẩu.");
            }
        } finally {
            setSaving(false);
        }
    };

    const inputType = showPasswords ? "text" : "password";

    return (
        <Modal show centered onHide={handleClose} backdrop="static">
            <Form onSubmit={handleSubmit}>
                <Modal.Header closeButton>
                    <Modal.Title className="h5 fw-bold d-flex align-items-center gap-2">
                        <FaLock className="text-success" />
                        Đổi mật khẩu
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <Form.Group className="mb-3">
                        <Form.Label className="small fw-bold">Mật khẩu hiện tại</Form.Label>
                        <Form.Control
                            type={inputType}
                            value={form.old_password}
                            required
                            autoFocus
                            onChange={e => handleChange("old_password", e.target.value)}
                        />
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label className="small fw-bold">Mật khẩu mới</Form.Label>
                        <Form.Control
                            type={inputType}
                            value={form.new_password}
                            required
                            minLength={6}
                            onChange={e => handleChange("new_password", e.target.value)}
                        />
                        <Form.Text className="text-muted">
                            Mật khẩu mới cần có ít nhất 6 ký tự.
                        </Form.Text>
                    </Form.Group>

                    <Form.Group className="mb-3">
                        <Form.Label className="small fw-bold">Xác nhận mật khẩu mới</Form.Label>
                        <Form.Control
                            type={inputType}
                            value={form.confirm_password}
                            required
                            minLength={6}
                            onChange={e => handleChange("confirm_password", e.target.value)}
                        />
                    </Form.Group>

                    <Button
                        type="button"
                        variant="link"
                        className="text-success fw-semibold p-0"
                        onClick={() => setShowPasswords(prev => !prev)}
                    >
                        {showPasswords ? <FaEyeSlash className="me-2" /> : <FaEye className="me-2" />}
                        {showPasswords ? "Ẩn mật khẩu" : "Hiện mật khẩu"}
                    </Button>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="outline-secondary" type="button" onClick={handleClose} disabled={saving}>
                        Hủy
                    </Button>
                    <Button variant="success" type="submit" disabled={saving}>
                        {saving ? "Đang lưu..." : "Cập nhật mật khẩu"}
                    </Button>
                </Modal.Footer>
            </Form>
        </Modal>
    );
};

export default ChangePassword;
