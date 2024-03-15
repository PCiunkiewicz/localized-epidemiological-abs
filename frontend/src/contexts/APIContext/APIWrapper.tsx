import { FC, useState } from 'react';
import { APIContext } from './APIContext';

// TODO: Set up APIWrapper with api requests
export const APIWrapper: FC<any> = ({ children }) => {
  const [newTerrain, setNewTerrain] = useState(false);
  const handleNewTerrain = () => setNewTerrain(!newTerrain);

  const [newSim, setNewSim] = useState(false);
  const handleNewSim = () => setNewSim(!newSim);

  const [newVirus, setNewVirus] = useState(false);
  const handleNewVirus = () => setNewVirus(!newVirus);

  return (
    <div>
      <APIContext.Provider
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
      </APIContext.Provider>
    </div>
  );
};
