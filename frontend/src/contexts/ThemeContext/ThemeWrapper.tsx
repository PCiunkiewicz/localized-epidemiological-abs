import { FC, useState } from 'react';
import { ThemeContext } from './ThemeContext';

export const ThemeWrapper: FC<any> = ({ children }) => {
  const [darkMode, setDarkMode] = useState(false);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div>
      <ThemeContext.Provider value={{ darkMode, toggleDarkMode }}>
        {children}
      </ThemeContext.Provider>
    </div>
  );
};
