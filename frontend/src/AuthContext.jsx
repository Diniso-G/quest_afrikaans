import { createContext, useContext, useState, useEffect, useCallback } from "react";
import api from "./api";

const AuthContext = createContext(null);

export function AuthProvider({children}) {
    const [token, setToken] = useState(() => localStorage.getItem("akq_token"));
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    const refreshUser = useCallback(async () => {
/*        
        if (!localStorage.getItem("afq_token")) {
            setUser(null);
            setLoading(false);
            return;
        }
        try {
            const resp = await api.get("/user/me");
            setUser(resp.data);
        }
        catch {
            logout();
        } finally {
            setLoading(false);
        }*/
       setLoading(false);
    }, []);

    useEffect(() => {
        refreshUser() }, [refreshUser]);

    function login(newToken) {
        localStorage.setItem("akq_token", newToken);
        //setToken(newToken);
        //refreshUser();
        setUser({ loggedIn: true});
    }

    function logout() {
        localStorage.removeItem("akq_token");
        //setToken(null);
        setUser(null);
    }

    return (
        <AuthContext.Provider value={{ token, user, loading, login, logout, refreshUser}}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}