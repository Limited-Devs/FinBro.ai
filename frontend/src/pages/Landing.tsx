import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ArrowRight, Sparkles, TrendingUp, Shield, Brain, MessageCircle, ChevronDown, Check, Plus, Minus } from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════════════
// STYLES - Playful Maximalist Theme (Content on Demand inspired)
// ═══════════════════════════════════════════════════════════════════════════

const colors = {
    purple: '#8B5CF6',
    purpleDark: '#7C3AED',
    peach: '#FECACA',
    salmon: '#FED7AA',
    mint: '#A7F3D0',
    yellow: '#FEF08A',
    white: '#FFFFFF',
    black: '#0F0F0F',
    gray: '#6B7280',
};

// ═══════════════════════════════════════════════════════════════════════════
// FLOATING CARD COMPONENT - Tilted scattered cards
// ═══════════════════════════════════════════════════════════════════════════

interface FloatingCardProps {
    children: React.ReactNode;
    rotation: number;
    className?: string;
    delay?: number;
}

const FloatingCard = ({ children, rotation, className = '', delay = 0 }: FloatingCardProps) => {
    const [isVisible, setIsVisible] = useState(false);
    const ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    setTimeout(() => setIsVisible(true), delay);
                }
            },
            { threshold: 0.1 }
        );

        if (ref.current) observer.observe(ref.current);
        return () => observer.disconnect();
    }, [delay]);

    return (
        <div
            ref={ref}
            className={`
        bg-white rounded-2xl shadow-xl border-2 border-black p-6
        transition-all duration-700 ease-out
        ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}
        ${className}
      `}
            style={{
                transform: isVisible ? `rotate(${rotation}deg)` : `rotate(${rotation}deg) translateY(20px)`,
                boxShadow: '8px 8px 0 0 #0F0F0F',
            }}
        >
            {children}
        </div>
    );
};

// ═══════════════════════════════════════════════════════════════════════════
// FAQ ACCORDION COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

interface FAQItemProps {
    question: string;
    answer: string;
}

