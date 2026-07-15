import { useEffect, useState } from "react";
import {Link, useNavigate} from "react-router-dom";
import api from "../api";
import {useAuth} from "../AuthContext";

export default function Dashboard() {
    const {user} = useAuth();
    const [error, setError] = useState("");
    
    useEffect(() => {
        api.get("/dashboard").then((resp) => setDashboard(resp.data)).catch(() => setError("Couldn't set dashboard."))

    }, []);

    return (
        <div>
            <div className="hero">
                <h1>Welcome back, {user?.username}</h1>
                <p>Begin your journey learning Afrikaans. Good luck</p>
            </div>
        </div>
    )
}