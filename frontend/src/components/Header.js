import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Header() {
  const location = useLocation();
  
  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <header style={headerStyle}>
      <div style={containerStyle}>
        <h1 style={logoStyle}>UT Jira Helper</h1>
        <nav>
          <ul style={navStyle}>
            <li>
              <Link 
                to="/" 
                style={{
                  ...linkStyle,
                  ...(isActive('/') ? activeLinkStyle : {})
                }}
              >
                Dashboard
              </Link>
            </li>
            <li>
              <Link 
                to="/issues" 
                style={{
                  ...linkStyle,
                  ...(isActive('/issues') ? activeLinkStyle : {})
                }}
              >
                Issues
              </Link>
            </li>
            <li>
              <a href="/settings" style={linkStyle}>Settings</a>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}

// Basic inline styles for demonstration
const headerStyle = {
  backgroundColor: '#0052CC', // Jira blue
  color: 'white',
  padding: '1rem 0',
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
};

const containerStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  maxWidth: '1200px',
  margin: '0 auto',
  padding: '0 1rem'
};

const logoStyle = {
  margin: 0,
  fontSize: '1.5rem'
};

const navStyle = {
  display: 'flex',
  listStyle: 'none',
  margin: 0,
  padding: 0
};

const linkStyle = {
  color: 'white',
  textDecoration: 'none',
  padding: '0 1rem',
  fontWeight: 500
};

const activeLinkStyle = {
  backgroundColor: 'rgba(255, 255, 255, 0.2)',
  borderRadius: '4px'
};

export default Header;