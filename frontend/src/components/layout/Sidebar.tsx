import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { NuvyraLogo } from '../common/NuvyraLogo';
import { useAuth } from '../../contexts/AuthContext';

interface SidebarProps { onCloseMobile?: () => void; }

export const Sidebar: React.FC<SidebarProps> = ({ onCloseMobile }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const navigation = [
    { name: 'Overview', href: '/dashboard' },
    { name: 'Daily Check-in', href: '/check-in', badge: 'Active' },
    { name: 'Biomarkers', href: '/biomarkers' },
    { name: 'Trends', href: '/trends' },
    { name: 'Timeline', href: '/timeline' },
    { name: 'Past History', href: '/past-history' },
    { name: 'Notifications', href: '/notifications' },
    { name: 'Reports', href: '/reports' },
  ];

  const confirmLogout = () => {
    setShowLogoutConfirm(false);
    logout();
  };

  return (
    <>
      <aside className="w-64 flex-shrink-0 bg-[#0E1524] border-r border-slate-800/80 flex flex-col justify-between h-screen sticky top-0">
        <div className="p-6">
          <NuvyraLogo size="md" />
          <div className="mt-8 space-y-1">
            <p className="px-3 text-[11px] font-semibold tracking-wider text-slate-500 uppercase">Intelligence</p>
            {navigation.map(item => (
              <NavLink
                key={item.name}
                to={item.href}
                onClick={onCloseMobile}
                className={({ isActive }) => `flex items-center justify-between px-3 py-2.5 rounded-xl text-sm font-medium ${isActive ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'}`}
              >
                <span>{item.name}</span>
                {item.badge && <span className="px-2 py-0.5 text-[10px] rounded-full bg-sky-500/20 text-sky-300 border border-sky-500/30">{item.badge}</span>}
              </NavLink>
            ))}
          </div>
        </div>

        <div className="p-4 border-t border-slate-800/60 bg-[#0B101D] space-y-2">
          <NavLink
            to="/profile"
            onClick={onCloseMobile}
            className={({ isActive }) => `flex items-center gap-2 px-3 py-2 rounded-xl text-sm ${isActive ? 'bg-sky-500/10 text-white border border-sky-500/20' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
          >
            <span aria-hidden="true">👤</span>
            <span>Profile</span>
          </NavLink>

          <NavLink
            to="/settings"
            onClick={onCloseMobile}
            className={({ isActive }) => `block px-3 py-2 rounded-xl text-sm ${isActive ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800/40'}`}
          >
            Privacy & Settings
          </NavLink>

          <button
            type="button"
            onClick={() => navigate('/profile')}
            className="w-full px-3 py-2.5 flex items-center justify-between rounded-xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 text-left"
            aria-label="Open your profile"
          >
            <div className="truncate">
              <p className="text-xs text-slate-200 truncate">{user?.full_name || 'Participant'}</p>
              <p className="text-[10px] text-slate-500 font-mono truncate">{user?.email || user?.subject_anonymous_id || 'Participant'}</p>
            </div>
            <span className="text-slate-500 text-xs ml-2" aria-hidden="true">›</span>
          </button>

          <button
            type="button"
            onClick={() => setShowLogoutConfirm(true)}
            className="w-full flex items-center gap-2 px-3 py-2.5 rounded-xl text-sm text-slate-400 hover:text-rose-300 hover:bg-rose-500/10 transition"
            title="Log out"
          >
            <span className="text-lg leading-none" aria-hidden="true">↪</span>
            <span>Log out</span>
          </button>
        </div>
      </aside>

      {showLogoutConfirm && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 p-4" role="dialog" aria-modal="true" aria-labelledby="logout-title">
          <div className="w-full max-w-sm rounded-2xl border border-slate-700 bg-[#111827] p-6 shadow-2xl">
            <div className="flex items-center gap-3 mb-3">
              <div className="h-10 w-10 rounded-full bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-300 text-xl" aria-hidden="true">↪</div>
              <h2 id="logout-title" className="text-lg font-semibold text-white">Log out of NUVYRA?</h2>
            </div>
            <p className="text-sm leading-6 text-slate-400">You will be signed out of this device. Your account and saved NUVYRA data will not be deleted.</p>
            <div className="mt-6 grid grid-cols-2 gap-3">
              <button type="button" onClick={() => setShowLogoutConfirm(false)} className="rounded-xl border border-slate-700 px-4 py-2.5 text-sm text-slate-200 hover:bg-slate-800">Cancel</button>
              <button type="button" onClick={confirmLogout} className="rounded-xl bg-rose-500 px-4 py-2.5 text-sm font-semibold text-white hover:bg-rose-400">Log out</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
