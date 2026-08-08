import { useContext } from 'react';
import { HealthContext, HealthContextType } from '../contexts/HealthContext';

export const useHealth = (): HealthContextType => {
  const context = useContext(HealthContext);
  if (!context) {
    throw new Error('useHealth must be used within a HealthProvider');
  }
  return context;
};

export default useHealth;