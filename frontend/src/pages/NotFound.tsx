import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, Home } from 'lucide-react';

export const NotFound: React.FC = () => {
  return (
    <div className="container" style={{ textAlign: 'center', paddingTop: '4rem', maxWidth: '540px' }}>
      <div className="glass-card" style={{ padding: '3rem 2rem' }}>
        <div
          style={{
            width: '4rem',
            height: '4rem',
            borderRadius: '50%',
            background: 'rgba(99, 102, 241, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.5rem',
            border: '1px solid rgba(99, 102, 241, 0.3)',
          }}
        >
          <Compass style={{ width: '2rem', height: '2rem', color: '#818cf8' }} />
        </div>
        <h1 style={{ fontSize: '3.5rem', fontWeight: 800, marginBottom: '0.5rem', color: '#818cf8' }}>404</h1>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '0.75rem' }}>Page Not Found</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '2rem' }}>
          The page you are looking for does not exist or has been moved to another coordinate.
        </p>
        <Link to="/" className="btn btn-primary" style={{ display: 'inline-flex', margin: '0 auto' }}>
          <Home style={{ width: '1.1rem', height: '1.1rem' }} />
          Return to Home
        </Link>
      </div>
    </div>
  );
};
