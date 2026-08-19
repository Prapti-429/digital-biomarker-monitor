import React, { useEffect, useState } from 'react';
import { apiClient } from '../services/api';
export const NotificationsPage: React.FC = () => {
 const [items,setItems]=useState<any[]>([]); const [error,setError]=useState('');
 const load=async()=>{try{const r=await apiClient.get('/past-history');setItems(r.data?.reminders||[]);}catch(e:any){setError(e?.message||'Unable to load notifications.');}};
 useEffect(()=>{void load();},[]);
 const done=async(id:string)=>{try{await apiClient.post(`/past-history/reminders/${id}/complete`);await load();}catch(e:any){setError(e?.message||'Unable to update notification.');}};
 return <main className="space-y-6"><header><h1 className="text-3xl font-bold text-white">Notifications</h1><p className="mt-2 text-slate-400">Reminders created from your saved health information and uploaded documents.</p></header>{error&&<div className="rounded-xl border border-rose-800 bg-rose-950/20 p-3 text-sm text-rose-200">{error}</div>}{items.length?items.map(x=><article key={x.id} className="rounded-2xl border border-slate-700 bg-slate-900/60 p-5"><div className="flex items-start justify-between gap-4"><div><h2 className="font-semibold text-white">{x.title}</h2><p className="mt-2 text-sm leading-6 text-slate-300">{x.message}</p>{x.due_date&&<p className="mt-2 text-xs text-slate-500">Reminder date: {x.due_date}</p>}</div><button onClick={()=>void done(x.id)} className="rounded-lg border border-slate-600 px-3 py-2 text-sm text-slate-200">Done</button></div></article>):<div className="rounded-2xl border border-slate-700 bg-slate-900/60 p-8 text-center text-slate-400">You have no pending health reminders.</div>}<p className="text-xs text-slate-500">These reminders are organizational aids. They do not decide whether a medical test is necessary; always follow your clinician's instructions.</p></main>;
};
export default NotificationsPage;
