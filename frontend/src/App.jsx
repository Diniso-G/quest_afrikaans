import {Routes, Route, Navigate, Link, useLocation } from "react-router-dom";
import {AuthProvider, useAuth } from "./AuthContext";
import Login from "./pages/Login";
import Dashboard from './pages/Dashboard';
import Registration from './pages/Registration';

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