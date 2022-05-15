export interface Terrain {
  id?: number;
  name: string;
  value: string;
  color: string;
  material?: string;
  walkable?: boolean;
  interactive?: boolean;
  restricted?: boolean;
  access_level?: number;
}
