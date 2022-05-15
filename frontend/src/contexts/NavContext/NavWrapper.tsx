import { FC, useState } from 'react';
import { NavContext } from './NavContext';

export const NavWrapper: FC<any> = ({ children }) => {
  const [newTerrain, setNewTerrain] = useState(false);
  const handleNewTerrain = () => setNewTerrain(!newTerrain);

  const [newSim, setNewSim] = useState(false);
  const handleNewSim = () => setNewSim(!newSim);

  const [newVirus, setNewVirus] = useState(false);
  const handleNewVirus = () => setNewVirus(!newVirus);

  return (
    <div>
      <NavContext.Provider
        value={{
          newTerrain,
          handleNewTerrain,
          newSim,
          handleNewSim,
          newVirus,
          handleNewVirus,
        }}
      >
        {children}
      </NavContext.Provider>
    </div>
  );
};
