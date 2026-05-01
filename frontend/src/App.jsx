import React, { useState, useEffect, useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { Shield, Globe, Briefcase, Smile, MessageCircle, X, Send, Maximize2, Minimize2, Mic, MicOff } from 'lucide-react';

// --- Config ---
const WHATSAPP_NUMBER = '14155238886'; // Twilio Sandbox Number (without +)
// IMPORTANT: Replace 'your-sandbox-word' with the actual word from your Twilio Console (e.g. 'join flag-shape')
const WHATSAPP_MESSAGE = 'join your-sandbox-word-here'; 
const WHATSAPP_URL = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(WHATSAPP_MESSAGE)}`;

// WhatsApp SVG Icon
const WhatsAppIcon = ({ size = 24, className = '' }) => (
  <svg viewBox="0 0 24 24" width={size} height={size} fill="currentColor" className={className}>
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" />
  </svg>
);

// --- Reusable Components ---

const FadeIn = ({ children, delay = 0, className = "" }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-10%" });
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 30 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 30 }}
      transition={{ duration: 0.8, delay, ease: "easeOut" }}
      className={className}
    >
      {children}
    </motion.div>
  );
};

const AnimatedCounter = ({ target }) => {
  const [count, setCount] = useState(0);
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  useEffect(() => {
    if (isInView) {
      let current = 0;
      const duration = 2000;
      const step = Math.max(1, Math.floor(target / 50));
      const timer = setInterval(() => {
        current += step;
        if (current >= target) {
          setCount(target);
          clearInterval(timer);
        } else {
          setCount(current);
        }
      }, duration / 50);
      return () => clearInterval(timer);
    }
  }, [isInView, target]);

  return <span ref={ref}>{count.toLocaleString()}</span>;
};

// --- Main App ---

export default function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [messages, setMessages] = useState([
    { role: 'bot', text: 'Hey bhai! 👋 I am AI Dost. How can I help you ace your hackathon today?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);
  const sessionId = useRef("session_" + Math.floor(Math.random() * 1000000));
  const messagesEndRef = useRef(null);

  // --- Speech Recognition Setup ---
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.lang = 'hi-IN'; // Hinglish/Hindi support
    recognition.interimResults = true;
    recognition.continuous = true;

    recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }
      if (finalTranscript) {
        setInput(prev => prev + finalTranscript);
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      recognition.abort();
    };
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setInput('');
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInput('');
    setIsLoading(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': 'hackathon_super_secret_key_123'
        },
        body: JSON.stringify({
          message: userMsg,
          session_id: sessionId.current
        })
      });
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'bot', text: data.reply }]);
    } catch (error) {
      console.error("Chat Error:", error);
      setMessages(prev => [...prev, { role: 'bot', text: 'Oops! Backend server se connect nahi ho paya. Please start uvicorn! ❌' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="bg-grid"></div>
      <div className="glow-blob"></div>

      {/* NAVBAR */}
      <nav className="fixed top-0 w-full z-50 glass-panel px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3 font-extrabold text-xl">
          <div className="w-8 h-8 bg-[#00e676] rounded-md flex items-center justify-center text-black">🤖</div>
          AI Dost
        </div>
        <div className="hidden md:flex gap-8 text-sm font-medium text-gray-300">
          <a href="#home" className="hover:text-[#00e676] transition-colors">Home</a>
          <a href="#how-it-works" className="hover:text-[#00e676] transition-colors">How it works</a>
          <a href="#features" className="hover:text-[#00e676] transition-colors">Features</a>
          <a href="#about-us" className="hover:text-[#00e676] transition-colors">About Us</a>
        </div>
        <div className="flex gap-4">
          <button onClick={() => setIsChatOpen(true)} className="px-5 py-2 rounded-full bg-[#00e676] hover:bg-[#2dff7a] text-black transition-transform hover:-translate-y-0.5 shadow-[0_0_20px_rgba(0,230,118,0.3)] text-sm font-semibold">
            Chat Now
          </button>
        </div>
      </nav>

      {/* HERO SECTION */}
      <section id="home" className="min-h-screen flex flex-col justify-center items-center text-center px-6 pt-32 pb-20 relative">
        {/* Particles */}
        <motion.div animate={{ y: [0, -30, 0], rotate: [0, 15, 0] }} transition={{ duration: 8, repeat: Infinity }} className="absolute top-[20%] left-[15%] text-2xl text-white/20 font-mono">{'</>'}</motion.div>
        <motion.div animate={{ y: [0, 30, 0], rotate: [0, -15, 0] }} transition={{ duration: 10, repeat: Infinity, delay: 1 }} className="absolute top-[30%] right-[20%] text-3xl text-white/20">🚀</motion.div>
        <motion.div animate={{ y: [0, -20, 0], rotate: [0, 10, 0] }} transition={{ duration: 7, repeat: Infinity, delay: 2 }} className="absolute bottom-[25%] left-[25%] text-2xl text-white/20 font-mono">{'{ }'}</motion.div>
        <motion.div animate={{ y: [0, 20, 0], rotate: [0, -10, 0] }} transition={{ duration: 9, repeat: Infinity, delay: 0.5 }} className="absolute bottom-[30%] right-[15%] text-2xl text-white/20">💡</motion.div>

        <FadeIn delay={0.1}>
          <div className="glass-panel inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm mb-8">
            Your Personal <span className="text-[#00e676]">✅ Student Mentor</span>
          </div>
        </FadeIn>

        <FadeIn delay={0.2}>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 leading-tight">
            Meet Your New Best Friend <br />
            <span className="text-gray-400">Hackathon & Career Guide</span>
          </h1>
        </FadeIn>

        <FadeIn delay={0.3} className="flex flex-wrap justify-center gap-4">
          <button onClick={() => setIsChatOpen(true)} className="px-8 py-4 rounded-full bg-[#00e676] hover:bg-[#2dff7a] text-black transition-transform hover:-translate-y-1 shadow-[0_0_30px_rgba(0,230,118,0.4)] font-semibold text-lg">
            Chat with AI Dost &rarr;
          </button>
          <a
            href={WHATSAPP_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="px-8 py-4 rounded-full bg-[#25D366] hover:bg-[#22c55e] text-white transition-transform hover:-translate-y-1 shadow-[0_0_30px_rgba(37,211,102,0.4)] font-semibold text-lg flex items-center gap-3"
          >
            <WhatsAppIcon size={22} />
            Chat on WhatsApp
          </a>
        </FadeIn>

        <FadeIn delay={0.5} className="flex flex-wrap justify-center gap-8 mt-20 text-gray-400 text-sm font-medium">
          <div className="flex items-center gap-2"><span className="text-[#00e676]">✦</span> Native Hinglish Support</div>
          <div className="flex items-center gap-2"><span className="text-[#00e676]">✦</span> Instant Scam Detection</div>
          <div className="flex items-center gap-2"><span className="text-[#00e676]">✦</span> 24/7 Mentorship</div>
        </FadeIn>
      </section>

      {/* STATS SECTION */}
      <section className="py-20 px-6 max-w-6xl mx-auto">
        <FadeIn>
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4"><span className="text-[#00e676]"><AnimatedCounter target={10000} /></span>+ Students Mentored!</h2>
            <p className="text-gray-400 text-lg">Join thousands of students crushing their interviews and hackathons.</p>
          </div>
        </FadeIn>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {[
            { num: "5+", label: "Regional Languages Auto-Detected" },
            { num: "100%", label: "Free & Open Source" },
            { num: "<1s", label: "Lightning Fast Replies" },
            { num: "24/7", label: "Mentorship Availability" }
          ].map((stat, i) => (
            <FadeIn delay={0.1 * i} key={i}>
              <div className="glass-panel p-10 rounded-3xl text-center hover:-translate-y-2 transition-all duration-300 hover:shadow-[0_10px_30px_rgba(0,230,118,0.1)] hover:border-[#00e676]/30">
                <div className="text-5xl font-extrabold text-[#00e676] mb-3">{stat.num}</div>
                <p className="text-gray-400 text-lg">{stat.label}</p>
              </div>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how-it-works" className="py-20 px-6 max-w-6xl mx-auto">
        <FadeIn>
          <div className="mb-16">
            <h2 className="text-4xl font-bold mb-4">How does it work?</h2>
            <p className="text-gray-400 text-lg">Your pathway to technical success in 3 simple steps.</p>
          </div>
        </FadeIn>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <FadeIn delay={0.2}>
            <h3 className="text-2xl text-[#00e676] font-bold mb-4">Step 1: Ask a Question</h3>
            <p className="text-gray-400 text-lg mb-12">Got a doubt about Data Structures, hackathon ideas, or resume building? Just drop a message.</p>

            <div className="flex justify-between border-t border-white/10 pt-6">
              <div className="text-[#00e676] font-bold">STEP 1</div>
              <div className="text-gray-600 font-bold">STEP 2</div>
              <div className="text-gray-600 font-bold">STEP 3</div>
            </div>
          </FadeIn>
          <FadeIn delay={0.4}>
            <div className="card-visual p-10">
              <div className="flex justify-between mb-8">
                <span className="font-bold text-[#d4af37]">MENTORSHIP TIER</span>
                <span className="text-gray-400">Unlimited Access</span>
              </div>
              <h2 className="text-5xl font-bold mb-2">100% Free</h2>
              <p className="text-gray-400 mb-8">No hidden fees. Just pure knowledge.</p>
              <button onClick={() => setIsChatOpen(true)} className="w-full py-4 rounded-xl bg-[#00e676] text-black font-bold text-lg hover:bg-[#2dff7a] transition-colors">
                Start Chatting
              </button>
            </div>
          </FadeIn>
        </div>
      </section>

      {/* FEATURES */}
      <section id="features" className="py-20 px-6 max-w-6xl mx-auto">
        <FadeIn>
          <h2 className="text-4xl font-bold mb-12">Why choose AI Dost?</h2>
        </FadeIn>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {[
            { icon: <Globe className="w-8 h-8 text-[#00e676]" />, title: "Multi-Lingual", desc: "Detects and responds in local regional languages naturally (Kannada, Telugu, Hindi, etc)." },
            { icon: <Shield className="w-8 h-8 text-[#00e676]" />, title: "Scam Detection", desc: "Built-in security layer alerts you about phishing links and OTP scams instantly." },
            { icon: <Briefcase className="w-8 h-8 text-[#00e676]" />, title: "Career Focus", desc: "Tailored resume tips, interview prep, and hackathon guidance." },
            { icon: <Smile className="w-8 h-8 text-[#00e676]" />, title: "Buddy Persona", desc: "Doesn't talk like a boring corporate bot—talks like a real friend (Bhai/Dost)." }
          ].map((feat, i) => (
            <FadeIn delay={i * 0.1} key={i}>
              <div className="glass-panel p-8 rounded-3xl h-full">
                <div className="mb-6">{feat.icon}</div>
                <h3 className="text-2xl font-bold mb-4">{feat.title}</h3>
                <p className="text-gray-400">{feat.desc}</p>
              </div>
            </FadeIn>
          ))}
        </div>
      </section>

      {/* ABOUT US */}
      <section id="about-us" className="py-20 px-6 max-w-6xl mx-auto text-center">
        <FadeIn>
          <h2 className="text-4xl font-bold mb-8">About Us</h2>
          <div className="glass-panel p-10 rounded-3xl inline-block max-w-2xl border border-[#00e676]/30 shadow-[0_0_30px_rgba(0,230,118,0.1)]">
            <p className="text-gray-300 text-lg mb-6">
              AI Dost is your ultimate companion for hackathons, career prep, and technical interviews. We believe in making high-quality mentorship accessible to everyone, in every language.
            </p>
            <a
              href="https://arthgrowthofficial.netlify.app/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block mt-2 text-[#00e676] font-bold text-xl tracking-wide hover:text-[#2dff7a] hover:underline transition-all"
            >
              Exclusively built by Arthgrowth Studio ↗
            </a>
          </div>
        </FadeIn>
      </section>

      {/* FOOTER */}
      <footer className="py-20 text-center border-t border-white/5 mt-20">
        <div className="w-16 h-16 bg-[#00e676] rounded-2xl mx-auto mb-8 flex items-center justify-center text-black font-bold text-2xl">🤖</div>
        <h2 className="text-3xl font-bold mb-4">Ready to level up your career?</h2>
        <p className="text-gray-400 mb-8">AI Dost is waiting to help you succeed.</p>
        <button onClick={() => setIsChatOpen(true)} className="px-8 py-4 rounded-full bg-[#00e676] text-black font-bold hover:bg-[#2dff7a] transition-colors">
          Start Chatting Now
        </button>
      </footer>

      {/* CHAT WIDGET */}
      <div className="fixed bottom-8 right-8 z-[999] flex flex-col items-end">
        {isChatOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            className={`glass-panel mb-4 rounded-2xl flex flex-col overflow-hidden shadow-2xl transition-all duration-300 origin-bottom-right ${isMaximized ? 'fixed inset-4 w-auto h-auto z-[1000]' : 'w-[350px] h-[500px]'}`}
          >
            {/* Header */}
            <div className="bg-[#1a1a1a] p-4 flex justify-between items-center border-b border-white/10">
              <div className="font-bold flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[#00e676]"></div>
                AI Dost Mentor
              </div>
              <div className="flex gap-4 items-center">
                <button onClick={() => setIsMaximized(!isMaximized)} className="text-gray-400 hover:text-white transition-colors">
                  {isMaximized ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
                </button>
                <button onClick={() => setIsChatOpen(false)} className="text-gray-400 hover:text-white transition-colors">
                  <X size={20} />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 p-4 overflow-y-auto flex flex-col gap-4 bg-[#0a0a0a]">
              {messages.map((msg, i) => (
                <div key={i} className={`max-w-[80%] p-3 rounded-2xl text-sm ${msg.role === 'user' ? 'bg-[#00e676] text-black self-end rounded-br-sm' : 'bg-[#222] text-white self-start rounded-bl-sm'}`}>
                  {msg.text}
                </div>
              ))}
              {isLoading && (
                <div className="bg-[#222] text-white self-start rounded-bl-sm p-3 rounded-2xl text-sm max-w-[80%] flex gap-1">
                  <span className="animate-bounce">.</span><span className="animate-bounce delay-100">.</span><span className="animate-bounce delay-200">.</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-3 bg-[#1a1a1a] border-t border-white/10 flex gap-2 items-center">
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && sendMessage()}
                placeholder={isListening ? '🎙️ Listening...' : 'Ask your query...'}
                className="flex-1 bg-transparent border-none outline-none text-sm text-white placeholder-gray-500"
              />
              <button
                onClick={toggleListening}
                className={`relative p-1.5 rounded-full transition-all duration-300 ${isListening
                    ? 'text-black bg-[#00e676] shadow-[0_0_15px_rgba(0,230,118,0.6)]'
                    : 'text-gray-400 hover:text-[#00e676]'
                  }`}
                title={isListening ? 'Stop listening' : 'Start voice input'}
              >
                {isListening && (
                  <span className="absolute inset-0 rounded-full bg-[#00e676] animate-ping opacity-40"></span>
                )}
                {isListening ? <MicOff size={18} className="relative z-10" /> : <Mic size={18} />}
              </button>
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="text-[#00e676] disabled:opacity-50 hover:text-[#2dff7a] transition-colors"
              >
                <Send size={20} />
              </button>
            </div>
          </motion.div>
        )}

        <button
          onClick={() => setIsChatOpen(!isChatOpen)}
          className="w-14 h-14 bg-[#00e676] rounded-full flex items-center justify-center text-black shadow-[0_5px_20px_rgba(0,230,118,0.4)] hover:scale-110 transition-transform"
        >
          {isChatOpen ? <X size={24} /> : <MessageCircle size={24} />}
        </button>
      </div>

      {/* FLOATING WHATSAPP BUTTON */}
      <a
        href={WHATSAPP_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="fixed bottom-8 left-8 z-[999] w-14 h-14 bg-[#25D366] rounded-full flex items-center justify-center text-white shadow-[0_5px_20px_rgba(37,211,102,0.5)] hover:scale-110 transition-transform hover:shadow-[0_5px_30px_rgba(37,211,102,0.7)] group"
        title="Chat on WhatsApp"
      >
        <WhatsAppIcon size={26} />
        <span className="absolute left-16 bg-[#1a1a1a] text-white text-sm px-3 py-1.5 rounded-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none shadow-lg border border-white/10">
          Chat on WhatsApp
        </span>
      </a>
    </>
  );
}
