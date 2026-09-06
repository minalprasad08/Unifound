import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { claimApi } from '../services/api';
import { Claim, ClaimStatus } from '../types/auth';
import {
  FileCheck,
  Clock,
  MapPin,
  Tag,
  AlertCircle,
  CheckCircle2,
  XCircle,
  ExternalLink,
  Ban,
  Package,
} from 'lucide-react';

export const MyClaims: React.FC = () => {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Cancellation state
  const [cancellingClaim, setCancellingClaim] = useState<Claim | null>(null);
  const [cancelling, setCancelling] = useState(false);
  const [cancelError, setCancelError] = useState<string | null>(null);

  // Filter tab
  const [statusFilter, setStatusFilter] = useState<ClaimStatus | 'ALL'>('ALL');

  const fetchClaims = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await claimApi.getMyClaims();
      setClaims(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load your claims.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClaims();
  }, []);

  const handleConfirmCancel = async () => {
    if (!cancellingClaim) return;
    try {
      setCancelling(true);
      setCancelError(null);
      await claimApi.cancelClaim(cancellingClaim.id);
      setCancellingClaim(null);
      await fetchClaims();
    } catch (err: any) {
      setCancelError(err.response?.data?.detail || 'Failed to cancel claim.');
    } finally {
      setCancelling(false);
    }
  };

  const getStatusBadge = (status: ClaimStatus) => {
    switch (status) {
      case 'PENDING':
        return <span className="badge badge-warning">UNDER REVIEW</span>;
      case 'APPROVED':
        return <span className="badge badge-success">APPROVED</span>;
      case 'REJECTED':
        return <span className="badge badge-danger">REJECTED</span>;
      case 'CANCELLED':
        return <span className="badge">CANCELLED</span>;
      default:
        return <span className="badge">{status}</span>;
    }
  };

  const filteredClaims = statusFilter === 'ALL'
    ? claims
    : claims.filter((c) => c.status === statusFilter);

  return (
    <div className="container animate-fade-in" style={{ paddingTop: '2rem', maxWidth: '1000px' }}>
      {/* Header */}
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
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800 }}>My Ownership Claims</h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
            Track, review, or cancel claims you have filed to reclaim property.
          </p>
        </div>

        <Link to="/search" className="btn btn-secondary">
          <Package style={{ width: '0.95rem', height: '0.95rem', marginRight: '0.4rem' }} />
          Browse Campus Items
        </Link>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.75rem', overflowX: 'auto', paddingBottom: '0.25rem' }}>
        {(['ALL', 'PENDING', 'APPROVED', 'REJECTED', 'CANCELLED'] as const).map((tab) => (
          <button
            key={tab}
            className={`btn btn-sm ${statusFilter === tab ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setStatusFilter(tab)}
            style={{ fontSize: '0.85rem' }}
          >
            {tab === 'ALL' ? 'All Claims' : tab}
            <span
              style={{
                marginLeft: '0.4rem',
                opacity: 0.75,
                background: 'rgba(255, 255, 255, 0.15)',
                padding: '0.1rem 0.4rem',
                borderRadius: '999px',
                fontSize: '0.75rem',
              }}
            >
              {tab === 'ALL' ? claims.length : claims.filter((c) => c.status === tab).length}
            </span>
          </button>
        ))}
      </div>

      {/* Error Alert */}
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
        <div style={{ padding: '5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <div className="spinner" style={{ margin: '0 auto 1rem' }} />
          Loading your submitted claims...
        </div>
      ) : filteredClaims.length === 0 ? (
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
            <FileCheck style={{ width: '2rem', height: '2rem' }} />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>No claims found</h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '420px', marginTop: '0.5rem', fontSize: '0.9rem' }}>
            {statusFilter === 'ALL'
              ? "You haven't submitted any ownership claims yet. Search reported found items to claim what belongs to you."
              : `You do not have any claims with status ${statusFilter}.`}
          </p>
          <Link to="/search" className="btn btn-primary" style={{ marginTop: '1.5rem' }}>
            Search Found Items
          </Link>
        </div>
      ) : (
        /* Claims List */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '3rem' }}>
          {filteredClaims.map((claim) => (
            <div
              key={claim.id}
              className="glass-card animate-fade-in"
              style={{
                padding: '1.5rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1.25rem',
              }}
            >
              {/* Header row with badges and item link */}
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  flexWrap: 'wrap',
                  gap: '0.75rem',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
                    {getStatusBadge(claim.status)}
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Claim #{claim.id} &bull; Filed {new Date(claim.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>
                    {claim.item ? claim.item.title : `Item #${claim.item_id}`}
                  </h3>
                </div>

                {claim.item && (
                  <Link
                    to={`/items/${claim.item.id}`}
                    className="btn btn-ghost btn-sm"
                    style={{ fontSize: '0.82rem' }}
                  >
                    <ExternalLink style={{ width: '0.85rem', height: '0.85rem', marginRight: '0.35rem' }} />
                    View Item
                  </Link>
                )}
              </div>

              {/* Item Details Preview */}
              {claim.item && (
                <div
                  style={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '1.25rem',
                    background: 'var(--bg-glass)',
                    padding: '0.85rem 1rem',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)',
                    fontSize: '0.85rem',
                    color: 'var(--text-secondary)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <Tag style={{ width: '0.85rem', height: '0.85rem', color: 'var(--primary)' }} />
                    <span>{claim.item.category}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <MapPin style={{ width: '0.85rem', height: '0.85rem', color: 'var(--primary)' }} />
                    <span>{claim.item.location}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <Clock style={{ width: '0.85rem', height: '0.85rem', color: 'var(--primary)' }} />
                    <span>Incident: {new Date(claim.item.incident_date).toLocaleDateString()}</span>
                  </div>
                </div>
              )}

              {/* Claim Body */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                <div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                    Your Ownership Explanation
                  </div>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                    {claim.description}
                  </p>
                </div>

                {claim.evidence && (
                  <div>
                    <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                      Provided Proof / Evidence
                    </div>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                      {claim.evidence}
                    </p>
                  </div>
                )}
              </div>

              {/* Reviewer Note Banner if Approved or Rejected */}
              {claim.admin_notes && (
                <div
                  style={{
                    padding: '0.85rem 1rem',
                    borderRadius: 'var(--radius-md)',
                    background: claim.status === 'APPROVED' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(244, 63, 94, 0.08)',
                    border: `1px solid ${claim.status === 'APPROVED' ? 'rgba(16, 185, 129, 0.25)' : 'rgba(244, 63, 94, 0.25)'}`,
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '0.6rem',
                  }}
                >
                  {claim.status === 'APPROVED' ? (
                    <CheckCircle2 style={{ width: '1.1rem', height: '1.1rem', color: 'var(--success)', marginTop: '0.15rem' }} />
                  ) : (
                    <XCircle style={{ width: '1.1rem', height: '1.1rem', color: 'var(--danger)', marginTop: '0.15rem' }} />
                  )}
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: claim.status === 'APPROVED' ? 'var(--success)' : 'var(--danger)' }}>
                      Campus Administration Decision Notes
                    </div>
                    <div style={{ fontSize: '0.88rem', color: 'var(--text-primary)', marginTop: '0.2rem' }}>
                      {claim.admin_notes}
                    </div>
                  </div>
                </div>
              )}

              {/* Actions */}
              {claim.status === 'PENDING' && (
                <div style={{ display: 'flex', justifyContent: 'flex-end', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)' }}>
                  <button
                    type="button"
                    className="btn btn-ghost btn-sm"
                    style={{ color: 'var(--danger)' }}
                    onClick={() => {
                      setCancellingClaim(claim);
                      setCancelError(null);
                    }}
                  >
                    <Ban style={{ width: '0.85rem', height: '0.85rem', marginRight: '0.35rem' }} />
                    Cancel Claim
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Cancel Confirmation Modal */}
      {cancellingClaim && (
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
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>Cancel Ownership Claim</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.5rem' }}>
              Are you sure you want to cancel your claim for <strong>"{cancellingClaim.item?.title || `Item #${cancellingClaim.item_id}`}"</strong>?
              If no other claims are pending, the item will return to OPEN status.
            </p>

            {cancelError && (
              <div
                style={{
                  padding: '0.75rem',
                  marginTop: '1rem',
                  background: 'var(--danger-bg)',
                  borderColor: 'var(--danger)',
                  color: 'var(--danger)',
                  fontSize: '0.85rem',
                  borderRadius: 'var(--radius-sm)',
                }}
              >
                {cancelError}
              </div>
            )}

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.75rem' }}>
              <button
                className="btn btn-secondary"
                onClick={() => setCancellingClaim(null)}
                disabled={cancelling}
              >
                Keep Claim
              </button>
              <button
                className="btn btn-primary"
                style={{ background: 'var(--danger)', borderColor: 'var(--danger)' }}
                onClick={handleConfirmCancel}
                disabled={cancelling}
              >
                {cancelling ? 'Cancelling...' : 'Confirm Cancel'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
