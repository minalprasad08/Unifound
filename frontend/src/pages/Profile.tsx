import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import {
  User as UserIcon,
  Mail,
  Phone,
  Building,
  Calendar,
  CheckCircle,
  AlertCircle,
  Save,
  Package,
  FileCheck,
  Key,
} from 'lucide-react';

export const Profile: React.FC = () => {
  const { user, isAdmin, updateProfile } = useAuth();

  const [fullName, setFullName] = useState(user?.full_name || '');
  const [phone, setPhone] = useState(user?.phone || '');
  const [department, setDepartment] = useState(user?.department || '');

  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  if (!user) return null;

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMsg(null);
    setErrorMsg(null);
    setLoading(true);

    try {
      await updateProfile({
        full_name: fullName,
        phone: phone || undefined,
        department: department || undefined,
      });
      setSuccessMsg('Account profile successfully updated.');
    } catch (err: any) {
      const detail = err.response?.data?.detail || 'Failed to update profile.';
      setErrorMsg(typeof detail === 'string' ? detail : JSON.stringify(detail));
    } finally {
      setLoading(false);
    }
  };

  const initials = user.full_name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .substring(0, 2)
    .toUpperCase();

  const joinedDate = new Date(user.created_at).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  return (
    <div className="container animate-fade-in" style={{ maxWidth: '900px', paddingTop: '1rem' }}>
      {/* Top Profile Banner Header */}
      <div
        className="glass-card"
        style={{
          padding: '2rem',
          marginBottom: '2rem',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1.5rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div
            style={{
              width: '4.5rem',
              height: '4.5rem',
              borderRadius: '50%',
              background: isAdmin ? 'var(--danger-bg)' : 'var(--primary-gradient)',
              border: `2px solid ${isAdmin ? 'var(--danger)' : 'var(--primary)'}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              fontSize: '1.5rem',
              fontWeight: 800,
              fontFamily: 'var(--font-heading)',
              boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)',
            }}
          >
            {initials}
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>{user.full_name}</h1>
              <span
                className={`badge ${isAdmin ? 'badge-danger' : 'badge-primary'}`}
                style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem' }}
              >
                {isAdmin ? 'CAMPUS ADMINISTRATOR' : 'CAMPUS COMMUNITY MEMBER'}
              </span>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.2rem' }}>
              {user.email}
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <Calendar style={{ width: '0.9rem', height: '0.9rem' }} />
                Joined {joinedDate}
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--success)' }}>
                <CheckCircle style={{ width: '0.9rem', height: '0.9rem' }} />
                Active Account
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Edit Profile Form + Account Overview */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem' }}>
        {/* Col 1: Update Profile Details */}
        <div className="glass-card" style={{ padding: '2rem' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1.25rem' }}>
            Account Profile Details
          </h2>

          {successMsg && (
            <div className="alert alert-success">
              <CheckCircle style={{ width: '1.2rem', height: '1.2rem', flexShrink: 0 }} />
              <div>{successMsg}</div>
            </div>
          )}

          {errorMsg && (
            <div className="alert alert-danger">
              <AlertCircle style={{ width: '1.2rem', height: '1.2rem', flexShrink: 0 }} />
              <div>{errorMsg}</div>
            </div>
          )}

          <form onSubmit={handleUpdate}>
            <div className="form-group">
              <label className="form-label" htmlFor="prof-name">
                Full Legal Name
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  id="prof-name"
                  type="text"
                  required
                  className="form-input"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  style={{ paddingLeft: '2.6rem' }}
                />
                <UserIcon
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
              <label className="form-label" htmlFor="prof-email">
                Campus Email (Read-only)
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  id="prof-email"
                  type="email"
                  disabled
                  className="form-input"
                  value={user.email}
                  style={{ paddingLeft: '2.6rem', opacity: 0.7, cursor: 'not-allowed' }}
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

            <div className="form-group">
              <label className="form-label" htmlFor="prof-phone">
                Contact Phone
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  id="prof-phone"
                  type="tel"
                  className="form-input"
                  placeholder="+1 555-0199"
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
              <label className="form-label" htmlFor="prof-dept">
                Department / Student ID
              </label>
              <div style={{ position: 'relative' }}>
                <input
                  id="prof-dept"
                  type="text"
                  className="form-input"
                  placeholder="CS-2026 / Faculty"
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

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '0.5rem' }}
            >
              <Save style={{ width: '1rem', height: '1rem' }} />
              {loading ? 'Saving Changes...' : 'Save Profile Changes'}
            </button>
          </form>
        </div>

        {/* Col 2: System Roles & Permissions */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Security & Access Box */}
          <div className="glass-card" style={{ padding: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '1rem' }}>
              <Key style={{ width: '1.25rem', height: '1.25rem', color: '#818cf8' }} />
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Security &amp; Permissions</h2>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.88rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-subtle)' }}>
                <span style={{ color: 'var(--text-secondary)' }}>System Role</span>
                <strong style={{ color: isAdmin ? 'var(--danger)' : 'var(--primary)' }}>{user.role}</strong>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-subtle)' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Authentication</span>
                <span style={{ color: 'var(--success)' }}>JWT Signed (HS256)</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '0.5rem', borderBottom: '1px solid var(--border-subtle)' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Item Reporting</span>
                <span style={{ color: 'var(--text-primary)' }}>Authorized (All Users)</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Claim Verification</span>
                <span style={{ color: isAdmin ? 'var(--success)' : 'var(--text-muted)' }}>
                  {isAdmin ? 'Admin Approval Granted' : 'Admin Approval Required'}
                </span>
              </div>
            </div>
          </div>

          {/* Activity Placeholder Summary */}
          <div className="glass-card" style={{ padding: '2rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem' }}>
              Lost &amp; Found Activity
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div
                style={{
                  background: 'var(--bg-tertiary)',
                  padding: '1rem',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center',
                }}
              >
                <Package style={{ width: '1.4rem', height: '1.4rem', color: '#818cf8', margin: '0 auto 0.4rem' }} />
                <div style={{ fontSize: '1.4rem', fontWeight: 800 }}>0</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Reported Items</div>
              </div>

              <div
                style={{
                  background: 'var(--bg-tertiary)',
                  padding: '1rem',
                  borderRadius: 'var(--radius-md)',
                  textAlign: 'center',
                }}
              >
                <FileCheck style={{ width: '1.4rem', height: '1.4rem', color: 'var(--success)', margin: '0 auto 0.4rem' }} />
                <div style={{ fontSize: '1.4rem', fontWeight: 800 }}>0</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Active Claims</div>
              </div>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '1rem', textAlign: 'center' }}>
              Item reporting and claims tracking will unlock in Phase 2 &amp; 3.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
