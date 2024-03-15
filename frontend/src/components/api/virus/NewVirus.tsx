import { SyntheticEvent, useState } from 'react';
import { Button, Col, Form, Modal, Row } from 'react-bootstrap';

import { useNavContext } from '../../../contexts/NavContext';
import { Virus } from '../../../types/api';
import VirusDataService, { formDefault } from '../../../utils/api/virus';

export default function NewVirus() {
  const { newVirus, handleNewVirus } = useNavContext();
  const [formData, setFormData] = useState<Virus>(formDefault);

  const handleChange = (name: string, value: string | number | boolean) => {
    setFormData({ ...formData, [name]: value });
  };

  const onSave = (e: SyntheticEvent) => {
    e.preventDefault();
    console.log(formData);
    VirusDataService.post(formData);
    handleClose();
  };

  const handleClose = () => {
    handleNewVirus();
    setFormData(formDefault);
  };

  return (
    <>
      <Modal show={newVirus} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>New Virus</Modal.Title>
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
                  placeholder='virus-name'
                  autoFocus
                />
              </Col>
            </Row>
            <Row className='my-3'>
              <Col>
                <Form.Label>Attack Rate</Form.Label>
                <Form.Control
                  type='number'
                  value={formData.attack_rate}
                  onChange={(e) => handleChange('attack_rate', e.target.value)}
                  placeholder='0'
                />
              </Col>
              <Col>
                <Form.Label>IPR</Form.Label>
                <Form.Control
                  type='number'
                  value={formData.infection_rate}
                  onChange={(e) => handleChange('infection_rate', e.target.value)}
                  placeholder='0'
                />
              </Col>
              <Col>
                <Form.Label>Fatality Rate</Form.Label>
                <Form.Control
                  type='number'
                  value={formData.fatality_rate}
                  onChange={(e) => handleChange('fatality_rate', e.target.value)}
                  placeholder='0'
                />
              </Col>
            </Row>
            <Button className='pull-right' type='submit'>
              Add Virus
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    </>
  );
}
