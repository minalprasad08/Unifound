import React, { useState, useEffect, useRef } from 'react';
import { notificationApi } from '../../services/api';
import { Notification } from '../../types/auth';
import {
  Bell,
  CheckCheck,
  FileCheck,
  Shield,
  Info,
  Sparkles,
} from 'lucide-react';

export const NotificationsMenu: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const unreadCount = notifications.filter((n) => !n.is_read).length;

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const data = await notificationApi.getMyNotifications();
      setNotifications(data);
    } catch {
      // Background poll silently fails
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000); // 30s poll
    return () => clearInterval(interval);
  }, []);

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMarkAsRead = async (id: number) => {
    try {
      await notificationApi.markAsRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
      );
    } catch {
      // Ignore
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationApi.markAllAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch {
      // Ignore
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'CLAIM_UPDATE':
        return <FileCheck style={{ width: '1rem', height: '1rem', color: 'var(--primary)' }} />;
      case 'MATCH_ALERT':
        return <Sparkles style={{ width: '1rem', height: '1rem', color: 'var(--warning)' }} />;
      case 'SYSTEM':
        return <Shield style={{ width: '1rem', height: '1rem', color: 'var(--info)' }} />;
      default:
        return <Info style={{ width: '1rem', height: '1rem', color: 'var(--text-muted)' }} />;
    }
  };

  return (
    <div ref={menuRef} style={{ position: 'relative' }}>
      {/* Bell Trigger Button */}
      <button
        type="button"
        className="btn btn-ghost"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'relative',
          padding: '0.5rem',
          borderRadius: 'var(--radius-full)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
        aria-label="Notifications"
      >
        <Bell style={{ width: '1.25rem', height: '1.25rem' }} />
        {unreadCount > 0 && (
          <span
            style={{
              position: 'absolute',
              top: '2px',
              right: '2px',
              background: 'var(--danger)',
              color: '#fff',
              fontSize: '0.68rem',
              fontWeight: 700,
              width: '18px',
              height: '18px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '2px solid var(--bg-dark)',
            }}
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Popover Dropdown */}
      {isOpen && (
        <div
          className="glass-card animate-fade-in"
          style={{
            position: 'absolute',
            right: 0,
            top: 'calc(100% + 8px)',
            width: '360px',
            maxHeight: '480px',
            overflowY: 'auto',
            padding: 0,
            zIndex: 1000,
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.2)',
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '1rem 1.25rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              borderBottom: '1px solid var(--border-color)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontWeight: 700, fontSize: '0.98rem' }}>Notifications</span>
              {unreadCount > 0 && (
                <span className="badge badge-primary" style={{ fontSize: '0.72rem', padding: '0.1rem 0.4rem' }}>
                  {unreadCount} new
                </span>
              )}
            </div>

            {unreadCount > 0 && (
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                onClick={handleMarkAllAsRead}
                style={{ fontSize: '0.78rem', color: 'var(--primary)', display: 'flex', alignItems: 'center', gap: '0.3rem', padding: '0.25rem 0.5rem' }}
              >
                <CheckCheck style={{ width: '0.85rem', height: '0.85rem' }} />
                Mark all read
              </button>
            )}
          </div>

          {/* List */}
          {loading && notifications.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
              Loading notices...
            </div>
          ) : notifications.length === 0 ? (
            <div style={{ padding: '2.5rem 1.5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              <Bell style={{ width: '2rem', height: '2rem', color: 'var(--text-muted)', margin: '0 auto 0.5rem' }} />
              <div style={{ fontWeight: 600, fontSize: '0.92rem' }}>All caught up!</div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                You have no active notifications right now.
              </div>
            </div>
          ) : (
            <div>
              {notifications.map((n) => (
                <div
                  key={n.id}
                  onClick={() => !n.is_read && handleMarkAsRead(n.id)}
                  style={{
                    padding: '0.85rem 1.25rem',
                    borderBottom: '1px solid var(--border-subtle)',
                    background: n.is_read ? 'transparent' : 'rgba(99, 102, 241, 0.06)',
                    cursor: n.is_read ? 'default' : 'pointer',
                    display: 'flex',
                    gap: '0.75rem',
                    alignItems: 'flex-start',
                    transition: 'background 0.15s ease',
                  }}
                >
                  <div style={{ marginTop: '0.15rem' }}>{getNotificationIcon(n.type)}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <span style={{ fontWeight: n.is_read ? 600 : 700, fontSize: '0.88rem' }}>{n.title}</span>
                      {!n.is_read && (
                        <span
                          style={{
                            width: '7px',
                            height: '7px',
                            borderRadius: '50%',
                            background: 'var(--primary)',
                            marginTop: '0.35rem',
                          }}
                        />
                      )}
                    </div>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.2rem', lineHeight: 1.4 }}>
                      {n.message}
                    </p>
                    <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '0.35rem', display: 'block' }}>
                      {new Date(n.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
