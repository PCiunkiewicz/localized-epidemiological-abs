import { useEffect, useState } from 'react';
import DataGrid, { SelectColumn } from 'react-data-grid';
import type { Column } from 'react-data-grid';

import { Simulation } from '../../../types/api';
import SimulationDataService from '../../../utils/api/simulation';

const columns: readonly Column<Simulation>[] = [
  SelectColumn,
  {
    key: 'id',
    name: 'ID',
    resizable: true,
    frozen: true,
  },
  {
    key: 'name',
    name: 'Name',
    resizable: true,
    frozen: true,
  },
  {
    key: 'mapfile',
    name: 'Map File',
    resizable: true,
    frozen: true,
  },
  {
    key: 'xy_scale',
    name: 'X-Y Scale (cm/px)',
    resizable: true,
    frozen: true,
  },
  {
    key: 't_step',
    name: 'Timestep Size (s)',
    resizable: true,
  },
  {
    key: 'max_iter',
    name: 'Max Iterations',
    resizable: true,
  },
  {
    key: 'save_resolution',
    name: 'Save Resolution (timesteps)',
    resizable: true,
  },
  {
    key: 'save_verbose',
    name: 'Save Verbose',
    resizable: true,
    formatter: ({ row }) => <>{Boolean(row.save_verbose).toString()}</>,
  },
  // {
  //   key: 'terrain',
  //   name: 'Terrains',
  //   resizable: true,
  //   formatter: ({ row }) => <>{map the terrains array to a string}</>,
  // },
];

export default function ViewSimulation() {
  const [simulations, setSimulations] = useState<Simulation[]>([]);

  useEffect(() => {
    SimulationDataService.list().then((response) => {
      setSimulations(response.data);
    });
  }, []);

  return <DataGrid columns={columns} rows={simulations} />;
}
