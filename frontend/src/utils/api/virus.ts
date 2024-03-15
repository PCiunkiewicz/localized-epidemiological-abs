import { Virus } from '../../types/api';
import http from './request';

export const formDefault: Virus = {
  id: undefined,
  name: '',
  attack_rate: 0.07,
  infection_rate: 0.021,
  fatality_rate: 0.01,
};

class VirusDataService {
  async list() {
    return http.get('/viruses/');
  }
  get(id: number) {
    return http.get(`/viruses/${id}`);
  }
  post(data: Virus) {
    return http.post('/viruses/', data);
  }
  patch(id: number, data: Virus) {
    return http.patch(`/viruses/${id}/`, data);
  }
  delete(id: number) {
    return http.delete(`/viruses/${id}/`);
  }
}

export default new VirusDataService();
