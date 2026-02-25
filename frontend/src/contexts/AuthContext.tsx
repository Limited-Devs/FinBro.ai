
import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { User, Session } from '@supabase/supabase-js';
import { supabase } from '@/services/supabase';
import { toast } from 'sonner';
import { onboardingAPI } from '@/services/api';

interface AuthContextType {
    user: User | null;
    session: Session | null;
    loading: boolean;
    isDemo: boolean;
    onboardingCompleted: boolean;
    checkOnboardingStatus: () => Promise<void>;
    setOnboardingCompleted: (completed: boolean) => void;
    signInWithDemo: () => void;
    signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    session: null,
    loading: true,
    isDemo: false,
    onboardingCompleted: false,
    checkOnboardingStatus: async () => { },
    setOnboardingCompleted: () => { },
    signInWithDemo: () => { },
    signOut: async () => { },
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [session, setSession] = useState<Session | null>(null);
    const [loading, setLoading] = useState(true);
    const [isDemo, setIsDemo] = useState(false);
    const [onboardingCompleted, setOnboardingCompletedState] = useState(false);

    // Check onboarding status from backend
    const checkOnboardingStatus = useCallback(async () => {
        if (isDemo) {
            setOnboardingCompletedState(true);
            return;
        }

        try {
            const status = await onboardingAPI.getStatus();
            setOnboardingCompletedState(status.onboarding_completed);
        } catch (error) {
            console.error('Error checking onboarding status:', error);
            // Assume not onboarded on error (will redirect to onboarding)
            setOnboardingCompletedState(false);
        }
    }, [isDemo]);

    // Allow manual setting of onboarding status (called after completing onboarding)
    const setOnboardingCompleted = useCallback((completed: boolean) => {
        setOnboardingCompletedState(completed);
    }, []);

    useEffect(() => {
        // Always check active sessions and subscribe to auth changes
        // This ensures the auth listener is registered even if demo mode was previously set
        const initAuth = async () => {
            try {
                const { data: { session: initialSession } } = await supabase.auth.getSession();
                setSession(initialSession);
                setUser(initialSession?.user ?? null);

                // If we have an active session, clear any leftover demo mode
                if (initialSession?.user) {
                    localStorage.removeItem('finbro_demo_mode');
                    setIsDemo(false);

                    // Check onboarding status for logged in user
                    try {
                        const status = await onboardingAPI.getStatus();
                        setOnboardingCompletedState(status.onboarding_completed);
                    } catch (error) {
                        console.error('Error checking onboarding status:', error);
                        setOnboardingCompletedState(false);
                    }
                } else {
                    // No active session - check if demo mode was previously enabled
                    const savedDemo = localStorage.getItem('finbro_demo_mode');
                    if (savedDemo === 'true') {
                        setIsDemo(true);
                        setOnboardingCompletedState(true); // Demo users are always "onboarded"
                    }
                }

                // Always register the auth state change listener
                const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, session) => {
                    setSession(session);
                    setUser(session?.user ?? null);

                    if (session) {
                        // Real user logged in - clear demo mode
                        localStorage.removeItem('finbro_demo_mode');
                        setIsDemo(false);

                        const status = await onboardingAPI.getStatus();
                        setOnboardingCompletedState(status.onboarding_completed);
                    } else {
                        // User logged out
                        setOnboardingCompletedState(false);
                    }

                    setLoading(false);
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
        setOnboardingCompletedState(true); // Demo users are always "onboarded"
        localStorage.setItem('finbro_demo_mode', 'true');
        toast.success("Welcome to Demo Mode! You can explore freely.");
    };

    const signOut = async () => {
        if (isDemo) {
            setIsDemo(false);
            setOnboardingCompletedState(false);
            localStorage.removeItem('finbro_demo_mode');
            toast.success("Exited Demo Mode");
        } else {
            const { error } = await supabase.auth.signOut();
            if (error) {
                toast.error(`Error signing out: ${error.message}`);
            } else {
                setOnboardingCompletedState(false);
                toast.success("Signed out successfully");
            }
        }
    };

    const value = {
        user,
        session,
        loading,
        isDemo,
        onboardingCompleted,
        checkOnboardingStatus,
        setOnboardingCompleted,
        signInWithDemo,
        signOut,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
