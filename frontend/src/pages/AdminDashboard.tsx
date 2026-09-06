import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { adminApi } from '../services/api';
import { AdminStats, AdminAnalytics, User } from '../types/auth';
import {
  Shield,
  Users,
  Package,
  FileCheck,
  AlertCircle,
  RefreshCw,
  ArrowRight,
  Search,
  X,
  BarChart3,
  Sparkles,
  MapPin,
  Layers,
} from 'lucide-react';

export const AdminDashboard: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [analytics, setAnalytics] = useState<AdminAnalytics | null>(null);
  const [period, setPeriod] = useState<'7d' | '30d' | '90d'>('30d');
  const [loading, setLoading] = useState(true);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Users modal state
  const [usersModalOpen, setUsersModalOpen] = useState(false);
  const [usersList, setUsersList] = useState<User[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);

  const fetchDashboardData = async (selectedPeriod = period) => {
    try {
      setError(null);
      const [statsData, analyticsData] = await Promise.all([
        adminApi.getStats(),
        adminApi.getAnalytics(selectedPeriod),
      ]);
      setStats(statsData);
      setAnalytics(analyticsData);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load administrator statistics.');
    } finally {
      setLoading(false);
      setRefreshing(false);
      setAnalyticsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData(period);
  }, []);

  const handlePeriodChange = async (newPeriod: '7d' | '30d' | '90d') => {
    setPeriod(newPeriod);
    setAnalyticsLoading(true);
    try {
      const data = await adminApi.getAnalytics(newPeriod);
      setAnalytics(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update analytics period.');
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData(period);
  };

  const handleOpenUsersModal = async () => {
    setUsersModalOpen(true);
    try {
      setLoadingUsers(true);
      const users = await adminApi.getUsers();
      setUsersList(users);
    } catch (err: any) {
      console.error('Failed to load user list', err);
    } finally {
      setLoadingUsers(false);
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ paddingTop: '5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <div className="spinner" style={{ margin: '0 auto 1rem' }} />
        Loading administrative console &amp; analytics...
      </div>
    );
  }

  // Calculate distributions for visual progress bars
  const lostCount = analytics?.lost_vs_found_distribution?.lost || 0;
  const foundCount = analytics?.lost_vs_found_distribution?.found || 0;
  const totalReportsInPeriod = lostCount + foundCount;
  const lostPercent = totalReportsInPeriod > 0 ? Math.round((lostCount / totalReportsInPeriod) * 100) : 50;
  const foundPercent = totalReportsInPeriod > 0 ? 100 - lostPercent : 50;

  const appClaims = analytics?.approved_claims || 0;
  const pendClaims = analytics?.pending_claims || 0;
  const rejClaims = analytics?.rejected_claims || 0;
  const totalClaimsInPeriod = appClaims + pendClaims + rejClaims;

  return (
    <div className="container animate-fade-in" style={{ paddingTop: '2rem', maxWidth: '1200px', paddingBottom: '3rem' }}>
      {/* Header Banner */}
      <div
        className="glass-card"
        style={{
          padding: '2rem 2.5rem',
          marginBottom: '2rem',
          borderLeft: '4px solid var(--danger)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1.5rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div
            style={{
              width: '3.5rem',
              height: '3.5rem',
              borderRadius: 'var(--radius-md)',
              background: 'var(--danger-bg)',
              border: '1px solid rgba(244, 63, 94, 0.3)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Shield style={{ width: '2rem', height: '2rem', color: 'var(--danger)' }} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <h1 style={{ fontSize: '1.85rem', fontWeight: 800 }}>Campus Security Administrator Portal</h1>
              <span className="badge badge-danger">ADMIN ONLY</span>
            </div>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginTop: '0.25rem' }}>
              Restricted management console &amp; analytics for campus lost &amp; found operations ({user?.email})
            </p>
          </div>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="btn btn-secondary btn-sm"
          style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <RefreshCw style={{ width: '0.9rem', height: '0.9rem', animation: refreshing ? 'spin 1s linear infinite' : 'none' }} />
          {refreshing ? 'Refreshing...' : 'Refresh Metrics'}
        </button>
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

      {/* Top Level All-Time Metric Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1.25rem',
          marginBottom: '2rem',
        }}
      >
        <div className="glass-card" style={{ padding: '1.5rem', borderLeft: '4px solid var(--primary)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>REGISTERED USERS</span>
            <Users style={{ width: '1rem', height: '1rem', color: 'var(--primary)' }} />
          </div>
          <div style={{ fontSize: '2.25rem', fontWeight: 800, marginTop: '0.5rem' }}>{stats?.total_users || 0}</div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {analytics?.active_users || 0} active accounts
          </p>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem', borderLeft: '4px solid #818cf8' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>ALL-TIME ITEMS</span>
            <Package style={{ width: '1rem', height: '1rem', color: '#818cf8' }} />
          </div>
          <div style={{ fontSize: '2.25rem', fontWeight: 800, marginTop: '0.5rem' }}>{stats?.total_items || 0}</div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            {stats?.items_by_type?.['LOST'] || 0} Lost vs {stats?.items_by_type?.['FOUND'] || 0} Found
          </p>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem', borderLeft: '4px solid #f59e0b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>PENDING CLAIMS</span>
            <FileCheck style={{ width: '1rem', height: '1rem', color: '#f59e0b' }} />
          </div>
          <div style={{ fontSize: '2.25rem', fontWeight: 800, marginTop: '0.5rem', color: '#f59e0b' }}>
            {stats?.pending_claims || 0}
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Awaiting campus staff review
          </p>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem', borderLeft: '4px solid var(--success)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)' }}>MATCHES EVALUATED</span>
            <Sparkles style={{ width: '1rem', height: '1rem', color: 'var(--success)' }} />
          </div>
          <div style={{ fontSize: '2.25rem', fontWeight: 800, marginTop: '0.5rem' }}>
            {analytics?.high_confidence_matches || 0}
          </div>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            High-confidence match alerts
          </p>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* PHASE 12: DEEP ADMIN ANALYTICS & TIME HORIZONS */}
      {/* ========================================================================= */}
      <div className="glass-card" style={{ padding: '1.75rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <BarChart3 style={{ width: '1.35rem', height: '1.35rem', color: 'var(--primary)' }} />
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Deterministic Platform Analytics</h2>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                Database-aggregated metrics for the selected time horizon (No AI hallucination)
              </p>
            </div>
          </div>

          {/* Time Horizon Selector */}
          <div style={{ display: 'flex', gap: '0.5rem', background: 'var(--surface)', padding: '0.3rem', borderRadius: 'var(--radius-sm)' }}>
            {(['7d', '30d', '90d'] as const).map((p) => (
              <button
                key={p}
                onClick={() => handlePeriodChange(p)}
                disabled={analyticsLoading}
                className="btn btn-sm"
                style={{
                  background: period === p ? 'var(--primary)' : 'transparent',
                  color: period === p ? '#fff' : 'var(--text-secondary)',
                  fontWeight: period === p ? 700 : 500,
                  fontSize: '0.78rem',
                  padding: '0.35rem 0.85rem',
                  borderRadius: 'var(--radius-sm)',
                  border: 'none',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
              >
                {p === '7d' ? 'Last 7 Days' : p === '30d' ? 'Last 30 Days' : 'Last 90 Days'}
              </button>
            ))}
          </div>
        </div>

        {/* Analytics Highlights for Selected Horizon */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
            gap: '1rem',
            marginBottom: '1.75rem',
          }}
        >
          <div style={{ padding: '1rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>LOST REPORTS ({period})</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.25rem', color: '#f43f5e' }}>{lostCount}</div>
          </div>

          <div style={{ padding: '1rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>FOUND REPORTS ({period})</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.25rem', color: '#10b981' }}>{foundCount}</div>
          </div>

          <div style={{ padding: '1rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>APPROVED CLAIMS ({period})</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.25rem', color: '#10b981' }}>{appClaims}</div>
          </div>

          <div style={{ padding: '1rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>MATCH ALERTS ({period})</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.25rem', color: '#818cf8' }}>
              {analytics?.high_confidence_matches || 0}
            </div>
          </div>

          <div style={{ padding: '1rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>NOTIFICATIONS SENT</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.25rem', color: '#38bdf8' }}>
              {analytics?.notifications_generated || 0}
            </div>
          </div>
        </div>

        {/* Visual Distribution Bars */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          {/* Lost vs Found Distribution */}
          <div style={{ padding: '1.25rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.85rem', fontWeight: 600 }}>
              <span>Lost vs Found Ratio</span>
              <span style={{ color: 'var(--text-muted)' }}>{totalReportsInPeriod} Total Reports</span>
            </div>
            {totalReportsInPeriod > 0 ? (
              <>
                <div style={{ display: 'flex', height: '14px', borderRadius: '7px', overflow: 'hidden', background: 'rgba(255,255,255,0.05)' }}>
                  <div style={{ width: `${lostPercent}%`, background: '#f43f5e' }} title={`Lost: ${lostCount} (${lostPercent}%)`} />
                  <div style={{ width: `${foundPercent}%`, background: '#10b981' }} title={`Found: ${foundCount} (${foundPercent}%)`} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.75rem' }}>
                  <span style={{ color: '#f43f5e' }}>● Lost: {lostCount} ({lostPercent}%)</span>
                  <span style={{ color: '#10b981' }}>● Found: {foundCount} ({foundPercent}%)</span>
                </div>
              </>
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', padding: '0.5rem 0' }}>No reports recorded in this period.</div>
            )}
          </div>

          {/* Claims Outcome Distribution */}
          <div style={{ padding: '1.25rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.85rem', fontWeight: 600 }}>
              <span>Claim Review Outcomes</span>
              <span style={{ color: 'var(--text-muted)' }}>{totalClaimsInPeriod} Total Claims</span>
            </div>
            {totalClaimsInPeriod > 0 ? (
              <>
                <div style={{ display: 'flex', height: '14px', borderRadius: '7px', overflow: 'hidden', background: 'rgba(255,255,255,0.05)' }}>
                  <div style={{ width: `${(appClaims / totalClaimsInPeriod) * 100}%`, background: '#10b981' }} />
                  <div style={{ width: `${(pendClaims / totalClaimsInPeriod) * 100}%`, background: '#f59e0b' }} />
                  <div style={{ width: `${(rejClaims / totalClaimsInPeriod) * 100}%`, background: '#ef4444' }} />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.75rem' }}>
                  <span style={{ color: '#10b981' }}>● Approved: {appClaims}</span>
                  <span style={{ color: '#f59e0b' }}>● Pending: {pendClaims}</span>
                  <span style={{ color: '#ef4444' }}>● Rejected: {rejClaims}</span>
                </div>
              </>
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', padding: '0.5rem 0' }}>No claims recorded in this period.</div>
            )}
          </div>
        </div>

        {/* Categorical & Location Breakdowns */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
          {/* Categories */}
          <div style={{ padding: '1.25rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
              <Layers style={{ width: '1rem', height: '1rem', color: 'var(--primary)' }} />
              <span style={{ fontSize: '0.88rem', fontWeight: 600 }}>Reports by Category ({period})</span>
            </div>
            {analytics?.reports_by_category && analytics.reports_by_category.length > 0 ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {analytics.reports_by_category.map((c) => (
                  <span
                    key={c.category}
                    className="badge badge-primary"
                    style={{ fontSize: '0.78rem', padding: '0.35rem 0.65rem' }}
                  >
                    {c.category}: <strong>{c.count}</strong>
                  </span>
                ))}
              </div>
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No categorical data in this period.</div>
            )}
          </div>

          {/* Locations */}
          <div style={{ padding: '1.25rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
              <MapPin style={{ width: '1rem', height: '1rem', color: 'var(--success)' }} />
              <span style={{ fontSize: '0.88rem', fontWeight: 600 }}>Reports by Campus Location ({period})</span>
            </div>
            {analytics?.reports_by_location && analytics.reports_by_location.length > 0 ? (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {analytics.reports_by_location.map((l) => (
                  <span
                    key={l.location}
                    className="badge badge-success"
                    style={{ fontSize: '0.78rem', padding: '0.35rem 0.65rem' }}
                  >
                    {l.location}: <strong>{l.count}</strong>
                  </span>
                ))}
              </div>
            ) : (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No location data in this period.</div>
            )}
          </div>
        </div>
      </div>

      {/* Item Status Breakdown */}
      <div className="glass-card" style={{ padding: '1.75rem', marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1.25rem' }}>All-Time Campus Item Status Breakdown</h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
            gap: '1rem',
          }}
        >
          <div style={{ padding: '1rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--success)', fontWeight: 600 }}>OPEN</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.25rem' }}>
              {stats?.items_by_status?.['OPEN'] || 0}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>Awaiting match / claim</div>
          </div>

          <div style={{ padding: '1rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.78rem', color: '#f59e0b', fontWeight: 600 }}>CLAIM PENDING</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.25rem' }}>
              {stats?.items_by_status?.['CLAIM_PENDING'] || 0}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>Verification in progress</div>
          </div>

          <div style={{ padding: '1rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.78rem', color: '#38bdf8', fontWeight: 600 }}>CLAIMED</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.25rem' }}>
              {stats?.items_by_status?.['CLAIMED'] || 0}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>Ownership approved</div>
          </div>

          <div style={{ padding: '1rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--primary)', fontWeight: 600 }}>RESOLVED</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.25rem' }}>
              {stats?.items_by_status?.['RESOLVED'] || 0}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>Handed back to owner</div>
          </div>

          <div style={{ padding: '1rem', background: 'var(--surface)', borderRadius: 'var(--radius-sm)' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--danger)', fontWeight: 600 }}>CLOSED</div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, marginTop: '0.25rem' }}>
              {stats?.items_by_status?.['CLOSED'] || 0}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>Archived or cancelled</div>
          </div>
        </div>
      </div>

      {/* Quick Links & Actions */}
      <div style={{ marginBottom: '2.5rem' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '1rem' }}>Administrative Tools &amp; Actions</h2>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.25rem',
          }}
        >
          <Link
            to="/admin/claims"
            className="glass-card"
            style={{
              padding: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              textDecoration: 'none',
              borderLeft: '4px solid #f59e0b',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div
                style={{
                  width: '3rem',
                  height: '3rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(245, 158, 11, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#f59e0b',
                }}
              >
                <FileCheck style={{ width: '1.5rem', height: '1.5rem' }} />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>Review Claims Queue</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                  {stats?.pending_claims || 0} claims awaiting review
                </div>
              </div>
            </div>
            <ArrowRight style={{ width: '1.25rem', height: '1.25rem', color: '#f59e0b' }} />
          </Link>

          <button
            onClick={handleOpenUsersModal}
            className="glass-card"
            style={{
              padding: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              textAlign: 'left',
              cursor: 'pointer',
              borderLeft: '4px solid var(--primary)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div
                style={{
                  width: '3rem',
                  height: '3rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(99, 102, 241, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--primary)',
                }}
              >
                <Users style={{ width: '1.5rem', height: '1.5rem' }} />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>Registered Users Directory</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                  Inspect accounts &amp; departments
                </div>
              </div>
            </div>
            <ArrowRight style={{ width: '1.25rem', height: '1.25rem', color: 'var(--primary)' }} />
          </button>

          <Link
            to="/search"
            className="glass-card"
            style={{
              padding: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              textDecoration: 'none',
              borderLeft: '4px solid var(--success)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div
                style={{
                  width: '3rem',
                  height: '3rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(16, 185, 129, 0.15)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--success)',
                }}
              >
                <Search style={{ width: '1.5rem', height: '1.5rem' }} />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>Search Registry</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                  Full-text campus inventory search
                </div>
              </div>
            </div>
            <ArrowRight style={{ width: '1.25rem', height: '1.25rem', color: 'var(--success)' }} />
          </Link>
        </div>
      </div>

      {/* Recent Platform Activity Audit Log */}
      <div className="glass-card" style={{ padding: '1.75rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Recent Administrative Activity (Audit Log)</h2>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
              Immutable record of security and administrative actions
            </p>
          </div>
          <span className="badge badge-primary">LIVE AUDIT STREAM</span>
        </div>

        {stats?.recent_activity && stats.recent_activity.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', color: 'var(--text-secondary)' }}>
                  <th style={{ padding: '0.75rem 0.5rem' }}>ACTION</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>ENTITY</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>ACTOR</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>DETAILS</th>
                  <th style={{ padding: '0.75rem 0.5rem' }}>TIMESTAMP</th>
                </tr>
              </thead>
              <tbody>
                {stats.recent_activity.map((log) => (
                  <tr key={log.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                    <td style={{ padding: '0.75rem 0.5rem', fontWeight: 700, color: 'var(--primary)' }}>{log.action}</td>
                    <td style={{ padding: '0.75rem 0.5rem', color: 'var(--text-muted)' }}>
                      {log.entity_type} {log.entity_id ? `#${log.entity_id}` : ''}
                    </td>
                    <td style={{ padding: '0.75rem 0.5rem' }}>User #{log.actor_id}</td>
                    <td style={{ padding: '0.75rem 0.5rem', color: 'var(--text-secondary)', maxWidth: '380px' }}>
                      {log.details || '—'}
                    </td>
                    <td style={{ padding: '0.75rem 0.5rem', color: 'var(--text-muted)', fontSize: '0.78rem' }}>
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            No recent audit activity found.
          </div>
        )}
      </div>

      {/* Users Directory Modal */}
      {usersModalOpen && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(4px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '1rem',
          }}
        >
          <div
            className="glass-card animate-scale-up"
            style={{
              width: '100%',
              maxWidth: '750px',
              maxHeight: '80vh',
              overflowY: 'auto',
              padding: '2rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '1.25rem',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Users style={{ width: '1.25rem', height: '1.25rem', color: 'var(--primary)' }} />
                <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>Registered Users Directory</h3>
              </div>
              <button
                onClick={() => setUsersModalOpen(false)}
                className="btn btn-ghost btn-sm"
                style={{ padding: '0.4rem' }}
              >
                <X style={{ width: '1.25rem', height: '1.25rem' }} />
              </button>
            </div>

            {loadingUsers ? (
              <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
                <div className="spinner" style={{ margin: '0 auto 1rem' }} />
                Loading users...
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {usersList.map((u) => (
                  <div
                    key={u.id}
                    style={{
                      padding: '0.85rem 1rem',
                      background: 'var(--surface)',
                      borderRadius: 'var(--radius-sm)',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontWeight: 700, fontSize: '0.92rem' }}>{u.full_name}</span>
                        <span className={`badge ${u.role === 'ADMIN' ? 'badge-danger' : 'badge-primary'}`} style={{ fontSize: '0.7rem' }}>
                          {u.role}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                        {u.email} {u.department ? `• ${u.department}` : ''} {u.student_id ? `• ID: ${u.student_id}` : ''}
                      </div>
                    </div>
                    <span className="badge badge-success" style={{ fontSize: '0.72rem' }}>
                      {u.is_active ? 'ACTIVE' : 'INACTIVE'}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
