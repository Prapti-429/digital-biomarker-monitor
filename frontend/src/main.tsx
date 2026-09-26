import React from 'react';
import ReactDOM from 'react-dom/client';
import { AuthProvider } from './contexts/AuthContext';
import { AppRouter } from './router/AppRouter';
import './styles/index.css';

/**
 * Vite gives lazy-loaded pages content hashes. After a new deployment, a
 * browser tab can still have an older index/app bundle that points at a
 * chunk which no longer exists. React then surfaces "Failed to fetch
 * dynamically imported module". Recover once by reloading the current URL
 * so the browser gets the newest manifest/chunk references.
 */
const CHUNK_RELOAD_KEY = 'nuvyra_chunk_reload_attempted';

const recoverFromStaleChunk = () => {
  try {
    if (sessionStorage.getItem(CHUNK_RELOAD_KEY) === 'true') return;
    sessionStorage.setItem(CHUNK_RELOAD_KEY, 'true');
    window.location.reload();
  } catch {
    window.location.reload();
  }
};

window.addEventListener('unhandledrejection', (event) => {
  const reason = event.reason;
  const message = reason instanceof Error ? reason.message : String(reason ?? '');
  if (/failed to fetch dynamically imported module|importing a module script failed/i.test(message)) {
    recoverFromStaleChunk();
  }
});

window.addEventListener('error', (event) => {
  const message = event.message || '';
  if (/failed to fetch dynamically imported module|importing a module script failed/i.test(message)) {
    recoverFromStaleChunk();
  }
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  </React.StrictMode>
);