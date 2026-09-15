import {Routes, Route, Navigate, Link, useLocation } from "react-router-dom";
import {AuthProvider, useAuth } from "./AuthContext";
import Login from "./pages/Login";
import Dashboard from './pages/Dashboard';
import Registration from './pages/Registration';
import Lessons from './pages/Lessons';
import Leaderboard from './pages/Leaderboard';
import Quiz from './pages/Quiz';
import WordMatch from './pages/WordMatch';

function TopBar() {
    const {user, logout} = useAuth();
    const location = useLocation();
    const isActive = (path)=> location.pathname === path;

    return (
        <div className="app-topbar">
            <Link to="/" className="topbar-brand">
                <span className="brand-mrk">[]</span>
                QUEST_AFRIKAANS
            </Link>
            {user && (
                <>
                    <div className="nav-links">
                        <Link to="/dashboard" className={isActive("/dashboard") ? "active" : ""}>Dasboard</Link> 
                        <Link to="/lessons" className={isActive("/lessons") ? "active" : ""}>Lessons</Link> 
                        <Link to="/quiz" className={isActive("/quiz") ? "active" : ""}>Quiz</Link>
                        <Link to="/word-match" className={isActive("/word-match") ? "active" : ""}>Word Match</Link>
                        <Link to="/leaderboard" className={isActive("/leaderboard") ? "active" : ""}>Leaderboard</Link> 
                    </div>
                    <div className="stat-pill">
                        <span>Lv. <b>{user.level}</b></span>
                        <span><b>{user.xp}</b> XP</span>
                        <span><b>{user.streak}</b></span>
                        <button className="btn btn-ghost" onClick={logout}>Sign out</button>
                    </div>
                </>
            )}
        </div>
    );
}

function PrivateRoute({ children}) {
    const { user, loading} = useAuth();
    if (loading) {
        return (<div>Loading...</div>);
    }
    if (!user) {
        return (<Navigate to="/login" replace/>);
    }
    return children;
}

function AppRoutes() {
    const {user, loading} = useAuth();
    return (
        <div className="shell">
            <TopBar />
            <main className="content">
                <Routes>
                    <Route path='/' element={loading ? null: <Navigate to={user ? "/dashboard" : "/login"} replace />} />
                    <Route path='/register' element={<Registration/>}/>
                    <Route path='/login' element={<Login/>}/>
                    <Route path="/dashboard" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
                    <Route path="/lessons" element={<PrivateRoute><Lessons /></PrivateRoute>} />
                    <Route path="/quiz" element={<PrivateRoute><Quiz /></PrivateRoute>} />
                    <Route path="/word-match" element={<PrivateRoute><WordMatch /></PrivateRoute>} />
                    <Route path="/leaderboard" element={<PrivateRoute><Leaderboard /></PrivateRoute>} />
                </Routes>
            </main>
        </div>
    );
}

export default function App() {
    return (
        <AuthProvider>
            <AppRoutes />
        </AuthProvider>
    );
}