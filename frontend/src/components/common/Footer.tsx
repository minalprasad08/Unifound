import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { authApi } from '../../services/api';
import { HealthStatus } from '../../types/auth';
import { Compass } from 'lucide-react';

export const Footer: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    let isMounted = true;
    const check = async () => {
      try {
        const data = await authApi.checkHealth();
        if (isMounted) setHealth(data);
      } catch (err) {
        if (isMounted) {
          setHealth({
            status: 'offline',
            service: 'Backend Disconnected',
            version: '1.0.0',
            environment: 'development',
            database: 'unreachable',
            timestamp: new Date().toISOString(),
          });
        }
      }
    };
    check();
    const interval = setInterval(check, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <footer
      style={{
        borderTop: '1px solid var(--border-subtle)',
        background: 'var(--bg-secondary)',
        padding: '3rem 0 2rem',
        marginTop: 'auto',
      }}
    >
      <div className="container">
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '2.5rem',
            marginBottom: '2.5rem',
          }}
        >
          {/* Col 1: System Info */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '1rem' }}>
              <div
                style={{
                  width: '2rem',
                  height: '2rem',
                  borderRadius: 'var(--radius-sm)',
                  background: 'var(--primary-gradient)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Compass style={{ width: '1.2rem', height: '1.2rem', color: '#ffffff' }} />
              </div>
              <span style={{ fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-primary)' }}>UniFound</span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '1rem' }}>
              AI-Powered Campus Lost & Found Management System featuring intelligent multimodal matching, Model Context Protocol (MCP) server, and Agentic AI orchestrator.
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.4rem',
                  padding: '0.25rem 0.65rem',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  background: health?.status === 'healthy' ? 'var(--success-bg)' : 'var(--danger-bg)',
                  color: health?.status === 'healthy' ? 'var(--success)' : 'var(--danger)',
                  border: `1px solid ${health?.status === 'healthy' ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
                }}
              >
                <span
                  style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: health?.status === 'healthy' ? 'var(--success)' : 'var(--danger)',
                  }}
                  className="pulse-indicator"
                />
                API: {health?.status === 'healthy' ? 'Healthy & Connected' : 'Offline / Standby'}
              </span>
            </div>
          </div>

          {/* Col 2: Quick Links */}
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-primary)' }}>
              Quick Links
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.85rem', padding: 0, margin: 0 }}>
              <li>
                <Link to="/" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
                  Home
                </Link>
              </li>
              <li>
                <Link to="/search" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
                  Browse &amp; Search Items
                </Link>
              </li>
              <li>
                <Link to="/report-lost" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
                  Report Lost Item
                </Link>
              </li>
              <li>
                <Link to="/report-found" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
                  Report Found Item
                </Link>
              </li>
              <li>
                <Link to="/my-claims" style={{ color: 'var(--text-secondary)', textDecoration: 'none' }}>
                  Track My Claims
                </Link>
              </li>
            </ul>
          </div>

          {/* Col 3: Campus Support */}
          <div>
            <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '1rem', color: 'var(--text-primary)' }}>
              Campus Support
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.65rem', fontSize: '0.85rem', padding: 0, margin: 0 }}>
              <li style={{ color: 'var(--text-secondary)' }}>
                Campus Safety &amp; Security Office
              </li>
              <li style={{ color: 'var(--text-secondary)' }}>
                Claim Verification Guidelines
              </li>
              <li style={{ color: 'var(--text-secondary)' }}>
                Property Retrieval Hours (8 AM - 6 PM)
              </li>
              <li style={{ color: 'var(--text-secondary)' }}>
                Official Campus Lost &amp; Found Portal
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div
          style={{
            borderTop: '1px solid var(--border-subtle)',
            paddingTop: '1.5rem',
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '1rem',
            fontSize: '0.8rem',
            color: 'var(--text-muted)',
          }}
        >
          <div>
            &copy; {new Date().getFullYear()} UniFound System. Production-ready implementation.
          </div>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <span>Privacy Policy</span>
            <span>Terms of Service</span>
            <span>Security Audits</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
