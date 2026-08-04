import React from 'react';
import ReactDOM from 'react-dom/client';
import AppRouter from './router/AppRouter';
import { HealthProvider } from './contexts/HealthContext';
import './styles/index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <HealthProvider>
      <AppRouter />
    </HealthProvider>
  </React.StrictMode>
);