import { BrowserRouter, Routes, Route } from 'react-router-dom';
// import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';

import { MainNavBar } from './components/navigation';
import Home from './components/Home';

import { NavWrapper } from './contexts/NavContext';
import ViewTerrain from './components/api/terrain/ViewTerrain';
import ViewSimulation from './components/api/simulation/ViewSimulation';
import ViewVirus from './components/api/virus/ViewVirus';

function App() {
  return (
    <BrowserRouter>
      <NavWrapper>
        <MainNavBar />
        <Routes>
          <Route path='/home' element={<Home />} />
          <Route path='/terrains' element={<ViewTerrain />} />
          <Route path='/simulations' element={<ViewSimulation />} />
          <Route path='/viruses' element={<ViewVirus />} />
        </Routes>
      </NavWrapper>
    </BrowserRouter>
  );
}

export default App;