const FAQItem = ({ question, answer }: FAQItemProps) => {
    const [isOpen, setIsOpen] = useState(false);

    return (
        <div className="border-b-2 border-black">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="w-full py-6 flex items-center justify-between text-left hover:bg-gray-50 transition-colors px-2"
            >
                <span className="text-xl font-bold text-black pr-4">{question}</span>
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-[#8B5CF6] flex items-center justify-center">
                    {isOpen ? (
                        <Minus className="w-5 h-5 text-white" />
                    ) : (
                        <Plus className="w-5 h-5 text-white" />
                    )}
                </div>
            </button>
            <div
                className={`overflow-hidden transition-all duration-300 ${isOpen ? 'max-h-96 pb-6' : 'max-h-0'
                    }`}
            >
                <p className="text-gray-600 text-lg px-2">{answer}</p>
            </div>
        </div>
    );
};

// ═══════════════════════════════════════════════════════════════════════════
// MAIN LANDING COMPONENT
// ═══════════════════════════════════════════════════════════════════════════

const Landing = () => {
    const [heroVisible, setHeroVisible] = useState(false);

    useEffect(() => {
        setTimeout(() => setHeroVisible(true), 100);
    }, []);

    return (
        <div className="min-h-screen bg-white overflow-x-hidden" style={{ fontFamily: "'Outfit', sans-serif" }}>

            {/* ═══════════════════════════════════════════════════════════════════
          NAVIGATION
          ═══════════════════════════════════════════════════════════════════ */}
            <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-sm border-b-2 border-black">
                <div className="container mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <div
                            className="w-10 h-10 rounded-xl flex items-center justify-center font-black text-white text-xl"
                            style={{ backgroundColor: colors.purple }}
                        >
                            F
                        </div>
                        <span className="text-2xl font-black text-black">FinBro</span>
                    </div>
                    <div className="hidden md:flex items-center gap-8">
                        <a href="#features" className="text-black font-semibold hover:text-[#8B5CF6] transition-colors">Features</a>
                        <a href="#how-it-works" className="text-black font-semibold hover:text-[#8B5CF6] transition-colors">How it works</a>
                        <a href="#pricing" className="text-black font-semibold hover:text-[#8B5CF6] transition-colors">Pricing</a>
                    </div>
                    <Link to="/dashboard">
                        <Button
                            className="bg-black text-white font-bold px-6 py-2 rounded-full hover:bg-[#8B5CF6] transition-colors border-2 border-black"
                            style={{ boxShadow: '4px 4px 0 0 #8B5CF6' }}
                        >
                            Get Started →
                        </Button>
                    </Link>
                </div>
            </nav>

            {/* ═══════════════════════════════════════════════════════════════════
          HERO SECTION - Purple Background
          ═══════════════════════════════════════════════════════════════════ */}
            <section
                className="min-h-screen pt-32 pb-20 px-6 relative overflow-hidden"
                style={{ backgroundColor: colors.purple }}
            >
                {/* Decorative elements */}
                <div className="absolute top-40 left-10 w-20 h-20 bg-yellow-300 rounded-full opacity-80" />
                <div className="absolute bottom-40 right-20 w-16 h-16 bg-green-300 rounded-full opacity-80" />
                <div className="absolute top-60 right-40 text-6xl">✨</div>
                <div className="absolute bottom-60 left-40 text-5xl">💰</div>

                <div className="container mx-auto relative z-10">
                    <div className="grid lg:grid-cols-2 gap-12 items-center">
                        {/* Left Column - Text */}
                        <div className="space-y-8">
                            <h1
                                className={`
                  text-6xl sm:text-7xl lg:text-8xl font-black leading-[0.9] text-white
                  tracking-tight uppercase
                  transition-all duration-700 delay-100
                  ${heroVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}
                `}
                                style={{ fontFamily: "'Outfit', sans-serif" }}
                            >
                                YOUR<br />
                                MONEY,<br />
                                <span className="text-black">DECODED.</span>
                            </h1>

                            <p
                                className={`
                  text-xl text-white/90 max-w-md leading-relaxed
                  transition-all duration-700 delay-200
                  ${heroVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'}
                `}
                            >
                                We take your financial stress away, so you can focus on the bigger picture.
                            </p>

                            <div
                                className={`
                  flex flex-wrap gap-4
                  transition-all duration-700 delay-300
                  ${heroVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6'}
                `}
                            >
                                <Link to="/dashboard">
                                    <Button
                                        size="lg"
                                        className="bg-black text-white font-bold px-8 py-6 text-lg rounded-full hover:bg-white hover:text-black transition-all border-2 border-black"
                                        style={{ boxShadow: '6px 6px 0 0 #FEF08A' }}
                                    >
                                        Get Started Free
                                        <ArrowRight className="ml-2 w-5 h-5" />
                                    </Button>
                                </Link>
                            </div>
                        </div>

                        {/* Right Column - Floating Cards */}
                        <div
                            className={`
                relative h-[500px] hidden lg:block
                transition-all duration-1000 delay-400
                ${heroVisible ? 'opacity-100' : 'opacity-0'}
              `}
                        >
                            <FloatingCard rotation={-6} className="absolute top-0 left-0 w-64" delay={200}>
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                                        <TrendingUp className="w-5 h-5 text-green-600" />
                                    </div>
                                    <span className="font-bold text-black">Portfolio Growth</span>
                                </div>
                                <div className="text-3xl font-black text-black">+24.5%</div>
                                <div className="text-gray-500 text-sm">This month</div>
                            </FloatingCard>

                            <FloatingCard rotation={4} className="absolute top-20 right-0 w-72" delay={400}>
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
                                        <Brain className="w-5 h-5 text-purple-600" />
                                    </div>
                                    <span className="font-bold text-black">AI Insights</span>
                                </div>
                                <p className="text-gray-600 text-sm">
                                    "Based on your spending, you could save an extra
                                    <span className="text-[#8B5CF6] font-bold"> $340/month</span>
                                    by optimizing subscriptions."
                                </p>
                            </FloatingCard>

                            <FloatingCard rotation={-3} className="absolute bottom-20 left-10 w-60" delay={600}>
                                <div className="flex items-center gap-3 mb-3">
                                    <div className="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
                                        <Shield className="w-5 h-5 text-yellow-600" />
                                    </div>
                                    <span className="font-bold text-black">Risk Score</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="text-2xl font-black text-green-500">LOW</div>
                                    <div className="text-gray-400">•</div>
                                    <div className="text-sm text-gray-500">Well balanced</div>
                                </div>
                            </FloatingCard>

                            <FloatingCard rotation={8} className="absolute bottom-0 right-10 w-48" delay={800}>
                                <div className="text-center">
                                    <div className="text-4xl mb-2">🎯</div>
                                    <div className="font-bold text-black">Goals Met</div>
                                    <div className="text-2xl font-black text-[#8B5CF6]">3/4</div>
                                </div>
                            </FloatingCard>
                        </div>
                    </div>
                </div>

                {/* Scroll indicator */}
                <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
                    <ChevronDown className="w-8 h-8 text-white/70" />
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════════
          FEATURES SECTION - Peach Background
          ═══════════════════════════════════════════════════════════════════ */}
            <section
                id="features"
                className="py-32 px-6 relative"
                style={{ backgroundColor: '#FED7AA' }}
            >
                <div className="container mx-auto">
                    <div className="grid lg:grid-cols-2 gap-16 items-center">
                        {/* Left - Big Text */}
                        <div>
                            <h2 className="text-5xl sm:text-6xl lg:text-7xl font-black text-black leading-[0.95] uppercase">
                                5, 4, 3, 2, 1<br />
                                That's how quickly<br />
                                we analyze<br />
                                <span style={{ color: colors.purple }}>your finances!</span>
                            </h2>
                            <p className="mt-8 text-xl text-gray-700 max-w-md">
                                Our AI-powered engine scans through 45+ financial parameters in seconds,
                                giving you insights that typically take financial advisors days to compile.
                            </p>
                            <Link to="/financial-report">
                                <Button
                                    className="mt-8 bg-black text-white font-bold px-8 py-4 text-lg rounded-full hover:bg-[#8B5CF6] transition-all border-2 border-black"
                                    style={{ boxShadow: '5px 5px 0 0 #8B5CF6' }}
                                >
                                    Try AI Report →
                                </Button>
                            </Link>
                        </div>

                        {/* Right - Feature Cards Stack */}
                        <div className="relative">
                            <FloatingCard rotation={-4} className="relative z-10" delay={100}>
                                <div className="flex items-start gap-4">
                                    <div className="w-12 h-12 rounded-xl bg-[#8B5CF6] flex items-center justify-center flex-shrink-0">
                                        <Sparkles className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-xl text-black mb-2">Smart Predictions</h3>
                                        <p className="text-gray-600">ML models trained on millions of data points to predict your savings potential.</p>
                                    </div>
                                </div>
                            </FloatingCard>

                            <FloatingCard rotation={3} className="relative z-20 -mt-4 ml-8" delay={250}>
                                <div className="flex items-start gap-4">
                                    <div className="w-12 h-12 rounded-xl bg-green-400 flex items-center justify-center flex-shrink-0">
                                        <TrendingUp className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-xl text-black mb-2">Expense Tracking</h3>
                                        <p className="text-gray-600">Automatic categorization and smart insights on where your money goes.</p>
                                    </div>
                                </div>
                            </FloatingCard>

                            <FloatingCard rotation={-2} className="relative z-30 -mt-4 mr-8" delay={400}>
                                <div className="flex items-start gap-4">
                                    <div className="w-12 h-12 rounded-xl bg-yellow-400 flex items-center justify-center flex-shrink-0">
                                        <MessageCircle className="w-6 h-6 text-black" />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-xl text-black mb-2">AI Chat Assistant</h3>
                                        <p className="text-gray-600">Ask anything about your finances. Get instant, personalized answers.</p>
                                    </div>
                                </div>
                            </FloatingCard>
                        </div>
                    </div>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════════
          HOW IT WORKS SECTION - White Background
          ═══════════════════════════════════════════════════════════════════ */}
            <section id="how-it-works" className="py-32 px-6 bg-white relative">
                <div className="absolute top-20 right-20 text-6xl">🤔</div>
                <div className="container mx-auto">
                    <div className="grid lg:grid-cols-2 gap-16 items-center">
                        {/* Left - Cards */}
                        <div className="space-y-6">
                            <FloatingCard rotation={-2} delay={0}>
                                <div className="flex items-center gap-4">
                                    <div className="w-14 h-14 rounded-full bg-[#8B5CF6] flex items-center justify-center text-white font-black text-2xl">
                                        1
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-xl text-black">Connect your accounts</h3>
                                        <p className="text-gray-600">Securely link your bank and investment accounts.</p>
                                    </div>
                                </div>
                            </FloatingCard>

                            <FloatingCard rotation={1} delay={150}>
                                <div className="flex items-center gap-4">
                                    <div className="w-14 h-14 rounded-full bg-green-400 flex items-center justify-center text-white font-black text-2xl">
                                        2
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-xl text-black">AI analyzes your data</h3>
                                        <p className="text-gray-600">Our ML models crunch 45+ financial parameters.</p>
                                    </div>
                                </div>
                            </FloatingCard>

                            <FloatingCard rotation={-1} delay={300}>
                                <div className="flex items-center gap-4">
                                    <div className="w-14 h-14 rounded-full bg-yellow-400 flex items-center justify-center text-black font-black text-2xl">
                                        3
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-xl text-black">Get personalized insights</h3>
                                        <p className="text-gray-600">Receive actionable advice tailored to your goals.</p>
                                    </div>
                                </div>
                            </FloatingCard>
                        </div>

                        {/* Right - Text */}
                        <div>
                            <h2 className="text-5xl sm:text-6xl font-black text-black leading-[0.95]">
                                I'm intrigued.<br />
                                <span style={{ color: colors.purple }}>How does this work?</span>
                            </h2>
                            <p className="mt-8 text-xl text-gray-600 max-w-md">
                                We've made financial intelligence accessible to everyone. No complex spreadsheets,
                                no expensive advisors. Just smart AI that works for you.
                            </p>
                            <Link to="/chat">
                                <Button
                                    className="mt-8 bg-white text-black font-bold px-8 py-4 text-lg rounded-full hover:bg-[#8B5CF6] hover:text-white transition-all border-2 border-black"
                                    style={{ boxShadow: '5px 5px 0 0 #0F0F0F' }}
                                >
                                    Chat with AI →
                                </Button>
                            </Link>
                        </div>
                    </div>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════════
          TESTIMONIALS SECTION - Purple Background
          ═══════════════════════════════════════════════════════════════════ */}
            <section className="py-24 px-6" style={{ backgroundColor: colors.purple }}>
                <div className="container mx-auto text-center">
                    <h2 className="text-4xl sm:text-5xl font-black text-white mb-4">
                        Praises? We've Collected A Few. ⭐
                    </h2>
                    <p className="text-xl text-white/80 mb-16 max-w-2xl mx-auto">
                        Join thousands who've transformed their financial lives
                    </p>

                    <div className="grid md:grid-cols-3 gap-8">
                        <FloatingCard rotation={-3} delay={0}>
                            <div className="text-left">
                                <div className="text-4xl mb-4">💸</div>
                                <p className="text-gray-700 mb-4">"Saved $2,400 in my first 3 months just by following the AI suggestions."</p>
                                <div className="font-bold text-black">— Sarah K.</div>
                            </div>
                        </FloatingCard>

                        <FloatingCard rotation={2} delay={150}>
                            <div className="text-left">
                                <div className="text-4xl mb-4">🚀</div>
                                <p className="text-gray-700 mb-4">"Finally understand where my money goes. The dashboard is incredibly intuitive."</p>
                                <div className="font-bold text-black">— Marcus T.</div>
                            </div>
                        </FloatingCard>

                        <FloatingCard rotation={-2} delay={300}>
                            <div className="text-left">
                                <div className="text-4xl mb-4">🎯</div>
                                <p className="text-gray-700 mb-4">"The AI chat is like having a financial advisor in my pocket 24/7."</p>
                                <div className="font-bold text-black">— Emma L.</div>
                            </div>
                        </FloatingCard>
                    </div>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════════
          FAQ SECTION - Mint Background
          ═══════════════════════════════════════════════════════════════════ */}
            <section className="py-32 px-6" style={{ backgroundColor: '#A7F3D0' }}>
                <div className="container mx-auto">
                    <div className="grid lg:grid-cols-2 gap-16">
                        {/* Left - Title */}
                        <div>
                            <h2 className="text-5xl sm:text-6xl font-black text-black leading-[0.95]">
                                Have more<br />
                                questions?<br />
                                <span style={{ color: colors.purple }}>We've got you!</span> 🙋
                            </h2>
                        </div>

                        {/* Right - FAQ Accordion */}
                        <div className="bg-white rounded-2xl border-2 border-black p-6" style={{ boxShadow: '8px 8px 0 0 #0F0F0F' }}>
                            <FAQItem
                                question="How does FinBro.ai analyze my finances?"
                                answer="Our AI uses machine learning models trained on financial data to analyze 45+ parameters including income, expenses, savings patterns, and investment behavior to provide personalized insights."
                            />
                            <FAQItem
                                question="Is my financial data secure?"
                                answer="Absolutely. We use bank-level encryption and never store your actual account credentials. Your data is encrypted at rest and in transit."
                            />
                            <FAQItem
                                question="Can I use FinBro for free?"
                                answer="Yes! Our core features including the dashboard, expense tracking, and basic AI insights are completely free. Premium features are available for power users."
                            />
                            <FAQItem
                                question="How accurate are the AI predictions?"
                                answer="Our savings prediction model has a 92.5% accuracy rate, and our risk assessment models are continuously improving with new data."
                            />
                        </div>
                    </div>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════════
          FINAL CTA SECTION - Black Background
          ═══════════════════════════════════════════════════════════════════ */}
            <section className="py-32 px-6 bg-black relative overflow-hidden">
                <div className="absolute top-10 left-10 text-6xl opacity-30">💰</div>
                <div className="absolute bottom-10 right-10 text-6xl opacity-30">✨</div>
                <div className="absolute top-1/2 right-1/4 text-4xl opacity-20">📈</div>

                <div className="container mx-auto text-center relative z-10">
                    <h2 className="text-5xl sm:text-6xl lg:text-7xl font-black text-white leading-[0.95] uppercase mb-8">
                        Came for the<br />
                        content, stayed<br />
                        for the <span style={{ color: colors.purple }}>glow up!</span> ✨
                    </h2>
                    <p className="text-xl text-gray-400 mb-12 max-w-xl mx-auto">
                        Start your financial transformation today. It's free to get started.
                    </p>
                    <Link to="/dashboard">
                        <Button
                            size="lg"
                            className="bg-[#8B5CF6] text-white font-bold px-12 py-8 text-xl rounded-full hover:bg-white hover:text-black transition-all border-2 border-[#8B5CF6]"
                            style={{ boxShadow: '8px 8px 0 0 #FEF08A' }}
                        >
                            Get Started Free →
                        </Button>
                    </Link>
                </div>
            </section>

            {/* ═══════════════════════════════════════════════════════════════════
          FOOTER
          ═══════════════════════════════════════════════════════════════════ */}
            <footer className="py-12 px-6 bg-white border-t-2 border-black">
                <div className="container mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
                    <div className="flex items-center gap-2">
                        <div
                            className="w-10 h-10 rounded-xl flex items-center justify-center font-black text-white text-xl"
                            style={{ backgroundColor: colors.purple }}
                        >
                            F
                        </div>
                        <span className="text-2xl font-black text-black">FinBro.ai</span>
                    </div>

                    <p className="text-gray-500">
                        © 2026 FinBro.ai — Your AI-Powered Finance Companion
                    </p>
                </div>
            </footer>
        </div>
    );
};

export default Landing;
