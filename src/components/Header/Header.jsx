import "./Header.css"
import { Link } from 'react-router-dom';
import { useData } from '../../context/DataContext.jsx';

const topNavLinks = [
  'EPAPER',
  'LIVE TV',
  'DAWNNEWS URDU',
  'IMAGES',
  'HERALD',
  'AURORA',
  'CITYFM89',
  'ADVERTISE',
  'EVENTS',
  'SUPPLEMENT',
  'CAREERS',
  'OBITUARIES',
]

const secondaryNavLinks = [
  { label: 'LATEST', path: '/front-page', sectionKey: 'front-page' },
  { label: 'NATIONAL', path: '/national', sectionKey: 'national' },
  { label: 'BACK PAGE', path: '/back-page', sectionKey: 'back-page' },
  { label: 'SPORTS', path: '/sports', sectionKey: 'sport' },
  { label: 'BUSINESS', path: '/business', sectionKey: 'business' },
  { label: 'LETTERS', path: '/letters', sectionKey: 'letters' },
  { label: 'OTHER VOICES', path: '/other-voices', sectionKey: 'other-voices' },
  { label: 'SUNDAY MAGAZINE', path: '/sunday-magazine', sectionKey: 'sunday-magazine' },
  { label: 'ICON', path: '/icon', sectionKey: 'icon' },
  { label: 'YOUNG WORLD', path: '/young-world', sectionKey: 'young-world' },
  { label: 'INTERNATIONAL', path: '/international', sectionKey: 'international' },
  { label: 'EDITORIAL', path: '/editorial', sectionKey: 'editorial' },
  { label: 'BUSINESS FINANCE', path: '/business-finance', sectionKey: 'business-finance' },
]

function twelveYearsAgoPakistan() {
  const now = new Date()
  const pkNow = new Date(
    new Intl.DateTimeFormat('en-CA', {
      timeZone: 'Asia/Karachi',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    }).format(now)
  )
  pkNow.setFullYear(pkNow.getFullYear() - 12)
  return new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Karachi',
    year: 'numeric',
    month: 'long',
    day: '2-digit',
  }).format(pkNow)
}

export default function Header(){
  const { isLoadingArchive, archiveDate, archiveError, sections } = useData();
    
  console.log("Loading:", isLoadingArchive);
  console.log("Error:", archiveError);
  
  const availableLinks = secondaryNavLinks.filter(link => {
    const stories = sections[link.sectionKey];
    return stories && stories.length > 0;
  });
  
  return(
    <div>
      <nav className="navbar">
        <ul className="links">
          {topNavLinks.map((link) => (
            <li key={link}>
              <a href="#">{link}</a>
            </li>
          ))}
        </ul>
        <div className="brand">
          <Link to="/">
            <img src={`${import.meta.env.BASE_URL}images/logo.png`} alt="Dawn logo" height="50" width="225" />
          </Link>
          <p>
            <b>EPAPER </b>
            <span>| {twelveYearsAgoPakistan()}</span>
          </p>
        </div>
        <ul className="otherLinks">
          {isLoadingArchive ? (
            <li><span>Loading sections...</span></li>
          ) : (
            availableLinks.map((link) => (
              <li key={link.label}>
                <Link to={link.path}>{link.label}</Link>
              </li>
            ))
          )}
        </ul>
      </nav>
      <section className="status-bar">
        {isLoadingArchive && <p className="status-message">Loading archive&hellip;</p>}
        {archiveError && <p className="status-message status-error">{archiveError}</p>}
        {!isLoadingArchive && !archiveError && archiveDate && (
          <p className="status-message">
            Showing Dawn archive for <strong>{archiveDate}</strong>
          </p>
        )}
      </section>
    </div>
  )
}