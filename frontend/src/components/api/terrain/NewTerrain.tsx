import { SyntheticEvent, useState } from 'react';
import { Button, Col, Form, Modal, Row } from 'react-bootstrap';

import { useNavContext } from '../../../contexts/NavContext';
import { Terrain } from '../../../types/api';
import TerrainDataService, { formDefault } from '../../../utils/api/terrain';

export default function NewTerrain() {
  const { newTerrain, handleNewTerrain } = useNavContext();
  const [formData, setFormData] = useState<Terrain>(formDefault);

  const handleChange = (name: string, value: string | number | boolean) => {
    setFormData({ ...formData, [name]: value });
  };

  const onSave = (e: SyntheticEvent) => {
    e.preventDefault();
    console.log(formData);
    TerrainDataService.post(formData);
    handleClose();
  };

  const handleClose = () => {
    handleNewTerrain();
    setFormData(formDefault);
  };

  return (
    <>
      <Modal show={newTerrain} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>New Terrain</Modal.Title>
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
                  placeholder='TERRAIN'
                  autoFocus
                />
              </Col>
              <Col>
                <Form.Label>Value</Form.Label>
                <Form.Control
                  type='text'
                  required
                  value={formData.value}
                  onChange={(e) => handleChange('value', e.target.value)}
                  placeholder='#000000'
                />
              </Col>
              <Col>
                <Form.Label>Color</Form.Label>
                <Form.Control
                  type='text'
                  required
                  value={formData.color}
                  onChange={(e) => handleChange('color', e.target.value)}
                  placeholder='#000000'
                />
              </Col>
            </Row>
            <Row className='my-3'>
              <Col>
                <Form.Label>Material</Form.Label>
                <Form.Control
                  type='text'
                  value={formData.material}
                  onChange={(e) => handleChange('material', e.target.value)}
                  placeholder='CONCRETE'
                />
              </Col>
              <Col>
                <Form.Label>Access Level</Form.Label>
                <Form.Control
                  type='number'
                  value={formData.access_level}
                  onChange={(e) => handleChange('access_level', e.target.value)}
                  placeholder='0'
                />
              </Col>
            </Row>
            <Row className='my-3'>
              <Col>
                <Form.Check
                  type='checkbox'
                  label='Walkable'
                  checked={formData.walkable}
                  onChange={(e) => handleChange('walkable', e.target.checked)}
                />
              </Col>
              <Col>
                <Form.Check
                  type='checkbox'
                  label='Interactive'
                  checked={formData.interactive}
                  onChange={(e) => handleChange('interactive', e.target.checked)}
                />
              </Col>
              <Col>
                <Form.Check
                  type='checkbox'
                  label='Restricted'
                  checked={formData.restricted}
                  onChange={(e) => handleChange('restricted', e.target.checked)}
                />
              </Col>
            </Row>
            <Button className='pull-right' type='submit'>
              Add Terrain
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    </>
  );
}
