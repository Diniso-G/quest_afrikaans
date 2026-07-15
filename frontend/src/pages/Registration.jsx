import { useState } from "react";
import {Link, useNavigate} from "react-router-dom";
import api from "../api";
import {useAuth} from "../AuthContext";

export default function Registration() {
    const [email, setEmail] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);
    const {login} = useAuth();
    const navigate = useNavigate();


    async function handleSubmit(e) {
        e.preventDefault();
        setError("");
        setBusy(true);

        try {
            await api.post("/auth/register", {email, username, password});
            const form = new URLSearchParams();
            form.append("username", email);
            form.append("password", password);
            const resp = await api.post("/auth/login", form);
            login(resp.data.access_token);
            navigate("/dashboard");
        } catch (err) {
            console.log("Registration error: ", err);
            console.log("response: ", err.response);
            console.log("data: ", err.response?.data);

            const detail = err.response?.data?.detail;
            setError(typeof detail === "string" ? detail: "Registration failed");
        } finally {
            setBusy(false);
        }
    };

    return (
        <div id ="authScreen">
            <div className="auth-wrap">
                <div className="auth-brand">
                    <h1>QUEST_AFRIKAANS</h1>
                    <p>Become fluent in Afrikaans</p>
                </div>
                <div className="auth-card">
                    <div id="authMessage" className="auth-error"></div>
                    <div id="registerForm">
                        <h2> Create an account</h2>
                        <p> Create account and start hunting bugs. </p>
                        {error && <div className="error-banner"> {error}</div>}
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label>Email</label>
                                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                            </div>    
                            <div className="form-group">
                                <label>Username</label>
                                <input value={username} onChange={(e) => setUsername(e.target.value)} required />
                            </div> 
                            <div className="form-group">
                                <label>Password</label>
                                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                            </div> 
                            <button className="btn btn-primary">
                            {busy ? "Creating...": "Create account"}
                            </button>
                        </form>         
                        <p>Already have an account? <Link to="/login">Sign in</Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

