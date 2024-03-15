import { Terrain } from '../../types/api';
import http from './request';

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

class TerrainDataService {
  async list() {
    return http.get('/terrains/');
  }
  get(id: number) {
    return http.get(`/terrains/${id}`);
  }
  post(data: Terrain) {
    return http.post('/terrains/', data);
  }
  patch(id: number, data: Terrain) {
    return http.patch(`/terrains/${id}/`, data);
  }
  delete(id: number) {
    return http.delete(`/terrains/${id}/`);
  }
}

export default new TerrainDataService();
