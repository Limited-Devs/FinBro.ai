
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "./contexts/ThemeContext";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import Layout from "./components/Layout";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import Analytics from "./pages/Analytics";
import Expenses from "./pages/Expenses";
import Savings from "./pages/Savings";
import Chat from "./pages/Chat";
import Profile from "./pages/Profile";
import FinancialReport from "./pages/FinancialReport";
import NotFound from "./pages/NotFound";
import Login from "./pages/Auth/Login";
import Signup from "./pages/Auth/Signup";
import Onboarding from "./pages/Onboarding";

const queryClient = new QueryClient();

// Route that requires authentication only
const PrivateRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, isDemo, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (!user && !isDemo) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Route that requires authentication AND completed onboarding
const OnboardedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, isDemo, onboardingCompleted, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    );
  }

  // Must be authenticated
  if (!user && !isDemo) {
    return <Navigate to="/login" replace />;
  }

  // Demo users skip onboarding
  if (isDemo) {
    return <>{children}</>;
  }

  // Authenticated users must complete onboarding
  if (!onboardingCompleted) {
    return <Navigate to="/onboarding" replace />;
  }

  return <>{children}</>;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider>
      <TooltipProvider>
        <AuthProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<Landing />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />

              {/* Onboarding - requires auth but not onboarding completion */}
              <Route path="/onboarding" element={<PrivateRoute><Onboarding /></PrivateRoute>} />

              {/* Protected routes - require auth AND onboarding */}
              <Route path="/dashboard" element={<OnboardedRoute><Layout><Dashboard /></Layout></OnboardedRoute>} />
              <Route path="/analytics" element={<OnboardedRoute><Layout><Analytics /></Layout></OnboardedRoute>} />
              <Route path="/expenses" element={<OnboardedRoute><Layout><Expenses /></Layout></OnboardedRoute>} />
              <Route path="/savings" element={<OnboardedRoute><Layout><Savings /></Layout></OnboardedRoute>} />
              <Route path="/chat" element={<OnboardedRoute><Layout><Chat /></Layout></OnboardedRoute>} />
              <Route path="/profile" element={<OnboardedRoute><Layout><Profile /></Layout></OnboardedRoute>} />
              <Route path="/financial-report" element={<OnboardedRoute><Layout><FinancialReport /></Layout></OnboardedRoute>} />

              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
