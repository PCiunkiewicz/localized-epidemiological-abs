import { SyntheticEvent, useEffect, useState } from 'react';
import { Button, Col, Form, Modal, Row } from 'react-bootstrap';

import { useNavContext } from '../../../contexts/NavContext';
import { Simulation, Terrain } from '../../../types/api';
import SimulationDataService, { formDefault } from '../../../utils/api/simulation';
import TerrainDataService from '../../../utils/api/terrain';
import NewTerrain from '../terrain/NewTerrain';

export default function NewSimulation() {
  const { newSim, handleNewSim, newTerrain, handleNewTerrain } = useNavContext();

  const [formData, setFormData] = useState<Simulation>(formDefault);
  const [terrains, setTerrains] = useState<Terrain[]>([]);

  const handleChange = (name: string, value: string | number | boolean) => {
    if (name === 'mapfile') {
      value = String(value).replace('C:\\fakepath\\', 'data/mapfiles/');
    }
    setFormData({ ...formData, [name]: value });
  };

  const onSave = (e: SyntheticEvent) => {
    e.preventDefault();
    SimulationDataService.post(formData);
    console.log(formData);
    handleClose();
  };

  // TODO: Fix `any` type on event
  const onTerrainChange = (e: any) => {
    const selected = e.target.selectedOptions;
    const selectedTerrain = [].slice.call(selected).map((x: any) => x.value);
    setFormData({ ...formData, terrain: selectedTerrain });
  };

  useEffect(() => {
    TerrainDataService.list().then((response) => {
      setTerrains(response.data);
    });
  }, [newTerrain]);

  const handleClose = () => {
    handleNewSim();
    setFormData(formDefault);
  };

  return (
    <>
      <Modal size='lg' show={newSim && !newTerrain} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>New Simulation</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={onSave}>
            <Row className='my-3'>
              <Col>
                <Form.Label>Name</Form.Label>
                <Form.Control
                  type='text'
                  required
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  placeholder='sim-example'
                  autoFocus
                />
              </Col>
            </Row>
            <Row className='my-3'>
              <Col>
                <Form.Label>Map File</Form.Label>
                <Form.Control type='file' required onChange={(e) => handleChange('mapfile', e.target.value)} />
              </Col>
            </Row>
            <Row className='my-3'>
              <Col>
                <Form.Label>Timestep Size (s)</Form.Label>
                <Form.Control
                  type='number'
                  value={formData.t_step}
                  onChange={(e) => handleChange('t_step', e.target.value)}
                />
              </Col>
              <Col>
                <Form.Label>Save Resolution (steps)</Form.Label>
                <Form.Control
                  type='number'
                  value={formData.save_resolution}
                  onChange={(e) => handleChange('save_resolution', e.target.value)}
                />
              </Col>
              <Col>
                <Form.Label>Maximum Iterations</Form.Label>
                <Form.Control
                  type='number'
                  value={formData.max_iter}
                  onChange={(e) => handleChange('max_iter', e.target.value)}
                />
              </Col>
              <Col>
                <Form.Label>Spatial Scale</Form.Label>
                <Form.Control
                  type='text'
                  required
                  value={formData.xy_scale}
                  onChange={(e) => handleChange('xy_scale', e.target.value)}
                />
              </Col>
            </Row>
            <Row className='my-3'>
              <Col>
                <Form.Check
                  label='Save Verbose'
                  type='checkbox'
                  checked={formData.save_verbose}
                  onChange={(e) => handleChange('save_verbose', e.target.checked)}
                />
              </Col>
            </Row>
            <Row className='my-3'>
              <Col>
                <Form.Label>Terrain</Form.Label>
                <Form.Control as='select' multiple onChange={onTerrainChange}>
                  {terrains
                    .sort((a, b) => (a.name > b.name ? 1 : -1))
                    .map((opt) => (
                      <option key={opt.id} value={opt.id}>
                        {opt.name}
                      </option>
                    ))}
                </Form.Control>
              </Col>
            </Row>
            <Button size='sm' variant='primary' onClick={handleNewTerrain}>
              New Terrain
            </Button>

            <Row className='my-3'>
              <Button type='submit'>Save Changes</Button>
            </Row>
          </Form>
        </Modal.Body>
      </Modal>
      <NewTerrain />
    </>
  );
}
