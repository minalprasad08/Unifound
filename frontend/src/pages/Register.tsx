import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types/auth';
import {
  UserPlus,
  Mail,
  Lock,
  User,
  Phone,
  Building,
  Shield,
  Eye,
  EyeOff,
  AlertCircle,
  ArrowRight,
} from 'lucide-react';

export const Register: React.FC = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [department, setDepartment] = useState('');
  const role: UserRole = 'USER';
  const [showPassword, setShowPassword] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password.length < 6) {
      setError('Password must be at least 6 characters long.');
      return;
    }

    setLoading(true);

    try {
      await register({
        email,
        password,
        full_name: fullName,
        phone: phone || undefined,
        department: department || undefined,
        role,
      });
      navigate('/profile');
    } catch (err: any) {
      const detail = err.response?.data?.detail || 'Registration failed. Please verify your details.';
      setError(typeof detail === 'string' ? detail : JSON.stringify(detail));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container animate-fade-in" style={{ maxWidth: '540px', paddingTop: '1.5rem' }}>
      <div className="glass-card" style={{ padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <div
            style={{
              width: '3.5rem',
              height: '3.5rem',
              borderRadius: 'var(--radius-md)',
              background: 'var(--primary-gradient)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 1rem',
              boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)',
            }}
          >
            <UserPlus style={{ width: '1.75rem', height: '1.75rem', color: '#ffffff' }} />
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Create an Account</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.35rem' }}>
            Register to report items, search records, and file verified claims
          </p>
        </div>

        {error && (
          <div className="alert alert-danger">
            <AlertCircle style={{ width: '1.2rem', height: '1.2rem', flexShrink: 0, marginTop: '0.1rem' }} />
            <div>{error}</div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Full Name */}
          <div className="form-group">
            <label className="form-label" htmlFor="register-name">
              Full Legal Name *
            </label>
            <div style={{ position: 'relative' }}>
              <input
                id="register-name"
                type="text"
                required
                className="form-input"
                placeholder="Alex Morgan"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                style={{ paddingLeft: '2.6rem' }}
              />
              <User
                style={{
                  position: 'absolute',
                  left: '0.9rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '1.1rem',
                  height: '1.1rem',
                  color: 'var(--text-muted)',
                }}
              />
            </div>
          </div>

          {/* Email */}
          <div className="form-group">
            <label className="form-label" htmlFor="register-email">
              Campus Email Address *
            </label>
            <div style={{ position: 'relative' }}>
              <input
                id="register-email"
                type="email"
                required
                className="form-input"
                placeholder="alex.m@campus.edu"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ paddingLeft: '2.6rem' }}
              />
              <Mail
                style={{
                  position: 'absolute',
                  left: '0.9rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '1.1rem',
                  height: '1.1rem',
                  color: 'var(--text-muted)',
                }}
              />
            </div>
          </div>

          {/* Two-column layout for Phone & Department */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="register-phone">
                Contact Phone
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  id="register-phone"
                  type="tel"
                  className="form-input"
                  placeholder="+1 555-0123"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  style={{ paddingLeft: '2.6rem' }}
                />
                <Phone
                  style={{
                    position: 'absolute',
                    left: '0.9rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    width: '1.1rem',
                    height: '1.1rem',
                    color: 'var(--text-muted)',
                  }}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="register-dept">
                Dept / Student ID
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  id="register-dept"
                  type="text"
                  className="form-input"
                  placeholder="CS-2026 / Engineering"
                  value={department}
                  onChange={(e) => setDepartment(e.target.value)}
                  style={{ paddingLeft: '2.6rem' }}
                />
                <Building
                  style={{
                    position: 'absolute',
                    left: '0.9rem',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    width: '1.1rem',
                    height: '1.1rem',
                    color: 'var(--text-muted)',
                  }}
                />
              </div>
            </div>
          </div>

          {/* Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="register-password">
              Password (Min. 6 characters) *
            </label>
            <div style={{ position: 'relative' }}>
              <input
                id="register-password"
                type={showPassword ? 'text' : 'password'}
                required
                minLength={6}
                className="form-input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={{ paddingLeft: '2.6rem', paddingRight: '2.6rem' }}
              />
              <Lock
                style={{
                  position: 'absolute',
                  left: '0.9rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '1.1rem',
                  height: '1.1rem',
                  color: 'var(--text-muted)',
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '0.9rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'transparent',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                {showPassword ? <EyeOff style={{ width: '1.1rem', height: '1.1rem' }} /> : <Eye style={{ width: '1.1rem', height: '1.1rem' }} />}
              </button>
            </div>
          </div>

          {/* Role Information Banner */}
          <div
            style={{
              padding: '0.85rem 1rem',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)',
              background: 'rgba(99, 102, 241, 0.08)',
              marginBottom: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
            }}
          >
            <Shield style={{ width: '1.25rem', height: '1.25rem', color: '#818cf8', flexShrink: 0 }} />
            <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              Registration creates a <strong style={{ color: 'var(--text-primary)' }}>Standard Campus Account</strong>. Administrator access is strictly controlled by campus security.
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ width: '100%', marginTop: '1rem' }}
          >
            {loading ? 'Creating Account...' : 'Complete Registration'}
            {!loading && <ArrowRight style={{ width: '1.1rem', height: '1.1rem' }} />}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.75rem', fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ fontWeight: 600 }}>
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
};
