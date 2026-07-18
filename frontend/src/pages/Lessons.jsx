import { useEffect, useState } from "react";
import {Link, useNavigate} from "react-router-dom";
import api from "../api";


export default function Lessons(){
    const [lessons, setLessons] = useState([]);
    const [error, setError] = useState("");
    const [target, setTarget] = useState("");
    const [generating, setGenerating] = useState(false);
    const [transcript, setTranscript] = useState("");
    const navigate = useNavigate();

    function load(){
        api.get("/lessons").then((resp) => setLessons(resp.data)).catch(() => setError("Couldn't load lessons."))
    }

    useEffect(() => { load()}, []);

        return (
        <div>
            <div className="hero">
                <h1>Lessons</h1>
                <p>This is the basis for Quest Afrikaans. Lesson browseing and adaptive proficiency scoring dashboard.</p>
            </div>
            {error && <div className="error-banner">{error}</div>}
            
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

                    <div  className="card-case">
                        <h3 className="case-title">Try Pronounce Feature</h3>
                        <p>Comming soon....</p>
                        
                    </div>
                </div>
            )}
        </div>
    );
}

