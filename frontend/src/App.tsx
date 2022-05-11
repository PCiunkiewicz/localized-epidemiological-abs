import React from 'react';
import logo from './logo.svg';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import { ThemeWrapper } from './contexts/ThemeContext';
import { MainNavBar } from './components/navigation';

function App() {
  return (
    <ThemeWrapper>
      <div className='App'>
        <MainNavBar></MainNavBar>
        <header className='App-header'>
          <img src={logo} className='App-logo' alt='logo' />
          <p>
            Edit <code>src/App.tsx</code> and save to reload.
          </p>
          <a
            className='App-link'
            href='https://reactjs.org'
            target='_blank'
            rel='noopener noreferrer'
          >
            Learn React
          </a>
        </header>
      </div>
    </ThemeWrapper>
  );
}

export default App;
