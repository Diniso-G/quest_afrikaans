import { useState } from "react";
import {Link, useNavigate} from "react-router-dom";
import api from "../api";
import {useAuth} from "../AuthContext";

export default function Login() {
    const [email, setEmail] = useState("");
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
            const form = new URLSearchParams();
            form.append("username", email);
            form.append("password", password);
            const resp = await api.post("/auth/login", form);
            login(resp.data.access_token);
            navigate("/dashboard");
        } catch (err) {
            setError(err.response?.data?.detail || "Login Failed");
        } finally {
            setBusy(false);
        }
    }

    return (
        <div id="authScreen">
            <div class="auth-wrap">
                <div class="auth-brand">
                    <h1>QUEST_AFRIKAANS</h1>
                    <p>Become fluent in afrikaanns/Word vlot in Afrikaans</p>
                </div>
                <div className="auth-card">
                    <div id="authMessage" class="auth-error"></div>
                    <div id="loginForm">
                        <h2> Welkom terug</h2>
                        <p> Sign in to continue learning Afrikaans </p>
                        {error && <div className="error-banner"> {error}</div>}
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label>Email</label>
                                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
                            </div>    
                            <div className="form-group">
                                <label>Password</label>
                                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                            </div> 
                            <button className="btn btn-primary">
                            {busy ? "Signing in...": "Sign in"}
                            </button>
                        </form>         
                        <p>No account? <Link to="/register">Create an Account</Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

