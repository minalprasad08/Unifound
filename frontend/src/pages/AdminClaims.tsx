import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { claimApi } from '../services/api';
import { Claim, ClaimStatus } from '../types/auth';
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  AlertCircle,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  User as UserIcon,
  Phone,
  Mail,
  GraduationCap,
  X,
  Filter,
} from 'lucide-react';

export const AdminClaims: React.FC = () => {
  const [claims, setClaims] = useState<Claim[]>([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(15);
  const [statusFilter, setStatusFilter] = useState<ClaimStatus | ''>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Review Modal State
  const [reviewingClaim, setReviewingClaim] = useState<Claim | null>(null);
  const [reviewAction, setReviewAction] = useState<'APPROVE' | 'REJECT' | null>(null);
  const [adminNotes, setAdminNotes] = useState('');
  const [submittingReview, setSubmittingReview] = useState(false);
  const [reviewError, setReviewError] = useState<string | null>(null);

  const fetchClaims = async (targetPage = page) => {
    try {
      setLoading(true);
      setError(null);
      const data = await claimApi.getAdminClaims({
        status: statusFilter || undefined,
        page: targetPage,
        page_size: pageSize,
      });
      setClaims(data.claims);
      setTotal(data.total);
      setTotalPages(data.total_pages);
      setPage(data.page);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load claims queue.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClaims(1);
  }, [statusFilter]);

  const handleOpenReview = (claim: Claim, action: 'APPROVE' | 'REJECT') => {
    setReviewingClaim(claim);
    setReviewAction(action);
    setAdminNotes('');
    setReviewError(null);
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reviewingClaim || !reviewAction) return;

    try {
      setSubmittingReview(true);
      setReviewError(null);
      if (reviewAction === 'APPROVE') {
        await claimApi.approveClaim(reviewingClaim.id, {
          admin_notes: adminNotes.trim() || undefined,
        });
      } else {
        await claimApi.rejectClaim(reviewingClaim.id, {
          admin_notes: adminNotes.trim() || undefined,
        });
      }
      setReviewingClaim(null);
      setReviewAction(null);
      await fetchClaims(page);
    } catch (err: any) {
      setReviewError(err.response?.data?.detail || 'Failed to submit review decision.');
    } finally {
      setSubmittingReview(false);
    }
  };

  const getStatusBadge = (status: ClaimStatus) => {
    switch (status) {
      case 'PENDING':
        return <span className="badge badge-warning">PENDING REVIEW</span>;
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

  return (
    <div className="container animate-fade-in" style={{ paddingTop: '2rem', maxWidth: '1200px' }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.4rem' }}>
          <span className="badge badge-primary">ADMINISTRATION PORTAL</span>
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Security & Lost Property Claims</span>
        </div>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800 }}>Claims Management Queue</h1>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
          Verify student and staff ownership claims, inspect submitted evidence, and approve item release.
        </p>
      </div>

      {/* Filter Toolbar */}
      <div
        className="glass-card"
        style={{
          padding: '1rem 1.25rem',
          marginBottom: '1.75rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
          <Filter style={{ width: '1rem', height: '1rem', color: 'var(--text-muted)' }} />
          <span style={{ fontSize: '0.88rem', fontWeight: 600 }}>Filter by Status:</span>
          {(['', 'PENDING', 'APPROVED', 'REJECTED', 'CANCELLED'] as const).map((statusVal) => (
            <button
              key={statusVal}
              className={`btn btn-sm ${statusFilter === statusVal ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setStatusFilter(statusVal as any)}
              style={{ fontSize: '0.82rem' }}
            >
              {statusVal === '' ? 'All Claims' : statusVal}
            </button>
          ))}
        </div>

        <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
          Total claims recorded: <strong>{total}</strong>
        </div>
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
          Loading claims queue...
        </div>
      ) : claims.length === 0 ? (
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
            <ShieldAlert style={{ width: '2rem', height: '2rem' }} />
          </div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>No claims match your filter</h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '400px', marginTop: '0.5rem', fontSize: '0.9rem' }}>
            {statusFilter
              ? `There are no claims currently marked as ${statusFilter}.`
              : 'No claims have been submitted yet.'}
          </p>
        </div>
      ) : (
        /* Claims Queue Grid */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '2.5rem' }}>
          {claims.map((claim) => (
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
              {/* Header row */}
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
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                    {getStatusBadge(claim.status)}
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Claim #{claim.id} &bull; Received {new Date(claim.created_at).toLocaleString()}
                    </span>
                  </div>
                  <h3 style={{ fontSize: '1.3rem', fontWeight: 700 }}>
                    {claim.item ? claim.item.title : `Item #${claim.item_id}`}
                  </h3>
                </div>

                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  {claim.item && (
                    <Link
                      to={`/items/${claim.item.id}`}
                      className="btn btn-secondary btn-sm"
                      style={{ fontSize: '0.82rem' }}
                    >
                      <ExternalLink style={{ width: '0.85rem', height: '0.85rem', marginRight: '0.35rem' }} />
                      View Item Details
                    </Link>
                  )}
                </div>
              </div>

              {/* Two Column details: Claimant & Evidence */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
                {/* Claimant Info Card */}
                {claim.claimant && (
                  <div
                    style={{
                      background: 'var(--bg-glass)',
                      padding: '1rem 1.25rem',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--border-color)',
                      fontSize: '0.85rem',
                    }}
                  >
                    <div style={{ fontWeight: 700, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <UserIcon style={{ width: '0.95rem', height: '0.95rem', color: 'var(--primary)' }} />
                      <span>Claimant Information</span>
                    </div>
                    <div style={{ fontWeight: 600, fontSize: '0.95rem' }}>{claim.claimant.full_name}</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', marginTop: '0.4rem', color: 'var(--text-secondary)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Mail style={{ width: '0.85rem', height: '0.85rem' }} />
                        <span>{claim.claimant.email}</span>
                      </div>
                      {claim.claimant.phone && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <Phone style={{ width: '0.85rem', height: '0.85rem' }} />
                          <span>{claim.claimant.phone}</span>
                        </div>
                      )}
                      {claim.claimant.student_id && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                          <GraduationCap style={{ width: '0.85rem', height: '0.85rem' }} />
                          <span>Student ID: {claim.claimant.student_id}</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Evidence & Description Card */}
                <div
                  style={{
                    background: 'var(--bg-glass)',
                    padding: '1rem 1.25rem',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-color)',
                  }}
                >
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                    Claimant Description
                  </div>
                  <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.5, marginBottom: '0.75rem' }}>
                    {claim.description}
                  </p>

                  {claim.evidence && (
                    <>
                      <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                        Submitted Proof / Evidence
                      </div>
                      <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                        {claim.evidence}
                      </p>
                    </>
                  )}
                </div>
              </div>

              {/* Decision Notes if already reviewed */}
              {claim.admin_notes && (
                <div
                  style={{
                    padding: '0.85rem 1rem',
                    borderRadius: 'var(--radius-md)',
                    background: claim.status === 'APPROVED' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(244, 63, 94, 0.08)',
                    border: `1px solid ${claim.status === 'APPROVED' ? 'rgba(16, 185, 129, 0.25)' : 'rgba(244, 63, 94, 0.25)'}`,
                    fontSize: '0.88rem',
                  }}
                >
                  <span style={{ fontWeight: 700, color: claim.status === 'APPROVED' ? 'var(--success)' : 'var(--danger)' }}>
                    Admin Review Note:
                  </span>{' '}
                  {claim.admin_notes}
                  {claim.reviewed_at && (
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginLeft: '0.5rem' }}>
                      (Reviewed {new Date(claim.reviewed_at).toLocaleDateString()})
                    </span>
                  )}
                </div>
              )}

              {/* Action Buttons for Pending Claims */}
              {claim.status === 'PENDING' && (
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'flex-end',
                    gap: '0.75rem',
                    paddingTop: '0.75rem',
                    borderTop: '1px solid var(--border-color)',
                  }}
                >
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    style={{ color: 'var(--danger)', borderColor: 'var(--danger)' }}
                    onClick={() => handleOpenReview(claim, 'REJECT')}
                  >
                    <XCircle style={{ width: '0.9rem', height: '0.9rem', marginRight: '0.35rem' }} />
                    Reject Claim
                  </button>

                  <button
                    type="button"
                    className="btn btn-primary btn-sm"
                    style={{ background: 'var(--success)', borderColor: 'var(--success)' }}
                    onClick={() => handleOpenReview(claim, 'APPROVE')}
                  >
                    <CheckCircle2 style={{ width: '0.9rem', height: '0.9rem', marginRight: '0.35rem' }} />
                    Approve Claim & Release
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Pagination Bar */}
      {totalPages > 1 && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            marginBottom: '3rem',
          }}
        >
          <button
            className="btn btn-secondary btn-sm"
            disabled={page <= 1 || loading}
            onClick={() => fetchClaims(page - 1)}
          >
            <ChevronLeft style={{ width: '1rem', height: '1rem', marginRight: '0.25rem' }} />
            Previous
          </button>

          <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            Page <strong>{page}</strong> of <strong>{totalPages}</strong>
          </span>

          <button
            className="btn btn-secondary btn-sm"
            disabled={page >= totalPages || loading}
            onClick={() => fetchClaims(page + 1)}
          >
            Next
            <ChevronRight style={{ width: '1rem', height: '1rem', marginLeft: '0.25rem' }} />
          </button>
        </div>
      )}

      {/* Approve / Reject Review Modal */}
      {reviewingClaim && reviewAction && (
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
          <div className="glass-card animate-fade-in" style={{ maxWidth: '500px', width: '100%', padding: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1.35rem', fontWeight: 800 }}>
                {reviewAction === 'APPROVE' ? 'Approve Ownership Claim' : 'Reject Ownership Claim'}
              </h3>
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                onClick={() => setReviewingClaim(null)}
                style={{ padding: '0.25rem', borderRadius: '50%' }}
              >
                <X style={{ width: '1.25rem', height: '1.25rem' }} />
              </button>
            </div>

            <form onSubmit={handleSubmitReview}>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem' }}>
                {reviewAction === 'APPROVE'
                  ? `Confirm approving claim #${reviewingClaim.id} for "${reviewingClaim.item?.title || 'item'}". The item status will automatically change to CLAIMED.`
                  : `Are you sure you want to reject claim #${reviewingClaim.id}? The claimant will receive a notification with your reasoning.`}
              </p>

              {reviewError && (
                <div
                  className="glass-card"
                  style={{
                    padding: '0.75rem',
                    marginBottom: '1rem',
                    background: 'var(--danger-bg)',
                    borderColor: 'var(--danger)',
                    color: 'var(--danger)',
                    fontSize: '0.85rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                  }}
                >
                  <AlertCircle style={{ width: '1rem', height: '1rem', flexShrink: 0 }} />
                  <span>{reviewError}</span>
                </div>
              )}

              <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                <label className="form-label" style={{ fontSize: '0.85rem' }}>
                  Administrative Notes / Feedback for Claimant
                </label>
                <textarea
                  className="input-field"
                  rows={3}
                  placeholder={
                    reviewAction === 'APPROVE'
                      ? 'e.g. Identity verified via Student ID card; serial number matched.'
                      : 'e.g. Evidence does not match reported item specs.'
                  }
                  value={adminNotes}
                  onChange={(e) => setAdminNotes(e.target.value)}
                  style={{ fontSize: '0.9rem' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setReviewingClaim(null)}
                  disabled={submittingReview}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  style={{
                    background: reviewAction === 'APPROVE' ? 'var(--success)' : 'var(--danger)',
                    borderColor: reviewAction === 'APPROVE' ? 'var(--success)' : 'var(--danger)',
                  }}
                  disabled={submittingReview}
                >
                  {submittingReview
                    ? 'Processing...'
                    : reviewAction === 'APPROVE'
                    ? 'Confirm Approval'
                    : 'Confirm Rejection'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
