import grabs from '../graphical-abstract.png';

export default function Home() {
  return (
    <div className='App'>
      <header className='App-header'>
        <img
          src={grabs}
          className='App-logo'
          alt='graphical abstract'
          style={{ height: 'auto', flex: 1, width: '100%' }}
        />
        {/* <p>For more information, find the full paper at the Github repository below.</p>
        <a
          className='App-link'
          href='https://github.com/PCiunkiewicz/localized-epidemiological-abs'
          target='_blank'
          rel='noopener noreferrer'
        >
          Github Repo
        </a> */}
      </header>
    </div>
  );
}
