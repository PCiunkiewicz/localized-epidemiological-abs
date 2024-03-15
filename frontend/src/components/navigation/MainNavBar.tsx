import { Container, Nav, Navbar, NavDropdown } from 'react-bootstrap';

import { useNavContext } from '../../contexts/NavContext';
import NewSimulation from '../api/simulation/NewSimulation';
import NewVirus from '../api/virus/NewVirus';

export default function MainNavBar() {
  const { handleNewSim, handleNewVirus } = useNavContext();
  return (
    <>
      <Navbar sticky='top' bg='light' variant='light'>
        <Container>
          <Navbar.Brand href='home'>LocABS</Navbar.Brand>
          <Nav className='me-auto'>
            <NavDropdown title='File' id='basic-nav-dropdown'>
              <NavDropdown.Item onClick={handleNewSim}>New Simulation</NavDropdown.Item>
              <NavDropdown.Item onClick={handleNewVirus}>New Virus</NavDropdown.Item>
              <NavDropdown.Divider />
              <NavDropdown.Item href='http://localhost:8080/browser/' target='_blank'>
                DB Admin
              </NavDropdown.Item>
            </NavDropdown>
            <Nav.Link>Scenarios</Nav.Link>
            <Nav.Link>Runs</Nav.Link>
            <Nav.Link>Statistics</Nav.Link>
            <NavDropdown title='Explore' id='basic-nav-dropdown'>
              <NavDropdown.Item href='terrains'>Terrains</NavDropdown.Item>
              <NavDropdown.Item href='simulations'>Simulations</NavDropdown.Item>
              <NavDropdown.Item href='viruses'>Viruses</NavDropdown.Item>
              <NavDropdown.Item>Scenarios</NavDropdown.Item>
              <NavDropdown.Item>Runs</NavDropdown.Item>
            </NavDropdown>
          </Nav>
          <Nav>
            <Nav.Link href='https://doi.org/10.1016/j.compbiomed.2022.105396' target='_blank'>
              Literature
            </Nav.Link>
            <Nav.Link href='https://github.com/PCiunkiewicz/localized-epidemiological-abs' target='_blank'>
              GitHub
            </Nav.Link>
          </Nav>
        </Container>
      </Navbar>
      <NewSimulation />
      <NewVirus />
    </>
  );
}
