import React, { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider, Navigate, useNavigate } from 'react-router-dom';
import { AppShell } from '../components/layout/AppShell';
import { ProtectedRoute } from '../components/common/ProtectedRoute';
import { LanguageProvider } from '../contexts/LanguageContext';

const DashboardPage=lazy(()=>import('../pages/DashboardPage').then(m=>({default:m.DashboardPage})));
const BiomarkersPage=lazy(()=>import('../pages/BiomarkersPage').then(m=>({default:m.BiomarkersPage})));
const TrendsPage=lazy(()=>import('../pages/TrendsPage').then(m=>({default:m.TrendsPage})));
const TimelinePage=lazy(()=>import('../pages/TimelinePage').then(m=>({default:m.TimelinePage})));
const CheckInPage=lazy(()=>import('../pages/CheckInMultimodalPage').then(m=>({default:m.CheckInMultimodalPage})));
const ReportsPage=lazy(()=>import('../pages/ReportsPage').then(m=>({default:m.ReportsPage})));
const PastHistoryPage=lazy(()=>import('../pages/PastHistoryPage').then(m=>({default:m.PastHistoryPage})));
const NotificationsPage=lazy(()=>import('../pages/NotificationsPage').then(m=>({default:m.NotificationsPage})));
const SettingsPage=lazy(()=>import('../pages/SettingsPage').then(m=>({default:m.SettingsPage})));
const ProfilePage=lazy(()=>import('../pages/ProfilePage').then(m=>({default:m.ProfilePage})));
const WelcomePage=lazy(()=>import('../components/NuvyraWelcome').then(m=>({default:m.default})));
const LoginPage=lazy(()=>import('../pages/LoginPage').then(m=>({default:m.LoginPage})));
const RegisterPage=lazy(()=>import('../pages/RegisterPage').then(m=>({default:m.RegisterPage})));

const FallbackLoader=()=> <div className="min-h-screen flex items-center justify-center"><div className="w-8 h-8 rounded-full border-2 border-sky-400 border-t-transparent animate-spin"/></div>;
const lazyElement=(Component:React.LazyExoticComponent<React.ComponentType>)=><Suspense fallback={<FallbackLoader/>}><Component/></Suspense>;

const FirstVisitRedirect: React.FC = () => {
  const completed = localStorage.getItem('nuvyra_onboarding_complete') === 'true';
  return <Navigate to={completed ? '/dashboard' : '/welcome'} replace />;
};

const WelcomeRoute: React.FC = () => {
  const navigate = useNavigate();
  return <WelcomePage onComplete={() => {
    localStorage.setItem('nuvyra_onboarding_complete', 'true');
    navigate('/dashboard', { replace: true });
  }} />;
};

const router=createBrowserRouter([
  {path:'/login',element:lazyElement(LoginPage)},
  {path:'/register',element:lazyElement(RegisterPage)},
  {element:<ProtectedRoute/>,children:[
    {path:'/welcome',element:<WelcomeRoute/>},
    {path:'/',element:<AppShell/>,children:[
      {index:true,element:<FirstVisitRedirect/>},
      {path:'dashboard',element:lazyElement(DashboardPage)},
      {path:'biomarkers',element:lazyElement(BiomarkersPage)},
      {path:'trends',element:lazyElement(TrendsPage)},
      {path:'timeline',element:lazyElement(TimelinePage)},
      {path:'check-in',element:lazyElement(CheckInPage)},
      {path:'reports',element:lazyElement(ReportsPage)},
      {path:'past-history',element:lazyElement(PastHistoryPage)},
      {path:'notifications',element:lazyElement(NotificationsPage)},
      {path:'profile',element:lazyElement(ProfilePage)},
      {path:'settings',element:lazyElement(SettingsPage)}
    ]}
  ]},
  {path:'*',element:<Navigate to="/dashboard" replace/>}
]);

export const AppRouter:React.FC=()=> <LanguageProvider><RouterProvider router={router}/></LanguageProvider>;
export default AppRouter;
