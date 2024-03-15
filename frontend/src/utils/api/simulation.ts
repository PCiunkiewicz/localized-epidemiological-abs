import { Simulation } from '../../types/api';
import http from './request';

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

export class SimulationDataService {
  list() {
    return http.get('/simulations/');
  }
  get(id: number) {
    return http.get(`/simulations/${id}`);
  }
  post(data: Simulation) {
    return http.post('/simulations/', data);
  }
  patch(id: number, data: Simulation) {
    return http.patch(`/simulations/${id}/`, data);
  }
  delete(id: number) {
    return http.delete(`/simulations/${id}/`);
  }
}

export default new SimulationDataService();
