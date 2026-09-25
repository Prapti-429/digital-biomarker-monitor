import React, { useEffect, useMemo, useState } from 'react';
import { aiService, AIHistoryPoint } from '../services/aiService';
import { useLanguage, AppLanguage } from '../contexts/LanguageContext';

type ReportDefinition = { key:string; title:string; description:string; fileName:string; observations:number };
const REPORTS: ReportDefinition[] = [
  { key:'weekly', title:'Weekly Longitudinal Summary', description:'A structured summary of your most recent 7 saved observations.', fileName:'nuvyra-weekly-longitudinal-report.csv', observations:7 },
  { key:'monthly', title:'Monthly Multimodal Synthesis', description:'A structured summary of your most recent 30 saved observations.', fileName:'nuvyra-monthly-multimodal-report.csv', observations:30 },
  { key:'baseline', title:'Baseline Calibration Benchmark', description:'Up to 90 saved observations for baseline and trajectory review.', fileName:'nuvyra-baseline-trajectory-report.csv', observations:90 },
];

const COPY: Record<AppLanguage, Record<string,string>> = {
  English:{title:'Longitudinal Reports',subtitle:'Export structured summaries of your baseline trajectory for research and observational review.',download:'Download report',preparing:'Preparing…',loading:'Loading saved observations…',available:'saved observations available',empty:'No saved observations are available for this report yet.',notice:'Downloads contain your saved NUVYRA longitudinal observations. They are research/observational summaries, not diagnostic medical reports.',what:'What is a longitudinal report?',whatText:'It is a portable snapshot of your repeated NUVYRA observations. It helps you review how your personal baseline and recorded pattern have changed over time.',csv:'CSV export',error:'The report could not be downloaded.'},
  Hindi:{title:'लॉन्गिट्यूडिनल रिपोर्ट',subtitle:'रिसर्च और अवलोकन समीक्षा के लिए अपनी व्यक्तिगत बेसलाइन की समय के साथ यात्रा का संरचित सारांश एक्सपोर्ट करें।',download:'रिपोर्ट डाउनलोड करें',preparing:'तैयार हो रही है…',loading:'सेव किए गए अवलोकन लोड हो रहे हैं…',available:'सेव किए गए अवलोकन उपलब्ध',empty:'इस रिपोर्ट के लिए अभी कोई सेव किया गया अवलोकन उपलब्ध नहीं है।',notice:'डाउनलोड में आपके सेव किए गए NUVYRA लॉन्गिट्यूडिनल अवलोकन होते हैं। ये रिसर्च/अवलोकन सारांश हैं, चिकित्सीय निदान रिपोर्ट नहीं।',what:'लॉन्गिट्यूडिनल रिपोर्ट क्या है?',whatText:'यह आपके बार-बार किए गए NUVYRA अवलोकनों का पोर्टेबल स्नैपशॉट है। इससे आप देख सकते हैं कि आपकी व्यक्तिगत बेसलाइन और रिकॉर्ड किए गए पैटर्न समय के साथ कैसे बदले।',csv:'CSV एक्सपोर्ट',error:'रिपोर्ट डाउनलोड नहीं हो सकी।'},
  French:{title:'Rapports longitudinaux',subtitle:'Exportez des résumés structurés de votre trajectoire de référence pour la recherche et l’observation.',download:'Télécharger le rapport',preparing:'Préparation…',loading:'Chargement des observations enregistrées…',available:'observations enregistrées disponibles',empty:'Aucune observation enregistrée n’est encore disponible pour ce rapport.',notice:'Les téléchargements contiennent vos observations longitudinales NUVYRA enregistrées. Ce sont des résumés de recherche/observation, pas des rapports médicaux diagnostiques.',what:'Qu’est-ce qu’un rapport longitudinal ?',whatText:'C’est un instantané portable de vos observations NUVYRA répétées. Il permet de revoir l’évolution de votre référence personnelle et de vos tendances enregistrées.',csv:'Export CSV',error:'Le rapport n’a pas pu être téléchargé.'}
};

