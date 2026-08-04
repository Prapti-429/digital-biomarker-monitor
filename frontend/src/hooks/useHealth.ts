import { useContext } from 'react';
import { HealthContext } from '../contexts/HealthContext';

export const useHealth = () => {
  const context = useContext(HealthContext);
  if (context === undefined) {
    throw new Error('useHealth must be instantiated within a valid structural HealthProvider layer.');
  }
  return context;
};