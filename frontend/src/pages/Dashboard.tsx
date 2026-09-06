import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { itemApi, claimApi, notificationApi } from '../services/api';
import { Item, Claim, Notification } from '../types/auth';
import {
  Package,
  FileCheck,
  Search,
  PlusCircle,
  ExternalLink,
  Bell,
  ArrowRight,
  AlertCircle,
  GraduationCap,
  Sparkles,
} from 'lucide-react';

export const Dashboard: React.FC = () => {
  const { user, isAdmin } = useAuth();

  const [reports, setReports] = useState<Item[]>([]);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        const [reportsData, claimsData, notifsData] = await Promise.all([
          itemApi.getMyReports(),
          claimApi.getMyClaims(),
          notificationApi.getMyNotifications(),
        ]);

        setReports(reportsData);
        setClaims(claimsData);
        setNotifications(notifsData);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load your dashboard data.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Compute actual metrics from user's live data
  const totalLost = reports.filter((r) => r.item_type === 'LOST').length;
  const totalFound = reports.filter((r) => r.item_type === 'FOUND').length;
  const openReports = reports.filter((r) => r.status === 'OPEN').length;
  const activeClaims = claims.filter((c) => c.status === 'PENDING').length;
  const unreadCount = notifications.filter((n) => !n.is_read).length;
  const matchAlerts = notifications.filter((n) => n.type === 'MATCH_ALERT');

  const recentReports = reports.slice(0, 4);
  const recentNotifications = notifications.slice(0, 4);


  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'OPEN':
        return <span className="badge badge-success">OPEN</span>;
      case 'CLAIM_PENDING':
        return <span className="badge badge-warning">CLAIM PENDING</span>;
      case 'CLAIMED':
        return <span className="badge badge-info">CLAIMED</span>;
      case 'RESOLVED':
        return <span className="badge badge-primary">RESOLVED</span>;
      case 'CLOSED':
        return <span className="badge badge-danger">CLOSED</span>;
      default:
        return <span className="badge">{status}</span>;
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ paddingTop: '5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <div className="spinner" style={{ margin: '0 auto 1rem' }} />
        Loading your personal dashboard...
      </div>
    );
  }

  return (
    <div className="container animate-fade-in" style={{ paddingTop: '2rem', maxWidth: '1200px', paddingBottom: '3rem' }}>
      {/* Welcome Banner */}
      <div
        className="glass-card"
        style={{
          padding: '2rem 2.5rem',
          marginBottom: '2rem',
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.08))',
          borderColor: 'rgba(99, 102, 241, 0.25)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1.5rem',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.5rem' }}>
            <span className="badge badge-primary">CAMPUS PORTAL</span>
            {isAdmin && <span className="badge badge-danger">ADMINISTRATOR</span>}
          </div>
          <h1 style={{ fontSize: '2.1rem', fontWeight: 800 }}>Welcome back, {user?.full_name}!</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.35rem', fontSize: '0.95rem' }}>
            Manage your reported possessions, track pending claims, and search the campus lost &amp; found registry.
          </p>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <GraduationCap style={{ width: '1rem', height: '1rem', color: 'var(--primary)' }} />
            <span>{user?.department ? `Dept: ${user.department}` : user?.email}</span>
          </div>
          {user?.student_id && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)' }}>
              <span>Student ID: {user.student_id}</span>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div
          className="glass-card animate-fade-in"
          style={{
            padding: '1rem',
            marginBottom: '1.5rem',
            background: 'var(--danger-bg)',
            borderColor: 'var(--danger)',
            color: 'var(--danger)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem',
          }}
        >
          <AlertCircle style={{ width: '1.25rem', height: '1.25rem' }} />
          <span>{error}</span>
        </div>
      )}

      {/* Metrics Row */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1.25rem',
          marginBottom: '2rem',
        }}
      >
        <div className="glass-card" style={{ padding: '1.5rem', borderLeft: '4px solid var(--danger)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>MY LOST REPORTS</span>
            <span style={{ color: 'var(--danger)' }}>&bull;</span>
          </div>
          <div style={{ fontSize: '2.25rem', fontWeight: 800, marginTop: '0.5rem' }}>{totalLost}</div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Personal items reported as lost
          </p>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem', borderLeft: '4px solid var(--success)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>MY FOUND REPORTS</span>
            <span style={{ color: 'var(--success)' }}>&bull;</span>
          </div>
          <div style={{ fontSize: '2.25rem', fontWeight: 800, marginTop: '0.5rem' }}>{totalFound}</div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Items you turned in or reported found
          </p>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem', borderLeft: '4px solid var(--primary)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>OPEN REPORTS</span>
            <Package style={{ width: '1rem', height: '1rem', color: 'var(--primary)' }} />
          </div>
          <div style={{ fontSize: '2.25rem', fontWeight: 800, marginTop: '0.5rem' }}>{openReports}</div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Active listings seeking resolution
          </p>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem', borderLeft: '4px solid #f59e0b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>ACTIVE CLAIMS</span>
            <FileCheck style={{ width: '1rem', height: '1rem', color: '#f59e0b' }} />
          </div>
          <div style={{ fontSize: '2.25rem', fontWeight: 800, marginTop: '0.5rem' }}>{activeClaims}</div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Pending verification by campus staff
          </p>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem', borderLeft: '4px solid #a855f7' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>UNREAD NOTICES</span>
            <Bell style={{ width: '1rem', height: '1rem', color: '#a855f7' }} />
          </div>
          <div style={{ fontSize: '2.25rem', fontWeight: 800, marginTop: '0.5rem', color: unreadCount > 0 ? '#a855f7' : 'inherit' }}>
            {unreadCount}
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {matchAlerts.length} match alert{matchAlerts.length === 1 ? '' : 's'}
          </p>
        </div>
      </div>

      {/* Quick Action Cards */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem' }}>Quick Actions</h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '1rem',
          }}
        >
          <Link
            to="/report-lost"
            className="glass-card"
            style={{
              padding: '1.25rem',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              textDecoration: 'none',
              transition: 'transform 0.2s ease, border-color 0.2s ease',
            }}
          >
            <div
              style={{
                width: '2.75rem',
                height: '2.75rem',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(244, 63, 94, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--danger)',
              }}
            >
              <PlusCircle style={{ width: '1.35rem', height: '1.35rem' }} />
            </div>
            <div>
              <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.98rem' }}>Report Lost Item</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>Lost something on campus?</div>
            </div>
          </Link>

          <Link
            to="/report-found"
            className="glass-card"
            style={{
              padding: '1.25rem',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              textDecoration: 'none',
            }}
          >
            <div
              style={{
                width: '2.75rem',
                height: '2.75rem',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(16, 185, 129, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--success)',
              }}
            >
              <Package style={{ width: '1.35rem', height: '1.35rem' }} />
            </div>
            <div>
              <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.98rem' }}>Report Found Item</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>Turn in discovered item</div>
            </div>
          </Link>

          <Link
            to="/search"
            className="glass-card"
            style={{
              padding: '1.25rem',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              textDecoration: 'none',
            }}
          >
            <div
              style={{
                width: '2.75rem',
                height: '2.75rem',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(99, 102, 241, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--primary)',
              }}
            >
              <Search style={{ width: '1.35rem', height: '1.35rem' }} />
            </div>
            <div>
              <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.98rem' }}>Search Database</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>Filter by keyword &amp; location</div>
            </div>
          </Link>

          <Link
            to="/my-claims"
            className="glass-card"
            style={{
              padding: '1.25rem',
              display: 'flex',
              alignItems: 'center',
              gap: '1rem',
              textDecoration: 'none',
            }}
          >
            <div
              style={{
                width: '2.75rem',
                height: '2.75rem',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(245, 158, 11, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#f59e0b',
              }}
            >
              <FileCheck style={{ width: '1.35rem', height: '1.35rem' }} />
            </div>
            <div>
              <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.98rem' }}>My Claims</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>Track claim verification status</div>
            </div>
          </Link>
        </div>
      </div>

      {/* Two Column Layout: Recent Reports & Recent Notifications */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '2rem' }}>
        {/* Recent Reports */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>My Recent Reports</h2>
            <Link to="/my-reports" style={{ fontSize: '0.85rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '0.25rem', textDecoration: 'none' }}>
              View All <ArrowRight style={{ width: '0.85rem', height: '0.85rem' }} />
            </Link>
          </div>

          {recentReports.length === 0 ? (
            <div className="glass-card" style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <Package style={{ width: '2rem', height: '2rem', color: 'var(--text-muted)', margin: '0 auto 0.5rem' }} />
              <div style={{ fontWeight: 600 }}>No reports filed yet</div>
              <p style={{ fontSize: '0.82rem', marginTop: '0.25rem', color: 'var(--text-muted)' }}>
                Items you report as lost or found will appear here.
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {recentReports.map((item) => (
                <div
                  key={item.id}
                  className="glass-card"
                  style={{
                    padding: '1rem 1.25rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: '1rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', minWidth: 0 }}>
                    <div
                      style={{
                        width: '2.5rem',
                        height: '2.5rem',
                        borderRadius: 'var(--radius-sm)',
                        background: item.item_type === 'LOST' ? 'rgba(244, 63, 94, 0.12)' : 'rgba(16, 185, 129, 0.12)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: item.item_type === 'LOST' ? 'var(--danger)' : 'var(--success)',
                        fontWeight: 700,
                        fontSize: '0.75rem',
                        flexShrink: 0,
                      }}
                    >
                      {item.item_type === 'LOST' ? 'LOST' : 'FND'}
                    </div>
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontWeight: 700, fontSize: '0.92rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {item.title}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                        <span>{item.location}</span>
                        <span>&bull;</span>
                        <span>{new Date(item.incident_date).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexShrink: 0 }}>
                    {getStatusBadge(item.status)}
                    <Link to={`/items/${item.id}`} className="btn btn-ghost btn-sm" style={{ padding: '0.35rem' }}>
                      <ExternalLink style={{ width: '0.9rem', height: '0.9rem' }} />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Notifications */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Recent Notices</h2>
            <Link to="/notifications" style={{ fontSize: '0.85rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '0.25rem', textDecoration: 'none' }}>
              Notifications Hub <ArrowRight style={{ width: '0.85rem', height: '0.85rem' }} />
            </Link>
          </div>

          {/* AI Match Alert Highlight if available */}
          {matchAlerts.length > 0 && (
            <div
              className="glass-card animate-fade-in"
              style={{
                padding: '1rem 1.25rem',
                marginBottom: '1rem',
                borderLeft: '4px solid #a855f7',
                background: 'rgba(168, 85, 247, 0.08)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '0.75rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Sparkles style={{ width: '1.25rem', height: '1.25rem', color: '#a855f7', flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#a855f7' }}>
                    {matchAlerts.length} Potential Match Alert{matchAlerts.length === 1 ? '' : 's'}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                    High-confidence matches detected for your reported items.
                  </div>
                </div>
              </div>
              <Link to="/my-reports" className="btn btn-primary btn-sm" style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem' }}>
                View Matches
              </Link>
            </div>
          )}

          {recentNotifications.length === 0 ? (
            <div className="glass-card" style={{ padding: '2.5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <Bell style={{ width: '2rem', height: '2rem', color: 'var(--text-muted)', margin: '0 auto 0.5rem' }} />
              <div style={{ fontWeight: 600 }}>No recent notices</div>
              <p style={{ fontSize: '0.82rem', marginTop: '0.25rem', color: 'var(--text-muted)' }}>
                System updates and claim alerts will appear here.
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {recentNotifications.map((n) => (
                <div
                  key={n.id}
                  className="glass-card"
                  style={{
                    padding: '1rem 1.25rem',
                    display: 'flex',
                    gap: '0.75rem',
                    alignItems: 'flex-start',
                    background: n.is_read ? 'transparent' : 'rgba(99, 102, 241, 0.05)',
                    borderLeft: !n.is_read ? '3px solid var(--primary)' : '1px solid var(--border)',
                  }}
                >
                  <div style={{ marginTop: '0.2rem' }}>
                    {n.type === 'MATCH_ALERT' ? (
                      <Sparkles style={{ width: '1rem', height: '1rem', color: '#a855f7' }} />
                    ) : (
                      <Bell style={{ width: '0.95rem', height: '0.95rem', color: n.is_read ? 'var(--text-muted)' : 'var(--primary)' }} />
                    )}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.25rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontWeight: n.is_read ? 600 : 700, fontSize: '0.88rem' }}>{n.title}</span>
                        {n.type === 'MATCH_ALERT' && (
                          <span className="badge" style={{ background: 'rgba(168, 85, 247, 0.2)', color: '#a855f7', fontSize: '0.68rem', padding: '0.1rem 0.4rem' }}>
                            MATCH ALERT
                          </span>
                        )}
                        {n.type === 'CLAIM_UPDATE' && (
                          <span className="badge" style={{ background: 'rgba(245, 158, 11, 0.2)', color: '#f59e0b', fontSize: '0.68rem', padding: '0.1rem 0.4rem' }}>
                            CLAIM
                          </span>
                        )}
                      </div>
                      <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                        {new Date(n.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.25rem', lineHeight: 1.4 }}>
                      {n.message}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
