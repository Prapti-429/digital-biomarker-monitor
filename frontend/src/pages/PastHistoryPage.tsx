import React, { useEffect, useState } from 'react';
import { apiClient } from '../services/api';

const info = 'This section helps you keep previous illnesses, prescriptions and reports together. The software can extract text from supported documents and create organization reminders, but it does not diagnose conditions or decide which tests you medically need.';

type HistoryData = { history: Array<any>; documents: Array<any>; reminders: Array<any> };

export const PastHistoryPage: React.FC = () => {
  const [data, setData] = useState<HistoryData>({ history: [], documents: [], reminders: [] });
  const [illness, setIllness] = useState('');
  const [details, setDetails] = useState('');
  const [status, setStatus] = useState('');
  const [documentType, setDocumentType] = useState('prescription');
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  const load = async () => { try { const r = await apiClient.get('/past-history'); setData(r.data); } catch (e: any) { setMessage(e?.message || 'Unable to load past history.'); } };
  useEffect(() => { void load(); }, []);

  const saveHistory = async (e: React.FormEvent) => {
    e.preventDefault(); if (!illness.trim()) return;
    setBusy(true); setMessage('');
    try { const form = new FormData(); form.append('illness_name', illness); form.append('details', details); form.append('current_status', status); await apiClient.post('/past-history/illness', form); setIllness(''); setDetails(''); setStatus(''); setMessage('Past history saved.'); await load(); }
    catch (err: any) { setMessage(err?.message || 'Could not save history.'); } finally { setBusy(false); }
  };

  const upload = async (e: React.FormEvent) => {
    e.preventDefault(); if (!file) return;
    setBusy(true); setMessage('');
    try { const form = new FormData(); form.append('document_type', documentType); form.append('file', file); const r = await apiClient.post('/past-history/documents', form); const tests = r.data?.analysis?.detected_tests || []; setMessage(tests.length ? `Document analyzed. Reminder(s) created for: ${tests.join(', ')}.` : 'Document uploaded and analyzed.'); setFile(null); await load(); }
    catch (err: any) { setMessage(err?.message || 'Could not upload document.'); } finally { setBusy(false); }
  };

  const complete = async (id: string) => { try { await apiClient.post(`/past-history/reminders/${id}/complete`); await load(); } catch (e: any) { setMessage(e?.message || 'Could not update reminder.'); } };

  return <main className="mx-auto max-w-5xl space-y-6 p-6 text-white">
    <header><div className="flex items-center gap-2"><h1 className="text-3xl font-bold">Past History</h1><button title={info} aria-label="Past history information" className="rounded-full border px-2 text-xs">i</button></div><p className="mt-2 text-slate-400">Tell NUVYRA about previous illnesses and keep your latest prescription and reports organized.</p></header>
    {message && <div className="rounded-xl border border-slate-700 bg-slate-900 p-3 text-sm">{message}</div>}
    <section className="rounded-2xl border border-slate-700 bg-slate-900/60 p-5"><h2 className="mb-4 text-xl font-semibold">Previous illness or health history</h2><form onSubmit={saveHistory} className="grid gap-3 md:grid-cols-2"><input value={illness} onChange={e => setIllness(e.target.value)} placeholder="Example: Asthma" className="rounded-xl bg-slate-950 p-3" required /><input value={status} onChange={e => setStatus(e.target.value)} placeholder="Current status (optional)" className="rounded-xl bg-slate-950 p-3" /><textarea value={details} onChange={e => setDetails(e.target.value)} placeholder="Anything you want the software to remember (optional)" className="rounded-xl bg-slate-950 p-3 md:col-span-2" rows={3} /><button disabled={busy} className="rounded-xl bg-white px-4 py-3 font-semibold text-slate-900 disabled:opacity-50">Save history</button></form></section>
    <section className="rounded-2xl border border-slate-700 bg-slate-900/60 p-5"><h2 className="mb-2 text-xl font-semibold">Upload prescription or report</h2><p className="mb-4 text-sm text-slate-400">PDF and text documents can be read automatically. Scanned/image-only documents may require review if no readable text is available.</p><form onSubmit={upload} className="space-y-3"><select value={documentType} onChange={e => setDocumentType(e.target.value)} className="rounded-xl bg-slate-950 p-3"><option value="prescription">Latest prescription</option><option value="report">Latest report</option><option value="lab_report">Lab report</option><option value="test_report">Test report</option></select><input type="file" accept=".pdf,.txt,.csv,image/*" onChange={e => setFile(e.target.files?.[0] || null)} className="block w-full rounded-xl border border-slate-700 p-3" /><button disabled={busy || !file} className="rounded-xl bg-white px-4 py-3 font-semibold text-slate-900 disabled:opacity-50">Upload & analyze</button></form></section>
    <section className="rounded-2xl border border-slate-700 bg-slate-900/60 p-5"><h2 className="mb-4 text-xl font-semibold">Saved history</h2>{data.history.length ? data.history.map(x => <div key={x.id} className="mb-2 rounded-xl border border-slate-700 p-3"><strong>{x.illness_name}</strong>{x.current_status && <span className="ml-2 text-sm text-slate-400">{x.current_status}</span>}<p className="text-sm text-slate-400">{x.details}</p></div>) : <p className="text-slate-500">No previous history added yet.</p>}</section>
    <section className="rounded-2xl border border-slate-700 bg-slate-900/60 p-5"><h2 className="mb-4 text-xl font-semibold">Notifications & test reminders</h2>{data.reminders.length ? data.reminders.map(x => <div key={x.id} className="mb-2 flex items-start justify-between gap-3 rounded-xl border border-amber-800/60 bg-amber-950/20 p-3"><div><strong>{x.title}</strong><p className="text-sm text-slate-300">{x.message}</p>{x.due_date && <p className="text-xs text-slate-500">Reminder date: {x.due_date}</p>}</div><button onClick={() => void complete(x.id)} className="rounded-lg border px-3 py-2 text-sm">Done</button></div>) : <p className="text-slate-500">No pending reminders.</p>}</section>
    <section className="rounded-2xl border border-slate-700 p-5 text-sm text-slate-400"><strong className="text-white">About document analysis:</strong> NUVYRA extracts readable information to organize your record and identify possible test mentions. It does not determine whether a test is necessary, interpret results as a diagnosis, or replace your clinician.</section>
  </main>;
};

export default PastHistoryPage;
