import React, { useState, useEffect } from 'react';
import { notificationApi } from '../services/api';
import { Notification } from '../types/auth';
import {
  Bell,
  CheckCircle2,
  CheckCheck,
  AlertCircle,
  FileCheck,
  Sparkles,
  Info,
  Clock,
} from 'lucide-react';

export const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [filter, setFilter] = useState<'ALL' | 'UNREAD'>('ALL');
  const [loading, setLoading] = useState(true);
  const [markingAll, setMarkingAll] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await notificationApi.getMyNotifications();
      setNotifications(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch notifications.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleMarkAsRead = async (id: number) => {
    try {
      await notificationApi.markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch (err) {
      console.error('Failed to mark notification as read', err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      setMarkingAll(true);
      await notificationApi.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to mark all as read.');
    } finally {
      setMarkingAll(false);
    }
  };

  const filteredNotifications = notifications.filter((n) => {
    if (filter === 'UNREAD') return !n.is_read;
    return true;
  });

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'CLAIM_UPDATE':
        return <FileCheck style={{ width: '1.1rem', height: '1.1rem', color: '#f59e0b' }} />;
      case 'MATCH_ALERT':
        return <Sparkles style={{ width: '1.1rem', height: '1.1rem', color: '#818cf8' }} />;
      default:
        return <Info style={{ width: '1.1rem', height: '1.1rem', color: 'var(--primary)' }} />;
    }
  };

  return (
    <div className="container animate-fade-in" style={{ paddingTop: '2rem', maxWidth: '850px', paddingBottom: '3rem' }}>
      {/* Page Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
          marginBottom: '2rem',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <h1 style={{ fontSize: '1.85rem', fontWeight: 800 }}>Notifications Center</h1>
            {unreadCount > 0 && (
              <span className="badge badge-primary">{unreadCount} New</span>
            )}
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginTop: '0.25rem' }}>
            Real-time updates regarding claim verification status, campus match discoveries, and account activity.
          </p>
        </div>

        {unreadCount > 0 && (
          <button
            onClick={handleMarkAllAsRead}
            disabled={markingAll}
            className="btn btn-secondary btn-sm"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
          >
            <CheckCheck style={{ width: '1rem', height: '1rem' }} />
            {markingAll ? 'Updating...' : 'Mark All as Read'}
          </button>
        )}
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

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
        <button
          onClick={() => setFilter('ALL')}
          className={`btn btn-sm ${filter === 'ALL' ? 'btn-primary' : 'btn-secondary'}`}
        >
          All ({notifications.length})
        </button>
        <button
          onClick={() => setFilter('UNREAD')}
          className={`btn btn-sm ${filter === 'UNREAD' ? 'btn-primary' : 'btn-secondary'}`}
        >
          Unread Only ({unreadCount})
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="glass-card" style={{ padding: '3.5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <div className="spinner" style={{ margin: '0 auto 1rem' }} />
          Loading your notifications...
        </div>
      ) : filteredNotifications.length === 0 ? (
        <div className="glass-card" style={{ padding: '3.5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <Bell style={{ width: '2.5rem', height: '2.5rem', color: 'var(--text-muted)', margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            {filter === 'UNREAD' ? 'You have no unread notifications' : 'No notifications yet'}
          </h3>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            When updates occur on your items or claims, notifications will appear here.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {filteredNotifications.map((n) => (
            <div
              key={n.id}
              className="glass-card"
              style={{
                padding: '1.25rem',
                display: 'flex',
                alignItems: 'flex-start',
                justifyContent: 'space-between',
                gap: '1rem',
                borderLeft: n.is_read ? '1px solid var(--border-subtle)' : '4px solid var(--primary)',
                background: n.is_read ? 'transparent' : 'rgba(99, 102, 241, 0.04)',
              }}
            >
              <div style={{ display: 'flex', gap: '0.85rem', minWidth: 0, flex: 1 }}>
                <div
                  style={{
                    width: '2.4rem',
                    height: '2.4rem',
                    borderRadius: 'var(--radius-sm)',
                    background: 'var(--surface)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    marginTop: '0.1rem',
                  }}
                >
                  {getTypeIcon(n.type)}
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <span style={{ fontWeight: n.is_read ? 600 : 700, fontSize: '0.95rem' }}>{n.title}</span>
                    <span className="badge" style={{ fontSize: '0.72rem' }}>{n.type}</span>
                    {!n.is_read && <span className="badge badge-primary" style={{ fontSize: '0.7rem' }}>NEW</span>}
                  </div>
                  <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.35rem', lineHeight: 1.5 }}>
                    {n.message}
                  </p>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--text-muted)', fontSize: '0.76rem', marginTop: '0.5rem' }}>
                    <Clock style={{ width: '0.8rem', height: '0.8rem' }} />
                    <span>{new Date(n.created_at).toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {!n.is_read && (
                <button
                  onClick={() => handleMarkAsRead(n.id)}
                  className="btn btn-ghost btn-sm"
                  title="Mark as read"
                  style={{ color: 'var(--primary)', flexShrink: 0 }}
                >
                  <CheckCircle2 style={{ width: '1.15rem', height: '1.15rem' }} />
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
