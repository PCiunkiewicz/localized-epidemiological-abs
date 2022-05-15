import { createContext, useContext } from 'react';

export const NavContext = createContext<any>(null);

export const useNavContext = () => {
  const context = useContext(NavContext);

  if (!context) throw new Error('useNavContext must be called from within the NavWrapper');

  return context;
};
