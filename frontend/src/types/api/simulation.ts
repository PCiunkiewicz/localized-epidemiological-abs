import { Terrain } from './terrain';

export interface Simulation {
  id?: number;
  name: string;
  mapfile: string;
  xy_scale?: number;
  t_step?: number;
  max_iter?: number;
  save_resolution?: number;
  save_verbose?: boolean;
  terrain?: Terrain[];
}
