import { Simulation } from '../../types/api/simulation';

export const formDefault: Simulation = {
  id: undefined,
  name: '',
  mapfile: '',
  xy_scale: 10.0,
  t_step: 1,
  max_iter: 100,
  save_resolution: 60,
  save_verbose: false,
  terrain: [],
};
