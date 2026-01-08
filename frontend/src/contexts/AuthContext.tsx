
import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, Session, AuthError } from '@supabase/supabase-js';
import { supabase } from '@/services/supabase';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

interface AuthContextType {
    user: User | null;
    session: Session | null;
    loading: boolean;
    isDemo: boolean;
    signInWithDemo: () => void;
    signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    session: null,
    loading: true,
    isDemo: false,
    signInWithDemo: () => { },
    signOut: async () => { },
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [session, setSession] = useState<Session | null>(null);
    const [loading, setLoading] = useState(true);
    const [isDemo, setIsDemo] = useState(false);

    useEffect(() => {
        // Check for demo mode in localStorage
        const savedDemo = localStorage.getItem('finbro_demo_mode');
        if (savedDemo === 'true') {
            setIsDemo(true);
            setLoading(false);
            return;
        }

        // Check active sessions and subscribe to auth changes
        const initAuth = async () => {
            try {
                const { data: { session: initialSession } } = await supabase.auth.getSession();
                setSession(initialSession);
                setUser(initialSession?.user ?? null);

                const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
                    setSession(session);
                    setUser(session?.user ?? null);
                    setLoading(false);

                    if (session) {
                        localStorage.removeItem('finbro_demo_mode');
                        setIsDemo(false);
                    }
                });

                return () => subscription.unsubscribe();
            } catch (error) {
                console.error('Auth initialization error:', error);
            } finally {
                setLoading(false);
            }
        };

        initAuth();
    }, []);

    const signInWithDemo = () => {
        setIsDemo(true);
        localStorage.setItem('finbro_demo_mode', 'true');
        toast.success("Welcome to Demo Mode! You can explore freely.");
    };

    const signOut = async () => {
        if (isDemo) {
            setIsDemo(false);
            localStorage.removeItem('finbro_demo_mode');
            toast.success("Exited Demo Mode");
        } else {
            const { error } = await supabase.auth.signOut();
            if (error) {
                toast.error(`Error signing out: ${error.message}`);
            } else {
                toast.success("Signed out successfully");
            }
        }
    };

    const value = {
        user,
        session,
        loading,
        isDemo,
        signInWithDemo,
        signOut,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
