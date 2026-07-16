import { useEffect, useState } from "react";
import {Link, useNavigate} from "react-router-dom";
import api from "../api";
import {useAuth} from "../AuthContext";

export default function Dashboard() {
    const {user} = useAuth();
    const [error, setError] = useState("");
    const [stats, setStats] = useState(null);
    
    useEffect(() => {
        api.get("/users/me/dashboard").then((resp) => setStats(resp.data)).catch(() => setError("Couldn't load your case file. Try refreashing browser."))

    }, []);

    return (
        <div>
            <div className="hero">
                <h1>Welkom back, {user?.username}</h1>
                <p>Everyday you stay learning. You become more proficient in Afrikaans.</p>
            </div>

            {error && <div className="error-banner">{error}</div>}

            {stats && (
                <>
                <div className="stats-row">
                    
                </div>

                <div className="section-title">Achievements</div>
                </>

            )}
            <div className="section-title">Ready for next lesson</div>
            <Link to="/lessons" className="btn btn-primary">Open Lesson</Link>
        </div>
    );
}