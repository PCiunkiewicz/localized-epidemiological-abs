import { createContext, useContext } from 'react';

export const APIContext = createContext<any>(null);

export const useAPIContext = () => {
  const context = useContext(APIContext);

  if (!context) throw new Error('useAPIContext must be called from within the APIWrapper');

  return context;
};
