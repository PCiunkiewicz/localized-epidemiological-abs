import { useContext } from 'react';
import { Container, Form, Nav, Navbar } from 'react-bootstrap';
import { Link } from 'react-router-dom';

import { ThemeContext } from '../../contexts/ThemeContext';

export default function MainNavBar() {
  const { darkMode, toggleDarkMode } = useContext(ThemeContext);
  return (
    <Navbar
      bg={darkMode ? 'dark' : 'light'}
      variant={darkMode ? 'dark' : 'light'}
      sticky='top'
    >
      <Container>
        <Navbar.Brand href='#home'>Navbar</Navbar.Brand>
        <Nav className='me-auto'>
          <Nav.Link href='#home'>Home</Nav.Link>
          <Nav.Link href='#features'>Features</Nav.Link>
          <Nav.Link href='#pricing'>Pricing</Nav.Link>
          <Form>
            <Form.Check
              type='switch'
              id='custom-switch'
              label='Dark Mode'
              onClick={toggleDarkMode}
            />
          </Form>
        </Nav>
      </Container>
    </Navbar>
  );
}
