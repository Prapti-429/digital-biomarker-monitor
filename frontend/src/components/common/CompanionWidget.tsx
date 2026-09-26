import React, { useEffect, useRef, useState } from 'react';
import { apiClient } from '../../services/api';
import { useLanguage, AppLanguage } from '../../contexts/LanguageContext';
import { useAuth } from '../../contexts/AuthContext';

type Message = { role: 'user' | 'assistant'; text: string };

type Lang = 'en' | 'hi' | 'fr';

const langCode = (language: AppLanguage): Lang => language === 'Hindi' ? 'hi' : language === 'French' ? 'fr' : 'en';

const COPY: Record<Lang, {
  greeting: string; title: string; subtitle: string; placeholder: string; send: string; listen: string; stop: string;
  categories: { label: string; prompt: string }[]; read: string; stopReading: string; close: string; typing: string;
  fallback: string; accountPrompt: string;
}> = {
  en: {
    greeting: 'Hey, I am your personalized NUVYRA AI Companion. How may I help you?', title: 'NUVYRA Companion',
    subtitle: 'Ask naturally. I can explain NUVYRA, your account, healthcare concepts, and what your measurements mean.',
    placeholder: 'Ask anything…', send: 'Send', listen: 'Speak', stop: 'Stop', read: 'Read aloud', stopReading: 'Stop reading', close: 'Close', typing: 'Thinking…',
    categories: [
      { label: 'My account', prompt: 'Help me understand my NUVYRA account and what I can do here.' },
      { label: 'My health data', prompt: 'Help me understand my NUVYRA measurements, baseline and trends.' },
      { label: 'Healthcare', prompt: 'I have a healthcare question. Help me understand it in simple language.' },
      { label: 'Health terms', prompt: 'Explain a healthcare term, test, report or medical abbreviation in simple language.' },
      { label: 'How NUVYRA works', prompt: 'Explain how NUVYRA and its digital-biomarker features work.' },
    ],
    fallback: 'I could not reach the companion right now. Please try again in a moment.',
    accountPrompt: 'My account',
  },
  hi: {
    greeting: 'नमस्ते, मैं आपका व्यक्तिगत NUVYRA AI Companion हूँ। मैं आपकी कैसे मदद कर सकता हूँ?', title: 'NUVYRA साथी',
    subtitle: 'स्वाभाविक तरीके से पूछें। मैं NUVYRA, आपके अकाउंट, स्वास्थ्य विषयों और measurements को समझाने में मदद कर सकता हूँ।',
    placeholder: 'कुछ भी पूछें…', send: 'भेजें', listen: 'बोलें', stop: 'रोकें', read: 'आवाज़ में सुनें', stopReading: 'पढ़ना रोकें', close: 'बंद करें', typing: 'सोच रहा हूँ…',
    categories: [
      { label: 'मेरा अकाउंट', prompt: 'मेरे NUVYRA अकाउंट और मैं यहाँ क्या कर सकता हूँ, समझाइए।' },
      { label: 'मेरा स्वास्थ्य डेटा', prompt: 'मेरे NUVYRA measurements, baseline और trends को समझने में मदद करें।' },
      { label: 'स्वास्थ्य', prompt: 'मेरा एक healthcare सवाल है। इसे आसान भाषा में समझाइए।' },
      { label: 'Health terms', prompt: 'किसी healthcare term, test, report या medical abbreviation को आसान भाषा में समझाइए।' },
      { label: 'NUVYRA कैसे काम करता है', prompt: 'समझाइए कि NUVYRA और उसके digital-biomarker features कैसे काम करते हैं।' },
    ],
    fallback: 'अभी companion से संपर्क नहीं हो पाया। कृपया थोड़ी देर बाद फिर कोशिश करें।', accountPrompt: 'मेरा अकाउंट',
  },
  fr: {
    greeting: 'Bonjour, je suis votre compagnon IA personnalisé NUVYRA. Comment puis-je vous aider ?', title: 'Compagnon NUVYRA',
    subtitle: 'Posez vos questions naturellement. Je peux expliquer NUVYRA, votre compte, les sujets de santé et vos mesures.',
    placeholder: 'Posez une question…', send: 'Envoyer', listen: 'Parler', stop: 'Arrêter', read: 'Lire à voix haute', stopReading: 'Arrêter la lecture', close: 'Fermer', typing: 'Réflexion…',
    categories: [
      { label: 'Mon compte', prompt: 'Aidez-moi à comprendre mon compte NUVYRA et ce que je peux faire ici.' },
      { label: 'Mes données de santé', prompt: 'Aidez-moi à comprendre mes mesures NUVYRA, ma référence personnelle et mes tendances.' },
      { label: 'Santé', prompt: 'J’ai une question de santé. Expliquez-la-moi avec des mots simples.' },
      { label: 'Termes de santé', prompt: 'Expliquez un terme de santé, un examen, un rapport ou une abréviation médicale simplement.' },
      { label: 'Comment fonctionne NUVYRA', prompt: 'Expliquez comment fonctionnent NUVYRA et ses fonctionnalités de biomarqueurs numériques.' },
    ],
    fallback: 'Je ne peux pas joindre le compagnon pour le moment. Veuillez réessayer.', accountPrompt: 'Mon compte',
  },
};

