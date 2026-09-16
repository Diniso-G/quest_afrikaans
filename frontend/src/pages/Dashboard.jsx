import { useEffect, useState } from "react";
import {Link} from "react-router-dom";
import api from "../api";
import {useAuth} from "../AuthContext";

export default function Dashboard() {
    const {user} = useAuth();
    const [error, setError] = useState("");
    const [stats, setStats] = useState(null);
    
    useEffect(() => {
        api.get("/users/me/dashboard").then((resp) => setStats(resp.data)).catch(() => setError("Couldn't load your case file. Try refreashing browser."));

    }, []);

    //const xpPcct = stats ? Math.round(((100 - stats.xp_to_next_level) / 100) * 100): 0;
    const xpIntoLevel = stats ? 100 - stats.xp_to_next_level : 0;

    return (
        <div>
            <div className="hero">
                <h1>Welkom back, {user?.username}</h1>
                <p>Everyday you stay learning. You become more proficient in Afrikaans.</p>
            </div>

            {error && <div className="error-banner">{error}</div>}

            {stats && (
                <>
                <div className="dashboard-hero">
                    <div className="xp-hero">
                        <div className="xp-hero-num">{stats.xp}</div>
                        <div className="xp-hero-label">Total XP</div>
                        <div className="xp-bar">
                            <div className="xp-bar-fill" style={{width: `${xpIntoLevel}%`}}/>
                        </div>
                    </div>
                    <div className="stat-cluster">
                        <div className="stat-chip"><b>{stats.level}</b> Level</div>
                        <div className="stat-chip"><b>{stats.streak}</b>Day streak</div>
                    </div>
                </div>
                <div className="section-title">Achievements</div>
                {stats.achievements.length === 0 ? (
                    <p style={{color: "var(--on-canvas-soft)"}}> No badges yet- start learning to earn one.</p>
                ) : (
                    <div>
                        {stats.achievements.map((a) => (
                            <span key={a} className="achievement-chip"> 
                            Crwn {a}
                            </span>
                        ))}
                    </div>
                )}
                </>

            )}
            <div className="section-title">Ready for your next lesson?</div>
            <Link to="/lessons" className="btn btn-primary">Open Lesson</Link>
        </div>
    );
}