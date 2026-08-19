import React, { useEffect, useRef, useState } from 'react';
import { apiClient } from '../services/api';

type Lang = 'en' | 'hi' | 'fr';

const copy = {
  en: { title: 'NUVYRA Companion', sub: 'Ask me about NUVYRA, your measurements, trends, or general health questions.', placeholder: 'Type your question…', send: 'Send', listen: 'Speak', stop: 'Stop', intro: 'Hi! I can explain how NUVYRA works and help you understand what you see. I cannot diagnose illness or prescribe treatment.' },
  hi: { title: 'NUVYRA Companion', sub: 'NUVYRA, आपके measurements, trends या सामान्य health questions के बारे में पूछें।', placeholder: 'अपना सवाल लिखें…', send: 'भेजें', listen: 'बोलें', stop: 'रोकें', intro: 'नमस्ते! मैं NUVYRA को समझने और आपके results को समझाने में मदद कर सकता हूँ। मैं diagnosis या treatment की सलाह नहीं देता।' },
  fr: { title: 'Compagnon NUVYRA', sub: 'Posez vos questions sur NUVYRA, vos mesures, les tendances ou la santé en général.', placeholder: 'Écrivez votre question…', send: 'Envoyer', listen: 'Parler', stop: 'Arrêter', intro: 'Bonjour ! Je peux expliquer NUVYRA et vos résultats. Je ne peux pas établir de diagnostic ni prescrire un traitement.' },
};

export const CompanionPage: React.FC = () => {
  const [language, setLanguage] = useState<Lang>((localStorage.getItem('nuvyra_language') as Lang) || 'en');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; text: string }>>([]);
  const [busy, setBusy] = useState(false);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef<any>(null);
  const t = copy[language];

  useEffect(() => () => recognitionRef.current?.stop(), []);

  const speak = (text: string) => {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = language === 'hi' ? 'hi-IN' : language === 'fr' ? 'fr-FR' : 'en-US';
    window.speechSynthesis.speak(utterance);
  };

  const startVoice = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) return;
    if (listening) { recognitionRef.current?.stop(); setListening(false); return; }
    const recognition = new SpeechRecognition();
    recognition.lang = language === 'hi' ? 'hi-IN' : language === 'fr' ? 'fr-FR' : 'en-US';
    recognition.interimResults = false;
    recognition.continuous = false;
    recognition.onresult = (event: any) => setInput(event.results[0][0].transcript);
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);
    recognitionRef.current = recognition;
    setListening(true);
    recognition.start();
  };

  const send = async () => {
    const message = input.trim();
    if (!message || busy) return;
    setMessages((m) => [...m, { role: 'user', text: message }]);
    setInput(''); setBusy(true);
    try {
      const { data } = await apiClient.post('/companion/chat', { message, language });
      setMessages((m) => [...m, { role: 'assistant', text: `${data.answer}\n\n${data.disclaimer}` }]);
      speak(data.answer);
    } catch {
      setMessages((m) => [...m, { role: 'assistant', text: 'I could not reach the companion right now. Please try again in a moment.' }]);
    } finally { setBusy(false); }
  };

  return <div className="mx-auto max-w-4xl space-y-6 p-4 md:p-8">
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div><div className="mb-2 inline-flex rounded-full bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700">AI companion</div><h1 className="text-3xl font-bold text-slate-900">{t.title}</h1><p className="mt-2 max-w-2xl text-slate-600">{t.sub}</p></div>
        <select aria-label="Language" value={language} onChange={(e) => setLanguage(e.target.value as Lang)} className="rounded-xl border border-slate-200 px-3 py-2 text-sm"><option value="en">English</option><option value="hi">हिन्दी</option><option value="fr">Français</option></select>
      </div>
      <div className="mt-5 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">{t.intro}</div>
    </div>
    <div className="min-h-[320px] space-y-3 rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
      {messages.length === 0 && <div className="flex h-64 items-center justify-center text-center text-slate-400">Ask anything about the software or what your dashboard means.</div>}
      {messages.map((m, i) => <div key={i} className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-3 text-sm ${m.role === 'user' ? 'ml-auto bg-sky-600 text-white' : 'bg-slate-100 text-slate-800'}`}>{m.text}{m.role === 'assistant' && <button onClick={() => speak(m.text.split('\n\n')[0])} className="ml-2 text-xs font-semibold underline">🔊</button>}</div>)}
    </div>
    <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex gap-2"><textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void send(); } }} placeholder={t.placeholder} rows={2} className="min-h-12 flex-1 resize-none rounded-2xl border border-slate-200 p-3 outline-none focus:border-sky-400" /><button onClick={startVoice} className="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-semibold">{listening ? `⏹ ${t.stop}` : `🎙️ ${t.listen}`}</button><button disabled={busy || !input.trim()} onClick={() => void send()} className="rounded-2xl bg-sky-600 px-5 py-2 text-sm font-semibold text-white disabled:opacity-50">{t.send}</button></div>
      <p className="mt-3 text-xs text-slate-500">For emergencies or medical decisions, use a qualified healthcare professional rather than this research companion.</p>
    </div>
  </div>;
};

export default CompanionPage;
