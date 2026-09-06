import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { itemApi } from '../services/api';
import { Item, ItemType } from '../types/auth';
import {
  Package,
  PlusCircle,
  Clock,
  MapPin,
  Tag,
  AlertCircle,
  ExternalLink,
  Edit,
  Trash2,
} from 'lucide-react';

export const MyReports: React.FC = () => {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<'ALL' | ItemType>('ALL');

  // Confirmation modal state
  const [itemToClose, setItemToClose] = useState<Item | null>(null);
  const [closing, setClosing] = useState(false);

  const fetchReports = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await itemApi.getMyReports();
      setItems(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load your reports.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleCloseItem = async () => {
    if (!itemToClose) return;
    setClosing(true);
    try {
      await itemApi.closeItem(itemToClose.id);
      setItemToClose(null);
      await fetchReports();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to close item report.');
    } finally {
      setClosing(false);
    }
  };

  const filteredItems = items.filter((item) => {
    if (filterType === 'ALL') return true;
    return item.item_type === filterType;
  });

  const totalCount = items.length;
  const openCount = items.filter((i) => i.status === 'OPEN' || i.status === 'CLAIM_PENDING').length;
  const closedCount = items.filter((i) => i.status === 'CLOSED' || i.status === 'RESOLVED').length;

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

  return (
    <div className="container animate-fade-in" style={{ paddingTop: '2rem', maxWidth: '1100px' }}>
      {/* Top Header */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem',
          marginBottom: '2rem',
        }}
      >
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>My Reported Items</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Manage and track the status of lost and found incident reports you submitted.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <Link to="/report-lost" className="btn btn-secondary">
            <PlusCircle style={{ width: '1rem', height: '1rem', marginRight: '0.4rem' }} />
            Report Lost
          </Link>
          <Link to="/report-found" className="btn btn-primary">
            <PlusCircle style={{ width: '1rem', height: '1rem', marginRight: '0.4rem' }} />
            Report Found
          </Link>
        </div>
      </div>

      {/* Metrics Row */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '1.25rem',
          marginBottom: '2rem',
        }}
      >
        <div className="glass-card" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Total Reports
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, marginTop: '0.25rem' }}>
            {totalCount}
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Active / Open
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, marginTop: '0.25rem', color: 'var(--success)' }}>
            {openCount}
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.25rem' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Resolved / Closed
          </div>
          <div style={{ fontSize: '1.85rem', fontWeight: 800, marginTop: '0.25rem', color: 'var(--text-secondary)' }}>
            {closedCount}
          </div>
        </div>
      </div>

      {/* Filters Bar */}
      <div
        style={{
          display: 'flex',
          gap: '0.5rem',
          marginBottom: '1.5rem',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '0.75rem',
        }}
      >
        <button
          className={`btn ${filterType === 'ALL' ? 'btn-primary' : 'btn-ghost'}`}
          style={{ fontSize: '0.85rem', padding: '0.4rem 1.1rem' }}
          onClick={() => setFilterType('ALL')}
        >
          All ({items.length})
        </button>
        <button
          className={`btn ${filterType === 'LOST' ? 'btn-primary' : 'btn-ghost'}`}
          style={{ fontSize: '0.85rem', padding: '0.4rem 1.1rem' }}
          onClick={() => setFilterType('LOST')}
        >
          Lost Items ({items.filter((i) => i.item_type === 'LOST').length})
        </button>
        <button
          className={`btn ${filterType === 'FOUND' ? 'btn-primary' : 'btn-ghost'}`}
          style={{ fontSize: '0.85rem', padding: '0.4rem 1.1rem' }}
          onClick={() => setFilterType('FOUND')}
        >
          Found Items ({items.filter((i) => i.item_type === 'FOUND').length})
        </button>
      </div>

      {/* Error Banner */}
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

      {/* Loading State */}
      {loading ? (
        <div style={{ padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <div className="spinner" style={{ margin: '0 auto 1rem' }} />
          Loading your reports...
        </div>
      ) : filteredItems.length === 0 ? (
        /* Empty State */
        <div
          className="glass-card"
          style={{
            padding: '4rem 2rem',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
          }}
        >
          <div
            style={{
              width: '4rem',
              height: '4rem',
              borderRadius: '50%',
              background: 'var(--bg-glass)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem',
              color: 'var(--text-muted)',
            }}
          >
            <Package style={{ width: '2rem', height: '2rem' }} />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>No reports found</h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '420px', marginTop: '0.5rem', fontSize: '0.92rem' }}>
            {filterType === 'ALL'
              ? "You haven't reported any lost or found items yet. Did you lose something or discover an abandoned campus item?"
              : `You have no ${filterType.toLowerCase()} item reports in your history.`}
          </p>
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
            <Link to="/report-lost" className="btn btn-secondary">
              Report Lost Item
            </Link>
            <Link to="/report-found" className="btn btn-primary">
              Report Found Item
            </Link>
          </div>
        </div>
      ) : (
        /* Grid of Reports */
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '1.5rem',
          }}
        >
          {filteredItems.map((item) => (
            <div
              key={item.id}
              className="glass-card"
              style={{
                padding: '1.5rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.2s ease',
              }}
            >
              <div>
                {/* Image or fallback */}
                {item.image_url ? (
                  <div
                    style={{
                      height: '160px',
                      borderRadius: 'var(--radius-md)',
                      overflow: 'hidden',
                      marginBottom: '1rem',
                      background: '#000',
                    }}
                  >
                    <img
                      src={item.image_url}
                      alt={item.title}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    />
                  </div>
                ) : (
                  <div
                    style={{
                      height: '90px',
                      borderRadius: 'var(--radius-md)',
                      background: 'rgba(255, 255, 255, 0.03)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginBottom: '1rem',
                      color: 'var(--text-muted)',
                      border: '1px dashed var(--border-color)',
                    }}
                  >
                    <Package style={{ width: '1.75rem', height: '1.75rem' }} />
                  </div>
                )}

                {/* Badges */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <span
                    className="badge"
                    style={{
                      background: item.item_type === 'LOST' ? 'rgba(244, 63, 94, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                      color: item.item_type === 'LOST' ? 'var(--danger)' : 'var(--success)',
                      borderColor: item.item_type === 'LOST' ? 'rgba(244, 63, 94, 0.3)' : 'rgba(16, 185, 129, 0.3)',
                    }}
                  >
                    {item.item_type}
                  </span>
                  {getStatusBadge(item.status)}
                </div>

                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem' }}>
                  {item.title}
                </h3>

                <p
                  style={{
                    color: 'var(--text-secondary)',
                    fontSize: '0.88rem',
                    marginBottom: '1rem',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }}
                >
                  {item.description}
                </p>

                {/* Meta details */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Tag style={{ width: '0.9rem', height: '0.9rem' }} />
                    <span>{item.category}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <MapPin style={{ width: '0.9rem', height: '0.9rem' }} />
                    <span>{item.location}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Clock style={{ width: '0.9rem', height: '0.9rem' }} />
                    <span>{new Date(item.incident_date).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              {/* Action buttons */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  marginTop: '1.5rem',
                  paddingTop: '1rem',
                  borderTop: '1px solid var(--border-color)',
                }}
              >
                <Link
                  to={`/items/${item.id}`}
                  className="btn btn-secondary"
                  style={{ flex: 1, padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}
                >
                  <ExternalLink style={{ width: '0.85rem', height: '0.85rem', marginRight: '0.35rem' }} />
                  Details
                </Link>

                {item.status !== 'CLOSED' && (
                  <>
                    <Link
                      to={`/items/${item.id}/edit`}
                      className="btn btn-ghost"
                      style={{ padding: '0.4rem 0.65rem' }}
                      title="Edit Report"
                    >
                      <Edit style={{ width: '0.9rem', height: '0.9rem' }} />
                    </Link>
                    <button
                      className="btn btn-ghost"
                      style={{ padding: '0.4rem 0.65rem', color: 'var(--danger)' }}
                      title="Close Report"
                      onClick={() => setItemToClose(item)}
                    >
                      <Trash2 style={{ width: '0.9rem', height: '0.9rem' }} />
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Close Confirmation Modal */}
      {itemToClose && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.75)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
            padding: '1rem',
          }}
        >
          <div className="glass-card animate-fade-in" style={{ maxWidth: '440px', width: '100%', padding: '2rem' }}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>Close this report?</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.5rem' }}>
              Are you sure you want to mark "<strong>{itemToClose.title}</strong>" as CLOSED?
              This indicates the item has been recovered or the report cancelled.
            </p>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.75rem' }}>
              <button
                className="btn btn-secondary"
                onClick={() => setItemToClose(null)}
                disabled={closing}
              >
                Cancel
              </button>
              <button
                className="btn btn-primary"
                style={{ background: 'var(--danger)', borderColor: 'var(--danger)' }}
                onClick={handleCloseItem}
                disabled={closing}
              >
                {closing ? 'Closing...' : 'Yes, Close Report'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
