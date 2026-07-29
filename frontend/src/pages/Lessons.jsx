import { useEffect, useState } from "react";
import {Link, useNavigate} from "react-router-dom";
import api from "../api";

const MODULE = ["Part 1", "Part 2", "Part 2"];
const DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"];


export default function Lessons(){
    const [lessons, setLessons] = useState([]);
    const [error, setError] = useState("");
    const [scoring, setScoring] = useState(null);
    const [target, setTarget] = useState("");
    const [generating, setGenerating] = useState(false);
    const [transcript, setTranscript] = useState("");
    const [pronResult, setPronResult] = useState(null);
    const navigate = useNavigate();

    function load(){
        api.get("/lessons").then((resp) => setLessons(resp.data)).catch(() => setError("Couldn't load lessons."))
    }

    useEffect(() => { load()}, []);

    async function handleScorePronounciation(e) {
        e.preventDefault()
        try {
            const resp = await api.post("/speech/score", { target_phrase: target, transcribed_text: transcript})
            setPronResult(resp.data)
        }
        catch {
            setError("Couldn't score pronounciation")
        }
    }

        return (
        <div>
            <div className="hero">
                <h1>Lessons</h1>
                <p>This is the basis for Quest Afrikaans. Lesson browseing and adaptive proficiency scoring dashboard.</p>
            </div>
            {error && <div className="error-banner">{error}</div>}

            <div className="card">
                <h3>Try pronounciation scoring</h3>
                <p>Demo only: paste a target phrase and a transcript (stand-in for real speech to text) to see how scoring works</p>
                <form onSubmit={handleScorePronounciation}>
                    <div className="field"><label>Target phrase</label>
                        <input value={target} onChange={(e) => setTarget(e.target.value)} placeholder="Hallo, hoe gaan dit?" required />   
                    </div>
                    <div className="field"><label>Transcript</label>
                        <input value={transcript} onChange={(e) => setTranscript(e.target.value)} placeholder="What you said" required />   
                    </div>
                    <button className="btn btn-primary">Score it</button>
                </form>
                {pronResult && (
                    <p>
                        <b>{pronResult.pronounciation_score}/100</b> - {pronResult.feedback}
                    </p>
                )}
            </div>

            <div className="section-title">Existing Lessons</div>
            {lessons.length === 0 ? (
                <p>No lessons yet - generate your first lesson above.</p>
            ) : (
                <div className="card-grid">
                    {lessons.map((c) => (
                        <div key={c.id} className="card-case">
                            <div className="case-id">CLASS-{String(c.id).padStart(4, "0")}{c.level} . {c.topic}</div>
                            <h3 className="case-title">{c.title}</h3>
                            <p>{c.content}</p>
                            {c.example_sentences && (
                                <pre>{c.example_sentences}</pre>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

