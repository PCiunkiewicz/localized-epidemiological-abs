import { Terrain } from '../../types/api/terrain';

export const formDefault: Terrain = {
  id: undefined,
  name: '',
  value: '',
  color: '',
  material: undefined,
  walkable: true,
  interactive: false,
  restricted: false,
  access_level: 0,
};
