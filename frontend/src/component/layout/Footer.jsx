import { Col, Container, Row } from "react-bootstrap";
import "./styles/Footer.css";

const Footer = () => {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="site-footer mt-5">
            <Container className="p-2">
                <hr />
                <Row>
                    <Col className="text-center footer-bottom">
                        <p className="small">Copyright © {currentYear} - 2DEL.</p>
                    </Col>
                </Row>
                <hr />
            </Container>
        </footer>
    );
};

export default Footer;