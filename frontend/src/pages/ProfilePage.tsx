import React from 'react';
import { useAuth } from '../contexts/AuthContext';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();
  const initials = (user?.full_name || user?.email || 'U').trim().charAt(0).toUpperCase();

  return (
    <div className="max-w-4xl space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">Your Profile</h1>
        <p className="mt-1 text-sm text-slate-400">Manage your NUVYRA account and understand how your account information is used.</p>
      </div>

      <section className="rounded-2xl border border-slate-800 bg-[#111827] p-6">
        <div className="flex flex-col sm:flex-row sm:items-center gap-5">
          <div className="h-16 w-16 rounded-full bg-gradient-to-br from-sky-500 to-teal-400 flex items-center justify-center text-xl font-bold text-slate-950" aria-hidden="true">{initials}</div>
          <div className="min-w-0">
            <h2 className="text-xl font-semibold text-white truncate">{user?.full_name || 'Participant'}</h2>
            <p className="text-sm text-slate-400 truncate">{user?.email || 'Email unavailable'}</p>
            {user?.subject_anonymous_id && <p className="mt-1 text-xs font-mono text-sky-400">Participant ID: {user.subject_anonymous_id}</p>}
          </div>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-[#111827] p-6 space-y-5">
        <div className="flex items-center gap-2"><h2 className="text-base font-semibold text-white">Account information</h2><span title="This information comes from your authenticated NUVYRA account." className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-slate-600 text-xs text-slate-400">i</span></div>
        <div className="grid sm:grid-cols-2 gap-4">
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4"><p className="text-xs text-slate-500">Name</p><p className="mt-1 text-sm text-white">{user?.full_name || 'Not provided'}</p></div>
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4"><p className="text-xs text-slate-500">Email</p><p className="mt-1 text-sm text-white break-all">{user?.email || 'Not available'}</p></div>
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4"><p className="text-xs text-slate-500">Account status</p><p className="mt-1 text-sm text-emerald-300">{user?.is_active ? 'Active' : 'Inactive'}</p></div>
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4"><p className="text-xs text-slate-500">Role</p><p className="mt-1 text-sm text-white">{user?.role || 'Participant'}</p></div>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-[#111827] p-6 space-y-4">
        <div className="flex items-center gap-2"><h2 className="text-base font-semibold text-white">Password & account access</h2><span title="Forgot-password recovery should change your password without deleting your account." className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-slate-600 text-xs text-slate-400">i</span></div>
        <p className="text-sm leading-6 text-slate-400">If you forget your password, use the password-recovery option on the sign-in screen. Recovering a password should not erase your check-ins, personal baseline, history, or uploaded documents.</p>
        <p className="text-sm leading-6 text-slate-400">If you intentionally want a completely new account, use the account-deletion process only after confirming that you understand that deletion is separate from logging out.</p>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-[#111827] p-6 space-y-4">
        <div className="flex items-center gap-2"><h2 className="text-base font-semibold text-white">About your data</h2><span title="NUVYRA uses your check-in information for longitudinal research-prototype analysis. It is not a diagnosis." className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-slate-600 text-xs text-slate-400">i</span></div>
        <p className="text-sm leading-6 text-slate-400">NUVYRA is a research prototype for longitudinal digital-biomarker monitoring. Your measurements are compared mainly with your own historical pattern. AI outputs are informational and do not replace a qualified healthcare professional.</p>
      </section>
    </div>
  );
};
