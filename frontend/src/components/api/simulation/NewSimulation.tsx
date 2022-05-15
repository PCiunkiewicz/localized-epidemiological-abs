import { SyntheticEvent, useState } from 'react';
import { Button, Col, Form, Modal, Row } from 'react-bootstrap';

import { useNavContext } from '../../../contexts/NavContext';
import { Simulation } from '../../../types/api/simulation';
import { Terrain } from '../../../types/api/terrain';
import { formDefault } from '../../../utils/api/simulation';
import NewTerrain from '../terrain/NewTerrain';

export default function NewSimulation() {
  const { newSim, handleNewSim, newTerrain, handleNewTerrain } = useNavContext();

  const [formData, setFormData] = useState<Simulation>(formDefault);

  const handleChange = (name: string, value: string | number | boolean) => {
    setFormData({ ...formData, [name]: value });
  };

  const onSave = (e: SyntheticEvent) => {
    e.preventDefault();
    // const formData = new FormData(e.target),
    //   formDataObj = Object.fromEntries(formData.entries());
    // console.log(formDataObj);
    console.log(formData);
    handleClose();
  };

  // TODO: Fix `any` type on event
  const onTerrainChange = (e: any) => {
    const selected = e.target.selectedOptions;
    const selectedTerrain = [].slice.call(selected).map((x: any) => x.value);
    setFormData({ ...formData, terrain: selectedTerrain });
  };

  const terrains: Terrain[] = [
    {
      id: 1,
      name: 'WALL',
      value: '#000000',
      color: '#000000',
      material: undefined,
      walkable: false,
      restricted: true,
      access_level: 0,
    },
    {
      id: 2,
      name: 'AGENT0',
      value: '#0000ff',
      color: '#0000ff',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 3,
      name: 'PUBLIC',
      value: '#00ff00',
      color: '#00ff00',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 4,
      name: 'PRINTER',
      value: '#01ff00',
      color: '#01ff00',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 5,
      name: 'MICROWAVE',
      value: '#02ff00',
      color: '#02ff00',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 6,
      name: 'TEA',
      value: '#03ff00',
      color: '#03ff00',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 7,
      name: 'AGENT1',
      value: '#0100ff',
      color: '#0100ff',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 8,
      name: 'AGENT2',
      value: '#0200ff',
      color: '#0200ff',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 9,
      name: 'AGENT3',
      value: '#0300ff',
      color: '#0300ff',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 10,
      name: 'AGENT4',
      value: '#0400ff',
      color: '#0400ff',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 11,
      name: 'AGENT5',
      value: '#0500ff',
      color: '#0500ff',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 12,
      name: 'AGENT6',
      value: '#0600ff',
      color: '#0600ff',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 13,
      name: 'AGENT7',
      value: '#0700ff',
      color: '#0700ff',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 14,
      name: 'AGENT8',
      value: '#0800ff',
      color: '#0800ff',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 15,
      name: 'DESK',
      value: '#7f7f7f',
      color: '#7f7f7f',
      material: undefined,
      walkable: false,
      restricted: true,
      access_level: 0,
    },
    {
      id: 16,
      name: 'WINDOW',
      value: '#c3c3c3',
      color: '#c3c3c3',
      material: undefined,
      walkable: false,
      restricted: true,
      access_level: 0,
    },
    {
      id: 17,
      name: 'EXIT',
      value: '#ffff00',
      color: '#ffff00',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
    {
      id: 18,
      name: 'OPEN',
      value: '#ffffff',
      color: '#ffffff',
      material: undefined,
      walkable: true,
      restricted: true,
      access_level: 0,
    },
  ];

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