const csvCell=(value:unknown)=>{const text=value==null?'':String(value);return '"'+text.replace(/"/g,'""')+'"';};
const buildCsv=(title:string,points:AIHistoryPoint[],language:AppLanguage)=>{
  const notice=language==='Hindi'?'केवल रिसर्च/अवलोकन सारांश; निदान या चिकित्सीय रिपोर्ट नहीं।':language==='French'?'Résumé de recherche/observation uniquement ; pas un diagnostic ni un rapport médical.':'Research/observational summary only; not a diagnosis or medical report.';
  const rows=[['NUVYRA Longitudinal Report',title],['Generated',new Date().toISOString()],['Notice',notice],[],['Check-in ID','Generated at','Pattern score','Confidence','Trend'],...points.map(p=>[p.check_in_id,p.generated_at,Number(p.score).toFixed(2),Number(p.confidence||0).toFixed(4),p.trend])];
  return rows.map(row=>row.map(csvCell).join(',')).join('\r\n');
};

const triggerDownload=(csv:string,fileName:string)=>{
  const blob=new Blob(['\uFEFF',csv],{type:'text/csv;charset=utf-8'});
  const url=URL.createObjectURL(blob);
  const anchor=document.createElement('a');
  anchor.href=url; anchor.download=fileName; anchor.rel='noopener'; anchor.style.position='fixed'; anchor.style.left='-9999px';
  document.body.appendChild(anchor); anchor.click();
  window.setTimeout(()=>{anchor.remove();URL.revokeObjectURL(url);},1500);
};

export const ReportsPage:React.FC=()=>{
  const {language}=useLanguage(); const t=COPY[language];
  const [history,setHistory]=useState<AIHistoryPoint[]>([]),[loading,setLoading]=useState(true),[error,setError]=useState<string|null>(null),[downloading,setDownloading]=useState<string|null>(null);
  useEffect(()=>{let active=true;aiService.history(90).then(r=>{if(active)setHistory(r?.items||[])}).catch((e:any)=>{if(active)setError(e?.message||t.error)}).finally(()=>{if(active)setLoading(false)});return()=>{active=false}},[]);
  const sortedHistory=useMemo(()=>[...history].sort((a,b)=>new Date(a.generated_at).getTime()-new Date(b.generated_at).getTime()),[history]);
  const downloadReport=(report:ReportDefinition)=>{
    setDownloading(report.key);setError(null);
    try{
      const points=sortedHistory.slice(-report.observations);
      if(!points.length)throw new Error(t.empty);
      triggerDownload(buildCsv(report.title,points,language),report.fileName);
    }catch(e:any){setError(e?.message||t.error)}finally{window.setTimeout(()=>setDownloading(null),400);}
  };
  return <div className="space-y-7 max-w-4xl">
    <header><h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">{t.title}</h1><p className="text-slate-400 text-sm mt-2">{t.subtitle}</p></header>
    {error&&<div role="alert" className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm text-amber-200">{error}</div>}
    <section className="rounded-2xl border border-sky-500/20 bg-sky-500/5 p-5"><h2 className="text-sm font-semibold text-white">{t.what}</h2><p className="mt-2 text-sm leading-6 text-slate-300">{t.whatText}</p></section>
    <div className="space-y-4">{REPORTS.map(report=>{const available=Math.min(report.observations,sortedHistory.length);const disabled=loading||available===0||downloading===report.key;return <article key={report.key} className="rounded-2xl bg-[#111827] border border-slate-800 p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div><h3 className="text-sm font-semibold text-white">{report.title}</h3><p className="text-xs text-slate-400 mt-1">{report.description}</p><p className="text-[11px] text-slate-500 mt-2">{loading?t.loading:`${available} ${t.available} · ${t.csv}`}</p></div>
      <button type="button" onClick={()=>downloadReport(report)} disabled={disabled} className="shrink-0 px-4 py-2.5 rounded-xl text-xs font-semibold bg-sky-500 text-slate-950 hover:bg-sky-400 transition disabled:opacity-40 disabled:cursor-not-allowed">{downloading===report.key?t.preparing:t.download}</button>
    </article>})}</div>
    <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-4 text-xs leading-5 text-slate-400">{t.notice}</div>
  </div>;
};
export default ReportsPage;
