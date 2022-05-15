import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
// import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import { MainNavBar } from './components/navigation';
import Home from './components/Home';
import { NavWrapper } from './contexts/NavContext';

function App() {
  return (
    <BrowserRouter>
      <NavWrapper>
        <MainNavBar />
        <Routes>
          <Route path='/home' element={<Home />} />
          <Route path='/home' element={<Home />} />
        </Routes>
      </NavWrapper>
    </BrowserRouter>
  );
}

export default App;
