import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  Compass,
  Sun,
  Moon,
  User as UserIcon,
  LogOut,
  Shield,
  Menu,
  X,
  Package,
  Search,
  FileCheck,
  ShieldAlert,
  LayoutDashboard,
  Bell,
} from 'lucide-react';
import { NotificationsMenu } from './NotificationsMenu';

export const Navbar: React.FC = () => {
  const { user, isAuthenticated, isAdmin, logout, theme, toggleTheme } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  React.useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  React.useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth > 768) {
        setMobileMenuOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const handleLogout = () => {
    logout();
    setUserDropdownOpen(false);
    navigate('/');
  };

  const isActive = (path: string) => {
    if (path === '/' && location.pathname !== '/') return false;
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const getLinkStyle = (path: string, colorOverride?: string) => {
    const active = isActive(path);
    return {
      fontSize: '0.92rem',
      fontWeight: active ? 700 : 500,
      color: active ? (colorOverride || 'var(--primary)') : 'var(--text-secondary)',
      textDecoration: 'none',
      display: 'flex',
      alignItems: 'center',
      gap: '0.35rem',
      paddingBottom: '0.2rem',
      borderBottom: active ? `2px solid ${colorOverride || 'var(--primary)'}` : '2px solid transparent',
      transition: 'all 0.15s ease',
    };
  };

  return (
    <header
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 50,
        background: 'rgba(9, 13, 22, 0.85)',
        backdropFilter: 'blur(16px)',
        WebkitBackdropFilter: 'blur(16px)',
        borderBottom: '1px solid var(--border-subtle)',
      }}
    >
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '4.25rem' }}>
        {/* Brand Logo */}
        <Link to={isAuthenticated ? "/dashboard" : "/"} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', textDecoration: 'none' }}>
          <div
            style={{
              width: '2.5rem',
              height: '2.5rem',
              borderRadius: 'var(--radius-md)',
              background: 'var(--primary-gradient)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 15px rgba(99, 102, 241, 0.4)',
            }}
          >
            <Compass style={{ width: '1.4rem', height: '1.4rem', color: '#ffffff' }} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
                UniFound
              </span>
              <span
                style={{
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  padding: '0.15rem 0.4rem',
                  borderRadius: 'var(--radius-full)',
                  background: 'rgba(99, 102, 241, 0.15)',
                  color: '#818cf8',
                  border: '1px solid rgba(99, 102, 241, 0.3)',
                }}
              >
                AI &bull; MCP
              </span>
            </div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Campus Lost &amp; Found</span>
          </div>
        </Link>

        {/* Desktop Nav Links */}
        <nav className="desktop-nav">
          {isAuthenticated ? (
            <Link to="/dashboard" style={getLinkStyle('/dashboard')}>
              <LayoutDashboard style={{ width: '0.95rem', height: '0.95rem' }} />
              Dashboard
            </Link>
          ) : (
            <Link to="/" style={getLinkStyle('/')}>
              Overview
            </Link>
          )}

          <Link to="/search" style={getLinkStyle('/search')}>
            <Search style={{ width: '0.95rem', height: '0.95rem' }} />
            Search
          </Link>

          <Link to="/report-lost" style={getLinkStyle('/report-lost')}>
            <span style={{ color: 'var(--danger)' }}>&bull;</span> Report Lost
          </Link>

          <Link to="/report-found" style={getLinkStyle('/report-found')}>
            <span style={{ color: 'var(--success)' }}>&bull;</span> Report Found
          </Link>

          {isAuthenticated && (
            <>
              <Link to="/my-reports" style={getLinkStyle('/my-reports')}>
                <Package style={{ width: '0.95rem', height: '0.95rem' }} />
                My Reports
              </Link>

              <Link to="/my-claims" style={getLinkStyle('/my-claims')}>
                <FileCheck style={{ width: '0.95rem', height: '0.95rem' }} />
                My Claims
              </Link>
            </>
          )}

          {isAdmin && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', paddingLeft: '0.5rem', borderLeft: '1px solid var(--border-subtle)' }}>
              <Link to="/admin/claims" style={getLinkStyle('/admin/claims', 'var(--danger)')}>
                <ShieldAlert style={{ width: '0.95rem', height: '0.95rem' }} />
                Claims Queue
              </Link>
              <Link to="/admin" style={getLinkStyle('/admin', 'var(--danger)')}>
                <Shield style={{ width: '0.95rem', height: '0.95rem' }} />
                Admin Portal
              </Link>
            </div>
          )}
        </nav>

        {/* Right Action Items */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          {/* Notifications Dropdown (Authenticated only) */}
          {isAuthenticated && <NotificationsMenu />}

          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="btn btn-ghost btn-sm"
            style={{ padding: '0.45rem', color: 'var(--text-secondary)' }}
            title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {theme === 'dark' ? (
              <Sun style={{ width: '1.15rem', height: '1.15rem', color: '#f59e0b' }} />
            ) : (
              <Moon style={{ width: '1.15rem', height: '1.15rem', color: '#6366f1' }} />
            )}
          </button>

          {/* User Profile / Auth State */}
          {isAuthenticated && user ? (
            <div style={{ position: 'relative' }}>
              <button
                onClick={() => setUserDropdownOpen(!userDropdownOpen)}
                className="btn btn-secondary btn-sm"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.4rem 0.75rem',
                  borderColor: isAdmin ? 'rgba(244, 63, 94, 0.4)' : undefined,
                }}
              >
                <div
                  style={{
                    width: '1.5rem',
                    height: '1.5rem',
                    borderRadius: '50%',
                    background: isAdmin ? 'var(--danger-bg)' : 'var(--primary-gradient)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    color: '#ffffff',
                  }}
                >
                  {user.full_name?.charAt(0).toUpperCase() || 'U'}
                </div>
                <span style={{ maxWidth: '110px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {user.full_name?.split(' ')[0]}
                </span>
              </button>

              {userDropdownOpen && (
                <div
                  className="glass-card animate-fade-in"
                  style={{
                    position: 'absolute',
                    top: 'calc(100% + 0.5rem)',
                    right: 0,
                    width: '240px',
                    padding: '0.75rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '0.5rem',
                    zIndex: 60,
                  }}
                >
                  <div style={{ padding: '0.5rem 0.75rem', borderBottom: '1px solid var(--border-subtle)' }}>
                    <p style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>{user.full_name}</p>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', wordBreak: 'break-all' }}>{user.email}</p>
                    {user.department && (
                      <p style={{ fontSize: '0.72rem', color: 'var(--accent-cyan)', marginTop: '0.2rem' }}>
                        Dept: {user.department}
                      </p>
                    )}
                  </div>

                  <Link
                    to="/dashboard"
                    onClick={() => setUserDropdownOpen(false)}
                    className="btn btn-secondary btn-sm"
                    style={{ justifyContent: 'flex-start' }}
                  >
                    <LayoutDashboard style={{ width: '1rem', height: '1rem' }} />
                    Dashboard
                  </Link>

                  <Link
                    to="/my-reports"
                    onClick={() => setUserDropdownOpen(false)}
                    className="btn btn-secondary btn-sm"
                    style={{ justifyContent: 'flex-start' }}
                  >
                    <Package style={{ width: '1rem', height: '1rem' }} />
                    My Reports
                  </Link>

                  <Link
                    to="/my-claims"
                    onClick={() => setUserDropdownOpen(false)}
                    className="btn btn-secondary btn-sm"
                    style={{ justifyContent: 'flex-start' }}
                  >
                    <FileCheck style={{ width: '1rem', height: '1rem' }} />
                    My Claims
                  </Link>

                  <Link
                    to="/notifications"
                    onClick={() => setUserDropdownOpen(false)}
                    className="btn btn-secondary btn-sm"
                    style={{ justifyContent: 'flex-start' }}
                  >
                    <Bell style={{ width: '1rem', height: '1rem' }} />
                    Notifications Hub
                  </Link>

                  <Link
                    to="/profile"
                    onClick={() => setUserDropdownOpen(false)}
                    className="btn btn-secondary btn-sm"
                    style={{ justifyContent: 'flex-start' }}
                  >
                    <UserIcon style={{ width: '1rem', height: '1rem' }} />
                    My Profile
                  </Link>

                  {isAdmin && (
                    <>
                      <hr style={{ borderColor: 'var(--border-subtle)', margin: '0.25rem 0' }} />
                      <Link
                        to="/admin/claims"
                        onClick={() => setUserDropdownOpen(false)}
                        className="btn btn-secondary btn-sm"
                        style={{ justifyContent: 'flex-start', color: 'var(--danger)' }}
                      >
                        <ShieldAlert style={{ width: '1rem', height: '1rem' }} />
                        Claims Queue
                      </Link>
                      <Link
                        to="/admin"
                        onClick={() => setUserDropdownOpen(false)}
                        className="btn btn-secondary btn-sm"
                        style={{ justifyContent: 'flex-start', color: 'var(--danger)' }}
                      >
                        <Shield style={{ width: '1rem', height: '1rem' }} />
                        Admin Portal
                      </Link>
                    </>
                  )}

                  <hr style={{ borderColor: 'var(--border-subtle)', margin: '0.25rem 0' }} />

                  <button
                    onClick={handleLogout}
                    className="btn btn-danger btn-sm"
                    style={{ justifyContent: 'flex-start' }}
                  >
                    <LogOut style={{ width: '1rem', height: '1rem' }} />
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <Link to="/login" className="btn btn-outline btn-sm">
                Sign In
              </Link>
              <Link to="/register" className="btn btn-primary btn-sm">
                Get Started
              </Link>
            </div>
          )}

          {/* Mobile Menu Toggle Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="btn btn-ghost btn-sm mobile-menu-btn"
            style={{ padding: '0.45rem' }}
          >
            {mobileMenuOpen ? <X style={{ width: '1.25rem', height: '1.25rem' }} /> : <Menu style={{ width: '1.25rem', height: '1.25rem' }} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div
          className="mobile-drawer animate-fade-in"
          style={{
            position: 'fixed',
            top: '4.25rem',
            left: 0,
            right: 0,
            background: 'var(--bg-secondary)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            borderBottom: '1px solid var(--border-subtle)',
            boxShadow: '0 12px 32px rgba(0, 0, 0, 0.4)',
            padding: '1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            zIndex: 49,
            maxHeight: 'calc(100vh - 4.25rem)',
            overflowY: 'auto',
          }}
        >
          {isAuthenticated ? (
            <Link
              to="/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              style={{ fontWeight: 600, color: 'var(--primary)' }}
            >
              Dashboard
            </Link>
          ) : (
            <Link
              to="/"
              onClick={() => setMobileMenuOpen(false)}
              style={{ fontWeight: 600, color: 'var(--text-primary)' }}
            >
              Overview
            </Link>
          )}

          <Link
            to="/search"
            onClick={() => setMobileMenuOpen(false)}
            style={{ color: 'var(--text-primary)', fontWeight: 500 }}
          >
            Search Items
          </Link>
          <Link
            to="/report-lost"
            onClick={() => setMobileMenuOpen(false)}
            style={{ color: 'var(--danger)', fontWeight: 500 }}
          >
            Report Lost Item
          </Link>
          <Link
            to="/report-found"
            onClick={() => setMobileMenuOpen(false)}
            style={{ color: 'var(--success)', fontWeight: 500 }}
          >
            Report Found Item
          </Link>

          {isAuthenticated && (
            <>
              <hr style={{ borderColor: 'var(--border-subtle)', margin: '0.25rem 0' }} />
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                My Activity
              </div>
              <Link
                to="/my-reports"
                onClick={() => setMobileMenuOpen(false)}
                style={{ color: 'var(--text-primary)', fontWeight: 500 }}
              >
                My Reports
              </Link>
              <Link
                to="/my-claims"
                onClick={() => setMobileMenuOpen(false)}
                style={{ color: 'var(--text-primary)', fontWeight: 500 }}
              >
                My Ownership Claims
              </Link>
              <Link
                to="/notifications"
                onClick={() => setMobileMenuOpen(false)}
                style={{ color: 'var(--text-primary)', fontWeight: 500 }}
              >
                Notifications Center
              </Link>
              <Link
                to="/profile"
                onClick={() => setMobileMenuOpen(false)}
                style={{ color: 'var(--text-primary)', fontWeight: 500 }}
              >
                Account Profile
              </Link>

              {isAdmin && (
                <>
                  <hr style={{ borderColor: 'var(--border-subtle)', margin: '0.25rem 0' }} />
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--danger)', textTransform: 'uppercase' }}>
                    Staff Administration
                  </div>
                  <Link
                    to="/admin/claims"
                    onClick={() => setMobileMenuOpen(false)}
                    style={{ color: 'var(--danger)', fontWeight: 600 }}
                  >
                    Claims Review Queue
                  </Link>
                  <Link
                    to="/admin"
                    onClick={() => setMobileMenuOpen(false)}
                    style={{ color: 'var(--danger)', fontWeight: 600 }}
                  >
                    Admin Console
                  </Link>
                </>
              )}

              <hr style={{ borderColor: 'var(--border-subtle)', margin: '0.25rem 0' }} />
              <button onClick={handleLogout} className="btn btn-danger btn-sm">
                Sign Out
              </button>
            </>
          )}
        </div>
      )}
    </header>
  );
};
