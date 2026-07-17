import { useEffect, useState } from "react";
import api from "../api";

export default function Leaderboard() {
    const [rows, setRows] = useState([]);
    const [error, setError] = useState("");

    useEffect(() => {
        api.get("/users/leaderboard").then((resp) => setRows(resp.data)).catch(() => setError("Coundn't load the leaderboard."))
    }, []);

    return (
        <div>
            <div className="hero">
                <h1>Leaderboard</h1>
                <p>The sharpest bug hunter.</p>
            </div>
            {error && <div className="error-banner">{error}</div>}
            <div className="case-card">
                {rows.map((r, i) => (
                    <div key={r.username} className="leaderboard-row">
                        <div className="leaderboard-rank">{i + 1}</div>
                        <div className="leaderboard-name">{r.username}</div>
                        <div>{r.bugs_fixed} bugs</div>
                        <div className="leaderboard-xp">{r.xp} XP</div>
                    </div>
                ))}
                {rows.length === 0 && <p>No entries yet.</p>}
            </div>
        </div>
    );
}