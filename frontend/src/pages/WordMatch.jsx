import { useState } from "react";
import api from "../api";
import { useAuth } from "../AuthContext";

const DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"];
const DIRECTIONS = [
    {value: "en_to_af", label: "English -> Afrokaans"},
    {value: "af_to_en", label: "Afrokaans -> English"},
    {value: "mixed", label: "Mixed (random each word)"},
];
const MODES = [
    {value: "multiple_choice", label: "Multiple choice"},
    {value: "free_text", label: "Type the answer"},
];

function recommendedMode(difficulty) {
    if (difficulty === "Advanced") return "free_text";
    return "multiple_choice";
}

export default function WordMath() {
    const { refreshUser } = useAuth();

    const [setupOpen, setSetupOpen] = useState(true);
    const [difficulty, setDifficulty] = useState("Beginner");
    const [direction, setDirection] = useState("mixed");
    const [mode, setMode] = useState(recommendedMode("Beginner"));

    const [word, setWord] = useState(null);
    const [textAnswer, setTextAnswer] = useState("");
    const [selected, setSelected] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [score, setScore] = useState({ correct: 0, total: 0});

    function pickDifficulty(level) {
        setDifficulty(level);
        setMode(recommendedMode(level));
    }

    async function startSession() {
        setSetupOpen(false);
        setScore({correct: 0, total: 0});
        setError("");
        await loadWord();
    }

    async function loadWord() {
        setLoading(true);
        setSelected(null);
        setTextAnswer("");
        setResult(null);
        try {
            const resp = await api.post("/vocab/practice/generate", {difficulty, direction, mode});
            setWord(resp.data);
        } catch {
            setError("Couldn't load a word. Try again.");
        } finally {
            setLoading(false);
        }
    }

    async function submitAnswer(answer) {
        if (result || !answer) return;
        try {
            const resp = await api.post("/vocab/practice/answer", {word_id: word.word_id, direction: word.direction, mode: word.mode, answer,});

            setResult(resp.data);
            setScore((s) => ({
                correct: s.correct + (resp.data.is_correct ? 1 : 0), total: s.total + 1,
            }));
            refreshUser();
        } catch {
            setError("Couldn't grade that answer. Try again.");
            setSelected(null);
        }
    }

    function handleMCSelect(option) {
        setSelected(option);
        submitAnswer(option);
    }

    function handleFreeTextSubmit(e) {
        e.preventDefault();
        submitAnswer(textAnswer);
    }

    function optionClass(option) {
        if (!result) return "quiz-option" + (selected === option ? "selected" : "");
        if (option === result.correct_option) return "quiz-option correct";
        if (option === selected) return "quiz-option incorrect";
        return "quiz-option disabled";
    }

    function endSession(){
        setSetupOpen(true);
        setWord(null);
        setResult(null);
        setError("");
    }

    if (setupOpen) {
        return (
            <div>
                <div className="hero">
                    <h1>Word Match</h1>
                    <p>Drill vocabulary both directions - multiple-choice questions or type the answer yourself. </p>
                </div>
                {error && <div className="error-banner">{error}</div>}
                <div className="card">
                        <div className="form-group">
                            <label className="label">Difficulty</label>
                            <div className="quiz-options">
                                {DIFFICULTIES.map((level) => (
                                    <button 
                                        key={level} 
                                        className={"quiz-option" + (difficulty === level ? " selected" : "")}
                                        onClick={() => pickDifficulty(level)}
                                        > 
                                        {level}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="label">Directions</label>
                            <div className="quiz-options">
                                {DIRECTIONS.map((d) => (
                                    <button 
                                        key={d.value} 
                                        className={"quiz-option" + (direction === d.value ? " selected" : "")}
                                        onClick={() => setDirection(d.value)}
                                        > 
                                        {d.value}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="label">Mode</label>
                            <div className="quiz-options">
                                {MODES.map((m) => (
                                    <button 
                                        key={m.value} 
                                        className={"quiz-option" + (mode === m.value ? " selected" : "")}
                                        onClick={() => setMode(m.value)}
                                        > 
                                        {m.value}
                                    </button>
                                ))}
                            </div>
                        </div>  

                        <button className="btn btn-primary" onClick={startSession}>
                            Start practice
                        </button>  
                    </div>
                </div>
        );
    }

    return (
        <div>
            <div className="hero">
                <h1>Word Match- {difficulty}</h1>
                <p>Score: {score.corrrect} / {score.total} correct</p>
            </div>

            {error && <div className="error-banner">{error}</div>}

            <div className="card">
                {loading || !word ? ( <p>Loading word...</p>
                ) : (
                    <>
                    <div className="case-id">
                        {word.direction === "en_to_af" ? "ENGLISH -> AFRIKAANS" : "AFRIKAANS -> ENGLISH"}
                    </div>
                    <h3 className="case-title">{word.prompt_word}</h3>

                    {word.mode === "multiple_choice" ? (
                        <div className="quiz-options">
                            {word.options.map((option) => (
                                <button 
                                    key={option} className={optionClass(option)}
                                    onClick={() => handleMCSelect(option)} disabled={!!result}>
                                        {option}
                                    </button>
                            ))}
                        </div>
                    ) : (
                        <form onSubmit={handleFreeTextSubmit}>
                            <div className="form-group">
                                <label className="label">Your answer</label>
                                <input type="text" value={textAnswer} onChange={(e) => setTextAnswer(e.target.value)}
                                  disabled={!!result} placeholder="Type your answer..." autoFocus/>
                            </div>

                            {!result && (
                                <button type="submit" className="btn btn-primary">
                                    Submit
                                </button>
                            )}
                        </form>
                    )}    

                    {result && (
                        <div className={"quiz-feedback " + (result.is_correct ? "correct" : "incorrect")}>
                            <b>{result.is_correct ? `Correct! +${result.xp_awarded} XP` : "Not quite."}</b>
                            {!result.is_correct && (
                                <p>The right answer was <b>{result.correct_answer}</b>.</p>
                            )}
                            {result.similarity != null && (
                                <p>Similarity: {Math.round(result.similarity * 100)}%</p>
                            )}
                        </div>
                    )}

                    <div className="quiz-actions">
                        {result ? (
                            <button className="btn btn-primary" onClick={loadWord}>
                                Next word
                            </button>
                        ) : null}
                        <button className="btn btn-ghost" onClick={endSession}>
                            End Session
                        </button>
                    </div>
                    </>
                )}
            </div>
        </div>
    );
}
