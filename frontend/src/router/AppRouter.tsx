import React, { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { ProtectedRoute } from '../components/common/ProtectedRoute';

const DashboardPage = lazy(() => import('../pages/DashboardPage').then(m => ({ default: m.DashboardPage })));
const BiomarkersPage = lazy(() => import('../pages/BiomarkersPage').then(m => ({ default: m.BiomarkersPage })));
const TrendsPage = lazy(() => import('../pages/TrendsPage').then(m => ({ default: m.TrendsPage })));
const TimelinePage = lazy(() => import('../pages/TimelinePage').then(m => ({ default: m.TimelinePage })));
const CheckInPage = lazy(() => import('../pages/CheckInPage').then(m => ({ default: m.CheckInPage })));
const ReportsPage = lazy(() => import('../pages/ReportsPage').then(m => ({ default: m.ReportsPage })));
const SettingsPage = lazy(() => import('../pages/SettingsPage').then(m => ({ default: m.SettingsPage })));
const LoginPage = lazy(() => import('../pages/LoginPage').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('../pages/RegisterPage').then(m => ({ default: m.RegisterPage })));

const FallbackLoader = () => (
  <div className="min-h-[60vh] flex items-center justify-center">
    <div className="w-8 h-8 rounded-full border-2 border-sky-400 border-t-transparent animate-spin" />
  </div>
);

const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <Suspense fallback={<FallbackLoader />}>
        <LoginPage />
      </Suspense>
    ),
  },
  {
    path: '/register',
    element: (
      <Suspense fallback={<FallbackLoader />}>
        <RegisterPage />
      </Suspense>
    ),
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        path: '/',
        element: <AppShell />,
        children: [
          {
            index: true,
            element: <Navigate to="/dashboard" replace />,
          },
          {
            path: 'dashboard',
            element: (
              <Suspense fallback={<FallbackLoader />}>
                <DashboardPage />
              </Suspense>
            ),
          },
          {
            path: 'biomarkers',
            element: (
              <Suspense fallback={<FallbackLoader />}>
                <BiomarkersPage />
              </Suspense>
            ),
          },
          {
            path: 'trends',
            element: (
              <Suspense fallback={<FallbackLoader />}>
                <TrendsPage />
              </Suspense>
            ),
          },
          {
            path: 'timeline',
            element: (
              <Suspense fallback={<FallbackLoader />}>
                <TimelinePage />
              </Suspense>
            ),
          },
          {
            path: 'check-in',
            element: (
              <Suspense fallback={<FallbackLoader />}>
                <CheckInPage />
              </Suspense>
            ),
          },
          {
            path: 'reports',
            element: (
              <Suspense fallback={<FallbackLoader />}>
                <ReportsPage />
              </Suspense>
            ),
          },
          {
            path: 'settings',
            element: (
              <Suspense fallback={<FallbackLoader />}>
                <SettingsPage />
              </Suspense>
            ),
          },
        ],
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/dashboard" replace />,
  },
]);

export const AppRouter: React.FC = () => {
  return <RouterProvider router={router} />;
};

export default AppRouter;