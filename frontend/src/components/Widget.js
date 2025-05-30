import React from 'react';

function Widget({ title, children, className }) {
  return (
    <div style={widgetStyle} className={className}>
      <div style={widgetHeaderStyle}>
        <h3 style={widgetTitleStyle}>{title}</h3>
      </div>
      <div style={widgetContentStyle}>
        {children}
      </div>
    </div>
  );
}

// Widget base styles
const widgetStyle = {
  backgroundColor: 'white',
  borderRadius: '8px',
  boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  border: '1px solid #e0e0e0',
  overflow: 'hidden'
};

const widgetHeaderStyle = {
  padding: '1rem 1rem 0.5rem 1rem',
  borderBottom: '1px solid #f0f0f0'
};

const widgetTitleStyle = {
  margin: 0,
  fontSize: '1.1rem',
  fontWeight: '600',
  color: '#333'
};

const widgetContentStyle = {
  padding: '1rem'
};

export default Widget;