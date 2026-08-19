import React from 'react';
import { NavLink } from 'react-router-dom';
import { NuvyraLogo } from '../common/NuvyraLogo';
import { useAuth } from '../../contexts/AuthContext';
interface SidebarProps { onCloseMobile?: () => void; }
export const Sidebar: React.FC<SidebarProps> = ({ onCloseMobile }) => {
 const { user, logout } = useAuth();
 const navigation = [
  { name:'Overview', href:'/dashboard' }, { name:'Daily Check-in', href:'/check-in', badge:'Active' },
  { name:'Biomarkers', href:'/biomarkers' }, { name:'Trends', href:'/trends' }, { name:'Timeline', href:'/timeline' },
  { name:'Past History', href:'/past-history' }, { name:'Reports', href:'/reports' },
 ];
 return <aside className="w-64 flex-shrink-0 bg-[#0E1524] border-r border-slate-800/80 flex flex-col justify-between h-screen sticky top-0">
  <div className="p-6"><NuvyraLogo size="md" /><div className="mt-8 space-y-1"><p className="px-3 text-[11px] font-semibold tracking-wider text-slate-500 uppercase">Intelligence</p>
   {navigation.map(item=><NavLink key={item.name} to={item.href} onClick={onCloseMobile} className={({isActive})=>`flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium ${isActive?'bg-sky-500/10 text-sky-400 border border-sky-500/20':'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'}`}><span>{item.name}</span>{item.badge&&<span className="px-2 py-0.5 text-[10px] rounded-full bg-sky-500/20 text-sky-300 border border-sky-500/30">{item.badge}</span>}</NavLink>)}
  </div></div>
  <div className="p-4 border-t border-slate-800/60 bg-[#0B101D] space-y-2"><NavLink to="/settings" onClick={onCloseMobile} className={({isActive})=>`block px-3 py-2 rounded-xl text-sm ${isActive?'bg-slate-800 text-white':'text-slate-400'}`}>Privacy & Settings</NavLink><div className="px-3 py-2.5 flex items-center justify-between rounded-xl bg-slate-900/80 border border-slate-800"><div className="truncate"><p className="text-xs text-slate-200 truncate">{user?.full_name||'Participant'}</p><p className="text-[10px] text-slate-500 font-mono truncate">{user?.subject_anonymous_id||'Participant'}</p></div><button onClick={logout} title="Sign out" className="text-slate-400 hover:text-rose-400">↪</button></div></div>
 </aside>;
};
