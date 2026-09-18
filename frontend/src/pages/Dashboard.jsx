import { useEffect, useState } from "react";
import {Link} from "react-router-dom";
import api from "../api";
import {useAuth} from "../AuthContext";

export default function Dashboard() {
    const {user} = useAuth();
    const [error, setError] = useState("");
    const [stats, setStats] = useState(null);
    const [history, setHistory] = useState(null);
    const [showHistory, setShowHistory] = useState(false);
    const [loadingHistory, setLoadingHistory] = useState(false);
    
    
    useEffect(() => {
        api.get("/users/me/dashboard").then((resp) => setStats(resp.data)).catch(() => setError("Couldn't load your stats. Try refreashing browser."));

    }, []);

    function toggleHistory() {
        if (showHistory) {
            setShowHistory(false);
            return;
        }
        setShowHistory(true);
        if (history) return;

        setLoadingHistory(true);
        api.get("/users/me/history").then((resp) => setHistory(resp.data)).catch(() => setError("Couldn't load your history file. Try refreashing browser.")).finally(() => setLoadingHistory(false));
    }

    const TYPE_LABELS = {lesson: "Lesson", quiz: "Quiz", vocab: "Word Match", pronunciation: "Pronounciation"};

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
            <div className="section-title">Your History</div>
            <button className="btn btn-primary" onClick={toggleHistory}>
                {showHistory ? "Hide history" : "View History"}
            </button>

            {showHistory && (
                <div style={{marginTop: 20}}>
                    {loadingHistory && <p>Loading...</p>}
                    {!loadingHistory && history && history.length === 0 && (
                        <p style={{color: "var(--on-canvas-soft)"}}>No activity yet - go complete something!</p>
                    )}
                    {!loadingHistory && history && history > 0 && (
                        <div className="card-grid">
                            {history.map((item, i) => (
                                <div key={i} className="card-case">
                                    <div className="case-id">
                                        {TYPE_LABELS[item.type] || item.type} - {new Date(item.created_at).toLocaleString()}
                                    </div>
                                    <h3 className="case-title">{item.label}</h3>
                                    {item.detail && <p>{item.detail}</p>}
                                    {item.correct !== null && item.correct !== undefined && (
                                        <span className={"achievement-chip"} style={{background: item.correct ? "var(--success" : "var(--rust)",}}>
                                            {item.correct ? "Correct" : "Incorrect"}
                                        </span>
                                    )}

                                    {item.score !== null && item.score !== undefined && (
                                        <span style={{marginLeft: 8}}>Score: {item.score}</span>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            <div className="section-title">Ready for your next Lesson?</div>
            <Link to="/lessons" className="btn btn-primary">Open Lesson</Link>
        </div>
    );
}