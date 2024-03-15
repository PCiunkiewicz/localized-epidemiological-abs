import { useEffect, useState } from 'react';
import DataGrid, { SelectColumn } from 'react-data-grid';
import type { Column } from 'react-data-grid';

import { Terrain } from '../../../types/api';
import TerrainDataService from '../../../utils/api/terrain';

const colorFormatter = (row: Terrain) => {
  return (
    <>
      <svg width='20' height='20'>
        <rect width='20' height='20' style={{ fill: row.value }} />
      </svg>
      {row.value}
    </>
  );
};

const columns: readonly Column<Terrain>[] = [
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
    key: 'value',
    name: 'Value',
    resizable: true,
    formatter: ({ row }) => colorFormatter(row),
  },
  {
    key: 'color',
    name: 'Color',
    resizable: true,
    formatter: ({ row }) => colorFormatter(row),
  },
  {
    key: 'material',
    name: 'Material',
    resizable: true,
  },
  {
    key: 'walkable',
    name: 'Walkable',
    resizable: true,
    formatter: ({ row }) => <>{Boolean(row.walkable).toString()}</>,
  },
  {
    key: 'interactive',
    name: 'Interactive',
    resizable: true,
    formatter: ({ row }) => <>{Boolean(row.interactive).toString()}</>,
  },
  {
    key: 'restricted',
    name: 'Restricted',
    resizable: true,
    formatter: ({ row }) => <>{Boolean(row.restricted).toString()}</>,
  },
  {
    key: 'access_level',
    name: 'Access Level',
    resizable: true,
  },
];

export default function ViewTerrain() {
  const [terrains, setTerrains] = useState<Terrain[]>([]);

  useEffect(() => {
    TerrainDataService.list().then((response) => {
      setTerrains(response.data);
    });
  }, []);

  return <DataGrid columns={columns} rows={terrains} />;
}
