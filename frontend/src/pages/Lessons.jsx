import { useEffect, useState } from "react";
import {Link, useNavigate} from "react-router-dom";
import api from "../api";

//const LANGUAGES = ["Python", "Java", "JavaScript", "C#", "C++", "SQL"];
//const DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"];

export default function Lessons(){
    const [lessons, setLessons] = useState([]);
    const [error, setError] = useState("");
    const [genLang, setGenLang] = useState("Python");
    const [genDiff, setGenDiff] = useState("Beginner");
    const [genTopic, setGenTopic] = useState("");
    const [generating, setGenerating] = useState(false);
    const navigate = useNavigate();

    function load(){
        api.get("/lessons").then((resp) => setChallenges(resp.data)).catch(() => setError("Couldn't load any case files."))
    }

    useEffect(() => { load()}, []);

    async function handleGenerate(err) {
        err.preventDefault();
        setGenerating(true);
        setError("");

        try {
            const resp = await api.post("/challenges/generate", {
                language: genLang,
                difficulty: genDiff,
                topic: genTopic || null,
            });
            navigate(`/challenges/${resp.data.id}`);
        } 
        catch (er) {
            setError(er.response?.data?.detail || "Couldn't generate a new case.");
        }
        finally {
            setGenerating(false);
        }
        
    }
    return (
        <div>
            <div className="hero">
                <h1>Case Files</h1>
                <p>Each case is a real snippet with a hidden bug. Read it like a detective- then fix it.</p>
            </div>
            {error && <div className="error-banner">{error}</div>}
            <div className="case-card">
                <div className="case-title"> Open a new case</div>
                <form onSubmit={handleGenerate}>
                    <div className="field">
                        <label>Language</label>
                        <select value={genLang} onChange={(err) => setGenLang(err.target.value)}>
                            {LANGUAGES.map((l) => <option key={l} value={l}>{l}</option>)}
                        </select>
                     </div>
                    <div className="field">
                        <label>Difficulty</label>
                        <select value={genDiff} onChange={(err) => setGenDiff(err.target.value)}>
                            {DIFFICULTIES.map((d) => <option key={d} value={d}>{d}</option>)}
                        </select>
                    </div>
                    <div className="field">
                        <label>Topic (optional)</label>
                        <input value={genTopic} onChange={(err) => setGenTopic(err.target.value)} placeholder="e.g. recursion"/>
                    </div>
                    <button className="btn btn-primary" disabled={generating}>
                        {generating ? "Generating..." : "Generate case"}
                    </button>
                </form>
            </div>

            <div className="section-title">Existing Cases</div>
            {challenges.length === 0 ? (
                <p>No cases yet - generate your first case above.</p>
            ) : (
                <div className="card-grid">
                    {challenges.map((c) => (
                        <Link key={c.id} to={`/challenges/${c.id}`} className="card-case">
                            <div className="case-id">CASE-{String(c.id).padStart(4, "0")} . {c.language}</div>
                            <div className="case-title">{c.title}</div>
                            <span className={`tag difficulty-${c.difficulty}`}>{c.difficulty}</span>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}

