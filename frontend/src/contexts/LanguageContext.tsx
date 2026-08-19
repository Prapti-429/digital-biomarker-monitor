import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

export type AppLanguage = 'English' | 'Hindi' | 'French';

interface LanguageContextValue { language: AppLanguage; setLanguage: (language: AppLanguage) => void; }

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined);
const STORAGE_KEY = 'nuvyra_language';

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<AppLanguage>(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved === 'Hindi' || saved === 'French' ? saved : 'English';
  });
  const setLanguage = (next: AppLanguage) => { setLanguageState(next); localStorage.setItem(STORAGE_KEY, next); };
  useEffect(() => { document.documentElement.lang = language === 'Hindi' ? 'hi' : language === 'French' ? 'fr' : 'en'; }, [language]);
  const value = useMemo(() => ({ language, setLanguage }), [language]);
  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
};

export const useLanguage = () => {
  const value = useContext(LanguageContext);
  if (!value) throw new Error('useLanguage must be used inside LanguageProvider');
  return value;
};