export const CompanionWidget: React.FC = () => {
  const { language } = useLanguage();
  const { user } = useAuth();
  const current = langCode(language);
  const t = COPY[current];
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [busy, setBusy] = useState(false);
  const [listening, setListening] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const recognitionRef = useRef<any>(null);
  const greetingSpoken = useRef(false);

  const speak = (text: string) => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = current === 'hi' ? 'hi-IN' : current === 'fr' ? 'fr-FR' : 'en-US';
    utterance.onstart = () => setSpeaking(true);
    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);
    window.speechSynthesis.speak(utterance);
  };

  useEffect(() => () => { recognitionRef.current?.stop(); window.speechSynthesis?.cancel(); }, []);

  const openCompanion = () => {
    setOpen(true);
    if (!greetingSpoken.current) {
      greetingSpoken.current = true;
      window.setTimeout(() => speak(t.greeting), 100);
    }
  };

  const startVoice = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    if (listening) { recognitionRef.current?.stop(); setListening(false); return; }
    const recognition = new SpeechRecognition();
    recognition.lang = current === 'hi' ? 'hi-IN' : current === 'fr' ? 'fr-FR' : 'en-US';
    recognition.interimResults = false;
    recognition.continuous = false;
    recognition.onresult = (event: any) => setInput(event.results[0][0].transcript);
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
    recognitionRef.current = recognition;
    setListening(true);
    recognition.start();
  };

  const send = async (preset?: string) => {
    const message = (preset ?? input).trim();
    if (!message || busy) return;
    setMessages((items) => [...items, { role: 'user', text: message }]);
    setInput(''); setBusy(true);
    try {
      const { data } = await apiClient.post('/companion/chat', { message, language: current });
      const answer = typeof data?.answer === 'string' && data.answer.trim() ? data.answer : t.fallback;
      const disclaimer = typeof data?.disclaimer === 'string' ? data.disclaimer : '';
      const text = disclaimer ? `${answer}\n\n${disclaimer}` : answer;
      setMessages((items) => [...items, { role: 'assistant', text }]);
    } catch {
      setMessages((items) => [...items, { role: 'assistant', text: t.fallback }]);
    } finally { setBusy(false); }
  };

  const accountName = user?.full_name || 'your account';

  return <>
    {!open && <button type="button" onClick={openCompanion} aria-label="Open NUVYRA AI Companion" title="NUVYRA AI Companion" className="fixed bottom-6 right-6 z-50 flex h-16 w-16 items-center justify-center rounded-full border border-sky-400/40 bg-sky-600 text-2xl text-white shadow-2xl shadow-sky-950/50 transition hover:scale-105 hover:bg-sky-500 focus:outline-none focus:ring-4 focus:ring-sky-400/30">✦</button>}
    {open && <div className="fixed bottom-5 right-5 z-[90] w-[calc(100vw-2rem)] max-w-[430px] overflow-hidden rounded-3xl border border-slate-700 bg-[#0E1524] shadow-2xl shadow-black/50" role="dialog" aria-modal="false" aria-label="NUVYRA AI Companion">
      <div className="flex items-center justify-between border-b border-slate-800 bg-gradient-to-r from-sky-950/80 to-[#0E1524] px-5 py-4">
        <div><div className="flex items-center gap-2"><span className="flex h-9 w-9 items-center justify-center rounded-xl bg-sky-500/15 text-lg text-sky-300">✦</span><div><h2 className="text-sm font-bold text-white">{t.title}</h2><p className="text-[11px] text-slate-400">Personalized for {accountName}</p></div></div></div>
        <button type="button" onClick={() => { setOpen(false); window.speechSynthesis?.cancel(); }} className="rounded-lg px-2 py-1 text-slate-400 hover:bg-slate-800 hover:text-white" aria-label={t.close}>×</button>
      </div>
      <div className="max-h-[62vh] overflow-y-auto p-4">
        {messages.length === 0 ? <div className="space-y-4">
          <div className="rounded-2xl border border-sky-500/20 bg-sky-500/5 p-4 text-sm leading-6 text-slate-200">{t.greeting}</div>
          <p className="text-xs leading-5 text-slate-400">{t.subtitle}</p>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">{t.categories.map((item) => <button key={item.label} type="button" onClick={() => void send(item.prompt)} className="rounded-2xl border border-slate-800 bg-slate-900/60 px-3 py-3 text-left text-xs font-semibold text-slate-200 transition hover:border-sky-500/40 hover:bg-sky-500/5">{item.label}<span className="mt-1 block text-[10px] font-normal leading-4 text-slate-500">{item.prompt}</span></button>)}</div>
        </div> : <div className="space-y-3">{messages.map((m, i) => <div key={i} className={m.role === 'user' ? 'ml-8 rounded-2xl bg-sky-600 px-3 py-2.5 text-sm text-white' : 'mr-3 rounded-2xl bg-slate-800 px-3 py-3 text-sm leading-6 text-slate-200'}><div className="whitespace-pre-wrap">{m.text}</div>{m.role === 'assistant' && <button type="button" onClick={() => speaking ? window.speechSynthesis.cancel() : speak(m.text.split('\n\n')[0])} className="mt-2 text-[11px] font-semibold text-sky-300 hover:text-sky-200">{speaking ? `⏹ ${t.stopReading}` : `🔊 ${t.read}`}</button>}</div>)}{busy && <div className="mr-10 rounded-2xl bg-slate-800 px-3 py-2 text-xs text-slate-400">{t.typing}</div>}</div>}
      </div>
      <div className="border-t border-slate-800 p-3">
        <div className="flex gap-2"><textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void send(); } }} placeholder={t.placeholder} rows={2} className="min-h-11 flex-1 resize-none rounded-2xl border border-slate-700 bg-slate-900 px-3 py-2.5 text-sm text-white outline-none placeholder:text-slate-500 focus:border-sky-500" /><button type="button" onClick={startVoice} className="h-11 rounded-2xl border border-slate-700 px-3 text-sm text-slate-200 hover:bg-slate-800" aria-label={listening ? t.stop : t.listen}>{listening ? '⏹' : '🎙️'}</button><button type="button" disabled={busy || !input.trim()} onClick={() => void send()} className="h-11 rounded-2xl bg-sky-600 px-4 text-sm font-semibold text-white disabled:opacity-40">{t.send}</button></div>
        <p className="mt-2 text-[10px] leading-4 text-slate-500">Health information only — not a diagnosis or a replacement for professional medical care.</p>
      </div>
    </div>}
  </>;
};

export default CompanionWidget;
