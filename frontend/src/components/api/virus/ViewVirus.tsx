import { useEffect, useState } from 'react';
import DataGrid, { SelectColumn } from 'react-data-grid';
import type { Column } from 'react-data-grid';

import { Virus } from '../../../types/api';
import VirusDataService from '../../../utils/api/virus';

const columns: readonly Column<Virus>[] = [
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
    key: 'attack_rate',
    name: 'Attack Rate',
    resizable: true,
  },
  {
    key: 'infection_rate',
    name: 'IPR',
    resizable: true,
  },
  {
    key: 'fatality_rate',
    name: 'Fatality Rate',
    resizable: true,
  },
];

export default function ViewVirus() {
  const [viruses, setViruses] = useState<Virus[]>([]);

  useEffect(() => {
    VirusDataService.list().then((response) => {
      setViruses(response.data);
    });
  }, []);

  return <DataGrid columns={columns} rows={viruses} />;
}
