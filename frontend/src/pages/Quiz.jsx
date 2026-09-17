import { useState } from "react";
import api from "../api";
import { useAuth } from "../AuthContext";

const DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"];

export default function Quiz() {
    const {refreshUser } = useAuth();

    const [difficulty, setDifficulty] = useState(null);
    const [question, setQuestion] = useState(null);
    const [selected, setSelected] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [score, setScore] = useState({ correct: 0, total: 0});

    async function startQuiz(level) {
        setDifficulty(level);
        setScore({correct: 0, total: 0});
        setError("");
        await loadQuestion(level);
    }
    async function loadQuestion(level) {
        setLoading(true);
        setSelected(null);
        setResult(null);
        try {
            const resp = await api.post("/quiz/generate", {difficulty: level || difficulty});
            setQuestion(resp.data);
        } catch {
            setError("Couldn't generate a question. Try again.");
        } finally {
            setLoading(false);
        }
    }

    async function handAnswer(option) {
        if (result) return;
        setSelected(option);
        try {
            const resp = await api.post("/quiz/answer", {question_id: question.id, selected_option: option,});

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

    function optionClass(option) {
        if (!result) return "quiz-option" + (selected === option ? " selected" : "");
        if (option === result.correct_option) return "quiz-option correct";
        if (option === selected) return "quiz-option incorrect";
        return "quiz-option disabled";
    }

    function endSession(){
        setDifficulty(null);
        setQuestion(null);
        setSelected(null);
        setResult(null);
        setError("");
    }

    if (!difficulty) {
        return (
            <div>
                <div className="hero">
                    <h1>Quiz</h1>
                    <p>Pick a difficulty to start a round of multiple-choice questions. </p>
                </div>
                {error && <div className="error-banner">{error}</div>}
                <div className="card-grid">
                    {DIFFICULTIES.map((level) => (
                        <div key={level} className="card-case" onClick={() => startQuiz(level)} style={{ cursor: "pointer"}}>
                            <div className="case-id">DIFFICULTY</div>
                            <h3 className="case-title">{level}</h3>
                            <p>
                                {level === "Beginner" && "Single common words, obviously distinct options."}
                                {level === "Intermediate" && "Short phrases with a few near-miss distractors."}
                                {level === "Advanced" && "Indions and sentences-level translation."}
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div>
            <div className="hero">
                <h1>Quiz - {difficulty}</h1>
                <p>Score: {score.correct} / {score.total} correct</p>
            </div>

            {error && <div className="error-banner">{error}</div>}

            <div className="card">
                {loading || !question ? ( <p>Loading question...</p>
                ) : (
                    <>
                        <h3 className="case-title">{question.prompt_text}</h3>

                        <div className="quiz-options">
                            {question.options.map((option) => (
                                <button key={option} className={optionClass(option)} onClick={() => handAnswer(option)} disabled={!!result}> {option}</button>
                            ))}
                        </div>

                        {result && (
                            <div className={"quiz-feedback " + (result.is_correct ? "correct" : "incorrect")}>
                                <b>{result.is_correct ? `Correct! +${result.xp_awarded} XP` : "Not quite."}</b>
                                {!result.is_correct && (
                                    <p>The right answer was <b>{result.correct_option}</b>.</p>
                                )}
                                {result.explanation && <p>{result.explanation}</p>}
                            </div>
                        )}

                        <div className="quiz-actions">
                            {result ? (
                                <button className="btn btn-primary" onClick={() => loadQuestion()}>
                                    Next Question
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
