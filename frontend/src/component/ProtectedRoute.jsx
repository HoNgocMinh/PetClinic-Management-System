import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { MyUserContext } from "../configs/MyContexts";

const ProtectedRoute = ({ children, allowedRole }) => {
    const user = useContext(MyUserContext);

    if (!user) {
        // Nếu chưa đăng nhập, đá về trang Login
        return <Navigate to="/login" />;
    }

    if (allowedRole && user.role !== allowedRole) {
        // Nếu sai Role (ví dụ Pet Owner vào trang Staff), đá về trang chủ
        return <Navigate to="/" />;
    }

    return children;
};

export default ProtectedRoute;
