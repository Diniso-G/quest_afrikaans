import { useEffect, useState, useRef } from "react";
import api from "../api";

import { useAuth} from "../AuthContext";

const LEVELS = ["All", "Beginner", "Intermediate", "Advanced"];
const COMPLETE_THRESHOLD = 70;

function parseExampleSentences(text) {
    if (!text) return [];
    return text.split("\n").map((line) => line.trim()).filter(Boolean).map((line) => {
        const [af, en] = line.split("|").map((s) => s && s.trim());
        return {afrikaans: af || line, english: en || ""};
    });
}

export default function Lessons(){
    const { refreshUser } = useAuth();

    const [lessons, setLessons] = useState([]);
    const [levelFilter, setLevelFilter] = useState("All");
    const [error, setError] = useState("");

    const [activePractice, setActivePractice] = useState(null);
    const [inputMode, setInputMode] = useState("type");

    const [scoring, setScoring] = useState(null);
    const [target, setTarget] = useState("");
    const [completionMessage, setCompletionMessage] = useState("");
    const [transcript, setTranscript] = useState("");
    const [pronResult, setPronResult] = useState(null);
    
    const [isRecording, setIsRecording] = useState(false);
    const [transcribing, setTranscribing] = useState(false);
    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);

    function load(level){
        const params = level && level !== "All" ? { level } : {};
        api.get("/lessons", {params}).then((resp) => setLessons(resp.data)).catch(() => setError("Couldn't load lessons."));
    }

    useEffect(() => { load(levelFilter);}, [levelFilter]);

    function startPractice(lesson, sentence) {
        setActivePractice({lessonId: lesson.id, lessonTitle: lesson.title, afrikaans: sentence.afrikaans, english: sentence.english,});
        setTranscript("");
        setPronResult(null);
        setCompletionMessage("");
        setError("");
    }

    async function recordLessonAttempt(lessonId, score) {
        try {
            const resp = await api.post("/lessons/attempt", {lessonId: lessonId, score});
            if (score >= COMPLETE_THRESHOLD) {
                setCompletionMessage(`Lesson marked complete! Total XP: ${resp.data.xp}`);
            }
            refreshUser();
        } catch {
            setError("Couldn't record lesson attempt.")
        }
    }

    async function handleScore(e) {
        e?.preventDefault()
        if (!activePractice || !transcript) return;
        setScoring(true);
        setError("");
        try {
            const resp = await api.post("/speech/score", { target_phrase: activePractice.afrikaans, transcribed_text: transcript});
            setPronResult(resp.data);
            await recordLessonAttempt(activePractice.lessonId, resp.data.pronounciation_score);
        }
        catch {
            setError("Couldn't score pronounciation")
        } finally {
            setScoring(false);
        }
    }

    async function startRecording() {
        setError("");
        try {
            const stream = await navigator.mediaDevices.getUserModel({ audio: true});
            const recorder = new MediaRecorder(stream);
            chunksRef.current = [];
            recorder.ondataavailable = (e) => {
                if (e.data.size > 0) chunksRef.current.push(e.data);
            };
            recorder.onstop = async () => {
                stream.getTracks().forEach((t) => t.stop());
                const blob = new Blob(chunksRef.current, {type: "audio/webm"});
                await uploadForTranscription(blob);
            };
            mediaRecorderRef.current = recorder;
            recorder.start();
            setIsRecording(true);
        } catch {
            setError("Couldn't access the microphone. Check your browser permissions or type your answer instead.");
        }
    }

    function stopRecording() {
        mediaRecorderRef.current?.stop();
        setIsRecording(false);
    }

    async function uploadForTranscription(blob) {
        setTranscribing(true);
        setError("");
        try{
            const form = new FormData();
            form.append("audio", blob, "recording.webm");
            const resp = await api.post("/speech/transcribe", form, {headers: {"Content-Type": "multipart/form-data"},
            });
            setTranscript(resp.data.transcribed_text);
        } catch (err) {
            setError(err.response?.data?.detail || "Couldn't transcrive that recording. Try again, or switch to typing your answer.");
        } finally {
            setTranscribing(false);
        }
    }

    return (
        <div>
            <div className="hero">
                <h1>Lessons</h1>
                <p>Browse lessons, then practice their example phrases by typing or recording your pronounciation.</p>
            </div>
            {error && <div className="error-banner">{error}</div>}

            <div className="chip-bar">
                {LEVELS.map((level) => (
                    <button
                    key={level} className={"quiz-option" + (levelFilter === level ? " selected" : "")}
                    style={{margin: 6}}
                    onClick={() => setLevelFilter(level)}>
                        {level}
                    </button>
                ))}
            </div>

            <div className="card">
                <h3>Practice a phrase</h3>
                {!activePractice ? (
                    <p>Pick "Practice" on any example sentence below to try it here.</p>
                ) : (
                    <>
                        <p>From <b>{activePractice.lessonTitle}</b></p>
                        <p className="case-title">
                            {activePractice.afrikaans}
                            {activePractice.english ? ` (${activePractice.english})` : ""}
                        </p>

                        <div className="quiz-options" style={{flexDirection: "row", marginBottom: 12}}>
                            <button className={"quiz-option" + (inputMode ==="type" ? " selected" : "")}
                            onClick={() => setInputMode("type")}>
                                Type it
                            </button>
                            <button className={"quiz-option" + (inputMode ==="record" ? " selected" : "")}
                            onClick={() => setInputMode("record")}>
                                Record it
                            </button>
                        </div>

                        <form onSubmit={handleScore}>
                            {inputMode === "type" ? (
                                <div className="field">
                                    <label>Your transcript</label>
                                    <input value={transcript} onChange={(e) => setTranscript(e.target.value)}
                                    placeholder="What you said" required />   
                                </div>
                            ) : (
                                <div className="field">
                                <label>Record yourself saying the phrase</label>
                                <div className="quiz-options" style={{flexDirection: "row"}}>
                                    {!isRecording ? (
                                        <button type="button" className="btn btn-primary" onClick={startRecording}>
                                            Start recording
                                        </button>
                                    ) : (
                                        <button type="button" className="btn btn-primary" onClick={stopRecording}>
                                            Stop recording
                                        </button>
                                    )}
                                </div>
                                {transcribing && <p>Transcribing...</p>}
                                {transcript && !transcribing && (
                                    <p>Heard: <i>{transcript}</i></p>
                                )}
                            </div>
                        )}
                        <button className="btn btn-primary" disabled={!transcript || scoring}>
                            {scoring ? "Scoring..." : "Score it"}
                        </button>
                    </form>
                {pronResult && (
                    <div className={"quiz-feedback " + (pronResult.pronounciation_score >= COMPLETE_THRESHOLD ? "correct" : "incorrect")}>
                        <b>{pronResult.pronounciation_score}/100</b> - {pronResult.feedback}
                    </div>
                )}
                {completionMessage && <div className="quiz-feedback correct">{completionMessage}</div>}
            </>
        )}
        </div>

        <div className="section-title">Existing Lessons</div>
        {lessons.length === 0 ? (
            <p>No lessons yet - generate your first lesson above.</p>
        ) : (
            <div className="card-grid">
                {lessons.map((c) => (
                    <div key={c.id} className="card-case">
                        <div className="case-id">
                            {c.level} - {c.topic}
                        </div>
                        <h3 className="case-title">{c.title}</h3>
                        <p>{c.content}</p>
                        {parseExampleSentences(c.example_sentences).map((sentence, i) => (
                            <div key={i} style={{display: "flex", justifyContent: "space-between",
                                alignItems: "center", marginTop: 8,
                            }}>
                                <span>{sentence.afrikaans}
                                    {sentence.english ? ` - ${sentence.english}` : ""}
                                </span>
                                <button className="btn btn-ghost" onClick={() => startPractice(c, sentence)}>
                                    Practice
                                </button>
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        )}
    </div>
    );
}

