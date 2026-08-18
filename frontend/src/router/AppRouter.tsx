import React, { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { ProtectedRoute } from '../components/common/ProtectedRoute';

const DashboardPage = lazy(() => import('../pages/DashboardPage').then(m => ({ default: m.DashboardPage })));
const BiomarkersPage = lazy(() => import('../pages/BiomarkersPage').then(m => ({ default: m.BiomarkersPage })));
const TrendsPage = lazy(() => import('../pages/TrendsPage').then(m => ({ default: m.TrendsPage })));
const TimelinePage = lazy(() => import('../pages/TimelinePage').then(m => ({ default: m.TrendsPage })));
const CheckInPage = lazy(() => import('../pages/CheckInAIPage').then(m => ({ default: m.CheckInAIPage })));
const ReportsPage = lazy(() => import('../pages/ReportsPage').then(m => ({ default: m.ReportsPage })));
const SettingsPage = lazy(() => import('../pages/SettingsPage').then(m => ({ default: m.SettingsPage })));
const LoginPage = lazy(() => import('../pages/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('../pages/RegisterPage').then(m => ({ default: m.RegisterPage })));

const FallbackLoader = () => <div className="min-h-[60vh] flex items-center justify-center"><div className="w-8 h-8 rounded-full border-2 border-sky-400 border-t-transparent animate-spin" /></div>;
const lazyElement = (Component: React.LazyExoticComponent<React.ComponentType>) => <Suspense fallback={<FallbackLoader />}><Component /></Suspense>;

const router = createBrowserRouter([
  { path: '/login', element: lazyElement(LoginPage) },
  { path: '/register', element: lazyElement(RegisterPage) },
  {
    element: <ProtectedRoute />,
    children: [{
      path: '/', element: <AppShell />, children: [
        { index: true, element: <Navigate to="/dashboard" replace /> },
        { path: 'dashboard', element: lazyElement(DashboardPage) },
        { path: 'biomarkers', element: lazyElement(BiomarkersPage) },
        { path: 'trends', element: lazyElement(TrendsPage) },
        { path: 'timeline', element: lazyElement(TimelinePage) },
        { path: 'check-in', element: lazyElement(CheckInPage) },
        { path: 'reports', element: lazyElement(ReportsPage) },
        { path: 'settings', element: lazyElement(SettingsPage) },
      ],
    }],
  },
  { path: '*', element: <Navigate to="/dashboard" replace /> },
]);

export const AppRouter: React.FC = () => <RouterProvider router={router} />;
export default AppRouter;
