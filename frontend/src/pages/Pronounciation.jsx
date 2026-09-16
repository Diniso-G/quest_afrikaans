import { useRef, useState } from "react";
import api from "../api";

const SUGGESTED_PHRASES = [
    "Hallo, hoe gaan dit?", "Goeie môre", "Dankie",
    "Totsiens", "Ek is honger",
];

export default function Pronounciation() {
    const [targetPhrase, setTargetPhrase] = useState("");
    const [transcript, setTranscript] = useState("");
    const [pronResult, setPronResult] = useState(null);
    const [inputMode, setInputMode] = useState("type");
    
    const [isRecording, setIsRecording] = useState(false);
    const [transcribing, setTranscribing] = useState(false);
    const mediaRecorderRef = useRef(null);
    const [error, setError] = useState("");
    const [scoring, setScoring] = useState(false);
    const chunksRef = useRef([]);

    async function handleScore(e) {
        e?.preventDefault()
        if (!activePractice || !transcript) return;
        setScoring(true);
        setError("");
        try {
            const resp = await api.post("/speech/score", { target_phrase: targetPhrase, transcribed_text: transcript});
            setPronResult(resp.data);
        }
        catch {
            setError("Couldn't score pronounciation. Try again")
        } finally {
            setScoring(false);
        }
    }    
    async function startRecording() {
        setError("");
        setPronResult(null);
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
                <h1>Pronounciation Practice</h1>
                <p>Pick or type any Afrikaans phrase, say it out loud, and get scored on how close you were.</p>
            </div>
            {error && <div className="error-banner">{error}</div>}

            <div className="card">
                <div className="form-group">
                    <label className="label">Phrase to practice</label>
                    <input value={targetPhrase} onChange={(e) => { setTargetPhrase(e.target.value); setTranscript(""); setPronResult(null);}} placeholder="Type an Afrikaans phrase..."/>
                </div>

                <div className="quiz-options" style={{flexDirection: "row", flexWrap: "wrap", marginBottom: 16}}>
                    {SUGGESTED_PHRASES.map((phrase) => (
                        <button key={phrase} className={"quiz-option" + (targetPhrase === phrase ? " selected" : "")}
                        onClick={() => pickSuggestion(phrase)}>
                            {phrase}
                        </button>
                    ))}
                </div>

                {targetPhrase && (
                    <>
                        <div className="quiz-options" style={{flexDirection: "row", marginBottom: 12}}>
                            <button className={"quiz-option" + (inputMode === "type" ? " selected" : "")} onClick={() => setInputMode("type")}>
                                Type it
                            </button>
                            <button className={"quiz-option" + (inputMode === "record" ? " selected" : "")} onClick={() => setInputMode("record")}>
                                Record it
                            </button>
                        </div>

                        <form onSubmit={handleScore}>
                            {inputMode === "type" ? (
                                <div className="form-group">
                                    <label className="label">Your Transcript</label>
                                    <input value={transcript} onChange={(e) => setTranscript(e.target.value)} placeholder="What you said" required />
                                </div>
                            ) : (
                                <div className="form-group">
                                    <label className="label">Record yourself saying the phrase</label>
                                    <div className="quiz-options" style={{flexDirection: "row"}}>
                                        {!isRecording ? (
                                            <button type="button" className="btn btn-primary" onClick={startRecording}>
                                                Start Recording
                                            </button>
                                        ) : (
                                            <button type="button" className="btn btn-primary" onClick={stopRecording}>
                                                Stop Recording
                                            </button>
                                        )}
                                    </div>
                                    {transcribing && <p>Transcribing...</p>}
                                    {transcript && !transcribing && (
                                        <p> Heard: <i>{transcript}</i></p>
                                    )}
                                </div>
                            )}

                            <button className="btn btn-primary" disabled={!transcript || scoring}>
                                {scoring ? "Scoring..." : "Score it"}
                            </button>
                        </form>

                        {pronResult && (
                            <div className={"quiz-feedback " + (pronResult.pronounciation_score >= 70 ? "correct" : "incorrect")}>
                                <b>{pronResult.pronounciation_score}/100</b> - {pronResult.feedback}
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
