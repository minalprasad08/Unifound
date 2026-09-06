import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { itemApi, claimApi, matchApi } from '../services/api';
import { Item, ItemMatchCandidate } from '../types/auth';
import {
  ArrowLeft,
  Calendar,
  MapPin,
  Tag,
  AlertCircle,
  Edit,
  Trash2,
  Clock,
  ShieldCheck,
  FileCheck,
  CheckCircle2,
  X,
  Sparkles,
  ExternalLink,
  Cpu,
  Camera,
} from 'lucide-react';

export const ItemDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [item, setItem] = useState<Item | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // AI Potential matches state
  const [matches, setMatches] = useState<ItemMatchCandidate[]>([]);
  const [loadingMatches, setLoadingMatches] = useState(false);

  // Close modal
  const [showCloseModal, setShowCloseModal] = useState(false);
  const [closing, setClosing] = useState(false);

  // Image analysis state
  const [analyzingImage, setAnalyzingImage] = useState(false);
  const [imageAnalysisError, setImageAnalysisError] = useState<string | null>(null);

  const handleAnalyzeImage = async () => {
    if (!item) return;
    try {
      setAnalyzingImage(true);
      setImageAnalysisError(null);
      const res = await itemApi.analyzeImage(item.id);
      setItem((prev) => (prev ? { ...prev, image_analysis: res.image_analysis } : null));
      fetchMatches(item.id);
    } catch (err: any) {
      setImageAnalysisError(err.response?.data?.detail || 'Image analysis could not be completed.');
    } finally {
      setAnalyzingImage(false);
    }
  };

  const fetchMatches = async (itemId: number) => {
    try {
      setLoadingMatches(true);
      const resp = await matchApi.getItemMatches(itemId);
      setMatches(resp.matches);
    } catch (err) {
      console.error('Failed to load AI matches', err);
    } finally {
      setLoadingMatches(false);
    }
  };

  const fetchItem = async () => {
    if (!id) return;
    try {
      setLoading(true);
      setError(null);
      const data = await itemApi.getItem(Number(id));
      setItem(data);
      // Fetch AI matches for this item
      fetchMatches(data.id);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Item report not found or inaccessible.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItem();
  }, [id]);

  const handleClose = async () => {
    if (!item) return;
    try {
      setClosing(true);
      await itemApi.closeItem(item.id);
      setShowCloseModal(false);
      await fetchItem();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to close item.');
    } finally {
      setClosing(false);
    }
  };

  // Claim modal state
  const [showClaimModal, setShowClaimModal] = useState(false);
  const [claimDescription, setClaimDescription] = useState('');
  const [claimEvidence, setClaimEvidence] = useState('');
  const [submittingClaim, setSubmittingClaim] = useState(false);
  const [claimSuccess, setClaimSuccess] = useState<string | null>(null);
  const [claimError, setClaimError] = useState<string | null>(null);

  const handleClaimSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!item) return;
    if (claimDescription.trim().length < 10) {
      setClaimError('Description must be at least 10 characters detailing your ownership.');
      return;
    }

    try {
      setSubmittingClaim(true);
      setClaimError(null);
      await claimApi.submitClaim({
        item_id: item.id,
        description: claimDescription.trim(),
        evidence: claimEvidence.trim() || undefined,
      });
      setClaimSuccess('Claim submitted successfully! Campus security and the reporter have been notified.');
      setClaimDescription('');
      setClaimEvidence('');
      await fetchItem();
    } catch (err: any) {
      setClaimError(err.response?.data?.detail || 'Failed to submit ownership claim.');
    } finally {
      setSubmittingClaim(false);
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ paddingTop: '5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <div className="spinner" style={{ margin: '0 auto 1rem' }} />
        Loading item details...
      </div>
    );
  }

  if (error || !item) {
    return (
      <div className="container" style={{ paddingTop: '4rem', maxWidth: '600px' }}>
        <div className="glass-card" style={{ padding: '2.5rem', textAlign: 'center' }}>
          <AlertCircle style={{ width: '3rem', height: '3rem', color: 'var(--danger)', margin: '0 auto 1rem' }} />
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Item Not Found</h2>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem' }}>{error || 'Unable to load this item report.'}</p>
          <button className="btn btn-primary" style={{ marginTop: '1.5rem' }} onClick={() => navigate('/my-reports')}>
            Back to My Reports
          </button>
        </div>
      </div>
    );
  }

  const isOwner = user?.id === item.reported_by;
  const isAdmin = user?.role === 'ADMIN';
  const canManage = isOwner || isAdmin;

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
    <div className="container animate-fade-in" style={{ paddingTop: '2rem', maxWidth: '900px' }}>
      {/* Back Button */}
      <button
        type="button"
        className="btn btn-ghost"
        style={{ marginBottom: '1.5rem', paddingLeft: 0 }}
        onClick={() => navigate(-1)}
      >
        <ArrowLeft style={{ width: '1rem', height: '1rem', marginRight: '0.5rem' }} />
        Back
      </button>

      <div className="glass-card" style={{ padding: '2.5rem', overflow: 'hidden' }}>
        {/* Top Header */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            gap: '1rem',
            marginBottom: '1.75rem',
            borderBottom: '1px solid var(--border-color)',
            paddingBottom: '1.5rem',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', marginBottom: '0.65rem' }}>
              <span
                className="badge"
                style={{
                  background: item.item_type === 'LOST' ? 'rgba(244, 63, 94, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                  color: item.item_type === 'LOST' ? 'var(--danger)' : 'var(--success)',
                  borderColor: item.item_type === 'LOST' ? 'rgba(244, 63, 94, 0.3)' : 'rgba(16, 185, 129, 0.3)',
                }}
              >
                {item.item_type} REPORT #{item.id}
              </span>
              {getStatusBadge(item.status)}
            </div>
            <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>{item.title}</h1>
          </div>

          {canManage && item.status !== 'CLOSED' && (
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <Link to={`/items/${item.id}/edit`} className="btn btn-secondary">
                <Edit style={{ width: '0.9rem', height: '0.9rem', marginRight: '0.4rem' }} />
                Edit Report
              </Link>
              <button
                type="button"
                className="btn btn-ghost"
                style={{ color: 'var(--danger)' }}
                onClick={() => setShowCloseModal(true)}
              >
                <Trash2 style={{ width: '0.9rem', height: '0.9rem', marginRight: '0.4rem' }} />
                Close Report
              </button>
            </div>
          )}

          {!canManage && user && user.id !== item.reported_by && item.status !== 'CLOSED' && item.status !== 'CLAIMED' && item.status !== 'RESOLVED' && (
            <div>
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => {
                  setShowClaimModal(true);
                  setClaimError(null);
                  setClaimSuccess(null);
                }}
              >
                <FileCheck style={{ width: '0.9rem', height: '0.9rem', marginRight: '0.4rem' }} />
                Claim This Item
              </button>
            </div>
          )}
        </div>

        {/* Content Body: Image + Details */}
        <div style={{ display: 'grid', gridTemplateColumns: item.image_url ? 'minmax(280px, 340px) 1fr' : '1fr', gap: '2rem' }}>
          {item.image_url && (
            <div
              style={{
                borderRadius: 'var(--radius-lg)',
                overflow: 'hidden',
                border: '1px solid var(--border-color)',
                height: '320px',
                background: '#000',
              }}
            >
              <img
                src={item.image_url}
                alt={item.title}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            </div>
          )}

          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.75rem' }}>Description</h3>
            <p
              style={{
                color: 'var(--text-secondary)',
                fontSize: '0.95rem',
                lineHeight: 1.65,
                whiteSpace: 'pre-wrap',
                marginBottom: '1.75rem',
              }}
            >
              {item.description}
            </p>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                gap: '1.25rem',
                background: 'var(--bg-glass)',
                padding: '1.25rem',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-color)',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  <Tag style={{ width: '0.85rem', height: '0.85rem' }} />
                  Category
                </div>
                <div style={{ fontWeight: 600, marginTop: '0.25rem', fontSize: '0.92rem' }}>{item.category}</div>
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  <MapPin style={{ width: '0.85rem', height: '0.85rem' }} />
                  Location
                </div>
                <div style={{ fontWeight: 600, marginTop: '0.25rem', fontSize: '0.92rem' }}>{item.location}</div>
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  <Calendar style={{ width: '0.85rem', height: '0.85rem' }} />
                  Incident Date
                </div>
                <div style={{ fontWeight: 600, marginTop: '0.25rem', fontSize: '0.92rem' }}>
                  {new Date(item.incident_date).toLocaleString()}
                </div>
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                  <Clock style={{ width: '0.85rem', height: '0.85rem' }} />
                  Reported On
                </div>
                <div style={{ fontWeight: 600, marginTop: '0.25rem', fontSize: '0.92rem' }}>
                  {new Date(item.created_at).toLocaleDateString()}
                </div>
              </div>
            </div>

            {/* Reporter Information */}
            {item.reporter && (
              <div
                style={{
                  marginTop: '1.5rem',
                  padding: '1.25rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(99, 102, 241, 0.06)',
                  border: '1px solid rgba(99, 102, 241, 0.2)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  <ShieldCheck style={{ width: '1rem', height: '1rem', color: 'var(--primary)' }} />
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--primary)' }}>Reported By</span>
                </div>
                <div style={{ fontSize: '0.95rem', fontWeight: 700 }}>{item.reporter.full_name}</div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                  {item.reporter.email} {item.reporter.department ? `• ${item.reporter.department}` : ''}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Image Analysis Section */}
      {item.image_url && (
        <div
          className="glass-card animate-fade-in"
          style={{
            marginTop: '2rem',
            padding: '2rem',
            borderTop: '4px solid #38bdf8',
          }}
        >
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '1rem',
              marginBottom: '1.5rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
              <div
                style={{
                  width: '3rem',
                  height: '3rem',
                  borderRadius: 'var(--radius-md)',
                  background: 'linear-gradient(135deg, #0284c7 0%, #38bdf8 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 15px rgba(56, 189, 248, 0.35)',
                }}
              >
                <Camera style={{ width: '1.6rem', height: '1.6rem', color: '#ffffff' }} />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <h2 style={{ fontSize: '1.35rem', fontWeight: 800 }}>🤖 AI Image Analysis</h2>
                  {item.image_analysis && (
                    <span className="badge badge-info">
                      {item.image_analysis.analyzer || 'local-vision-v1'}
                    </span>
                  )}
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginTop: '0.2rem' }}>
                  Automated computer vision feature extraction for color clustering, brand detection, and visual traits.
                </p>
              </div>
            </div>

            {canManage && (
              <button
                onClick={handleAnalyzeImage}
                disabled={analyzingImage}
                className="btn btn-secondary btn-sm"
                style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
              >
                <Sparkles style={{ width: '0.9rem', height: '0.9rem', color: '#38bdf8' }} />
                {analyzingImage ? 'Analyzing Image...' : item.image_analysis ? 'Re-analyze Image' : 'Analyze Image'}
              </button>
            )}
          </div>

          {imageAnalysisError && (
            <div
              style={{
                padding: '0.85rem 1rem',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                color: 'var(--danger)',
                fontSize: '0.88rem',
                marginBottom: '1.25rem',
              }}
            >
              {imageAnalysisError}
            </div>
          )}

          {analyzingImage ? (
            <div style={{ textAlign: 'center', padding: '2.5rem', color: 'var(--text-secondary)' }}>
              <div className="spinner" style={{ margin: '0 auto 0.85rem' }} />
              Extracting color palette, form factors, and brand markings from image...
            </div>
          ) : item.image_analysis ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
                  gap: '1rem',
                  background: 'var(--surface)',
                  padding: '1.5rem',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Item Type
                  </div>
                  <div style={{ fontWeight: 700, fontSize: '1rem', marginTop: '0.25rem', textTransform: 'capitalize' }}>
                    {item.image_analysis.item_type || 'Unspecified'}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Brand / Manufacturer
                  </div>
                  <div style={{ fontWeight: 700, fontSize: '1rem', marginTop: '0.25rem' }}>
                    {item.image_analysis.brand || 'None visible'}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Dominant Colors
                  </div>
                  <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.35rem' }}>
                    {item.image_analysis.colors && item.image_analysis.colors.length > 0 ? (
                      item.image_analysis.colors.map((c) => (
                        <span
                          key={c}
                          className="badge"
                          style={{ textTransform: 'capitalize', fontSize: '0.75rem' }}
                        >
                          {c}
                        </span>
                      ))
                    ) : (
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>None</span>
                    )}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Visible Text
                  </div>
                  <div style={{ fontWeight: 600, fontSize: '0.92rem', marginTop: '0.25rem' }}>
                    {item.image_analysis.visible_text && item.image_analysis.visible_text.length > 0
                      ? item.image_analysis.visible_text.join(', ')
                      : 'None detected'}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Visual Confidence
                  </div>
                  <div style={{ fontWeight: 800, fontSize: '1.15rem', color: '#38bdf8', marginTop: '0.2rem' }}>
                    {Math.round(item.image_analysis.confidence * 100)}%
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Analyzed On
                  </div>
                  <div style={{ fontSize: '0.85rem', marginTop: '0.25rem', color: 'var(--text-secondary)' }}>
                    {new Date(item.image_analysis.analyzed_at).toLocaleString()}
                  </div>
                </div>
              </div>

              {item.image_analysis.characteristics && item.image_analysis.characteristics.length > 0 && (
                <div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                    Recognized Visual Traits:
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    {item.image_analysis.characteristics.map((ch, idx) => (
                      <span key={idx} className="badge badge-info" style={{ fontSize: '0.78rem' }}>
                        ✓ {ch}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem', background: 'var(--surface)', borderRadius: 'var(--radius-md)' }}>
              <Camera style={{ width: '2.2rem', height: '2.2rem', color: 'var(--text-muted)', margin: '0 auto 0.5rem' }} />
              <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Visual Analysis Pending</div>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '0.25rem' }}>
                This item report contains an uploaded image that has not yet been processed. Click <strong>Analyze Image</strong> above to extract visual attributes.
              </p>
            </div>
          )}
        </div>
      )}

      {/* AI Potential Matches Section */}
      <div className="glass-card animate-fade-in" style={{ padding: '2rem', marginTop: '2rem', borderTop: '4px solid var(--primary)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <div
              style={{
                width: '3rem',
                height: '3rem',
                borderRadius: 'var(--radius-md)',
                background: 'var(--primary-gradient)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 15px rgba(99, 102, 241, 0.4)',
              }}
            >
              <Cpu style={{ width: '1.6rem', height: '1.6rem', color: '#ffffff' }} />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>AI Potential Matches</h2>
                <span className="badge badge-primary">
                  {matches.length} {matches.length === 1 ? 'Candidate' : 'Candidates'}
                </span>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginTop: '0.2rem' }}>
                Explainable multi-factor similarity matching between opposite-type reports ({item.item_type === 'LOST' ? 'LOST ↔ FOUND' : 'FOUND ↔ LOST'}).
              </p>
            </div>
          </div>

          <button
            onClick={() => fetchMatches(item.id)}
            disabled={loadingMatches}
            className="btn btn-secondary btn-sm"
          >
            <Sparkles style={{ width: '0.9rem', height: '0.9rem' }} />
            {loadingMatches ? 'Scanning...' : 'Re-scan Matches'}
          </button>
        </div>

        {loadingMatches ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
            <div className="spinner" style={{ margin: '0 auto 1rem' }} />
            Analyzing candidate reports with AI similarity engine...
          </div>
        ) : matches.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem 1.5rem', background: 'var(--surface)', borderRadius: 'var(--radius-md)' }}>
            <Sparkles style={{ width: '2.5rem', height: '2.5rem', color: 'var(--text-muted)', margin: '0 auto 0.75rem' }} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>No high-confidence matches found yet</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', maxWidth: '480px', margin: '0.35rem auto 0' }}>
              The matching engine scans across active {item.item_type === 'LOST' ? 'FOUND' : 'LOST'} reports. As soon as a corresponding report is submitted, it will be ranked here.
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {matches.map((cand) => {
              const getConfidenceLevel = (score: number) => {
                if (score >= 80) return { label: 'Very Strong Match', badgeClass: 'badge-success', color: 'var(--success)' };
                if (score >= 60) return { label: 'Strong Match', badgeClass: 'badge-info', color: '#38bdf8' };
                if (score >= 40) return { label: 'Possible Match', badgeClass: 'badge-warning', color: '#f59e0b' };
                return { label: 'Low Match', badgeClass: '', color: 'var(--text-muted)' };
              };
              const level = getConfidenceLevel(cand.confidence);

              return (
                <div
                  key={cand.item.id}
                  style={{
                    padding: '1.5rem',
                    background: 'var(--surface)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--border-subtle)',
                    borderLeft: `4px solid ${level.color}`,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '1rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.35rem' }}>
                        <span className={`badge ${level.badgeClass}`}>
                          {cand.confidence}% • {level.label}
                        </span>
                        {cand.visual_score != null && (
                          <span className="badge badge-info" style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                            <Camera style={{ width: '0.75rem', height: '0.75rem' }} />
                            Visual: {Math.round(cand.visual_score * 100)}%
                          </span>
                        )}
                        <span className={`badge ${cand.item.item_type === 'LOST' ? 'badge-danger' : 'badge-success'}`}>
                          {cand.item.item_type}
                        </span>
                        <span className="badge">{cand.item.category}</span>
                      </div>
                      <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                        {cand.item.title}
                      </h3>
                      <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.35rem', lineHeight: 1.5 }}>
                        {cand.item.description}
                      </p>
                    </div>

                    <Link
                      to={`/items/${cand.item.id}`}
                      className="btn btn-primary btn-sm"
                      style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexShrink: 0 }}
                    >
                      <span>View Item</span>
                      <ExternalLink style={{ width: '0.85rem', height: '0.85rem' }} />
                    </Link>
                  </div>

                  {/* Metadata line */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)', flexWrap: 'wrap' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <MapPin style={{ width: '0.8rem', height: '0.8rem' }} />
                      <span>{cand.item.location}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <Calendar style={{ width: '0.8rem', height: '0.8rem' }} />
                      <span>{new Date(cand.item.incident_date).toLocaleDateString()}</span>
                    </div>
                  </div>

                  {/* Similarity Breakdown Bars */}
                  <div
                    style={{
                      background: 'rgba(0,0,0,0.2)',
                      padding: '1rem',
                      borderRadius: 'var(--radius-sm)',
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
                      gap: '0.75rem',
                      fontSize: '0.78rem',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
                        <span>Description</span>
                        <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                          {Math.round(cand.description_score * 100)}%
                        </span>
                      </div>
                      <div style={{ height: '4px', background: 'var(--border-subtle)', borderRadius: '2px', marginTop: '0.3rem', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${cand.description_score * 100}%`, background: 'var(--primary)' }} />
                      </div>
                    </div>

                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
                        <span>Title</span>
                        <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                          {Math.round(cand.title_score * 100)}%
                        </span>
                      </div>
                      <div style={{ height: '4px', background: 'var(--border-subtle)', borderRadius: '2px', marginTop: '0.3rem', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${cand.title_score * 100}%`, background: '#818cf8' }} />
                      </div>
                    </div>

                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
                        <span>Category</span>
                        <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                          {Math.round(cand.category_score * 100)}%
                        </span>
                      </div>
                      <div style={{ height: '4px', background: 'var(--border-subtle)', borderRadius: '2px', marginTop: '0.3rem', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${cand.category_score * 100}%`, background: 'var(--success)' }} />
                      </div>
                    </div>

                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
                        <span>Location</span>
                        <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                          {Math.round(cand.location_score * 100)}%
                        </span>
                      </div>
                      <div style={{ height: '4px', background: 'var(--border-subtle)', borderRadius: '2px', marginTop: '0.3rem', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${cand.location_score * 100}%`, background: '#f59e0b' }} />
                      </div>
                    </div>

                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)' }}>
                        <span>Date Proximity</span>
                        <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                          {Math.round(cand.date_score * 100)}%
                        </span>
                      </div>
                      <div style={{ height: '4px', background: 'var(--border-subtle)', borderRadius: '2px', marginTop: '0.3rem', overflow: 'hidden' }}>
                        <div style={{ height: '100%', width: `${cand.date_score * 100}%`, background: '#ec4899' }} />
                      </div>
                    </div>
                  </div>

                  {/* Visual Evidence Section */}
                  {cand.visual_evidence && cand.visual_evidence.length > 0 && (
                    <div
                      style={{
                        background: 'rgba(56, 189, 248, 0.06)',
                        border: '1px solid rgba(56, 189, 248, 0.25)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '0.65rem 0.85rem',
                      }}
                    >
                      <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38bdf8', marginBottom: '0.25rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                        Visual Evidence
                      </div>
                      <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', fontSize: '0.78rem' }}>
                        {cand.visual_evidence.map((ev, i) => (
                          <span key={i} style={{ color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                            <span style={{ color: 'var(--success)', fontWeight: 700 }}>✓</span>
                            {ev}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Natural Language Explanation */}
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontStyle: 'italic', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Sparkles style={{ width: '0.9rem', height: '0.9rem', color: 'var(--primary)' }} />
                    <span>{cand.explanation}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Close Confirmation Modal */}
      {showCloseModal && (
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
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>Close Report</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.5rem' }}>
              Are you sure you want to mark this item as CLOSED? This status change indicates the report is no longer active.
            </p>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.75rem' }}>
              <button className="btn btn-secondary" onClick={() => setShowCloseModal(false)} disabled={closing}>
                Cancel
              </button>
              <button
                className="btn btn-primary"
                style={{ background: 'var(--danger)', borderColor: 'var(--danger)' }}
                onClick={handleClose}
                disabled={closing}
              >
                {closing ? 'Closing...' : 'Confirm Close'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Claim Submission Modal */}
      {showClaimModal && (
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
          <div className="glass-card animate-fade-in" style={{ maxWidth: '520px', width: '100%', padding: '2rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1.35rem', fontWeight: 800 }}>Submit Ownership Claim</h3>
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                onClick={() => setShowClaimModal(false)}
                style={{ padding: '0.25rem', borderRadius: '50%' }}
              >
                <X style={{ width: '1.25rem', height: '1.25rem' }} />
              </button>
            </div>

            {claimSuccess ? (
              <div style={{ textAlign: 'center', padding: '1.5rem 0' }}>
                <CheckCircle2 style={{ width: '3rem', height: '3rem', color: 'var(--success)', margin: '0 auto 1rem' }} />
                <h4 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem' }}>Claim Received!</h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                  {claimSuccess}
                </p>
                <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
                  <button className="btn btn-secondary" onClick={() => setShowClaimModal(false)}>
                    Close
                  </button>
                  <Link to="/my-claims" className="btn btn-primary">
                    View in My Claims
                  </Link>
                </div>
              </div>
            ) : (
              <form onSubmit={handleClaimSubmit}>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', marginBottom: '1.25rem' }}>
                  Please provide proof of ownership for <strong>"{item.title}"</strong>. Campus administration will review your evidence before approving release.
                </p>

                {claimError && (
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
                    <span>{claimError}</span>
                  </div>
                )}

                <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                  <label className="form-label" style={{ fontSize: '0.85rem' }}>
                    Ownership Description <span style={{ color: 'var(--danger)' }}>*</span>
                  </label>
                  <textarea
                    className="input-field"
                    rows={3}
                    placeholder="Describe how, where, or when you lost this item, along with any distinguishing characteristics..."
                    value={claimDescription}
                    onChange={(e) => setClaimDescription(e.target.value)}
                    required
                    style={{ fontSize: '0.9rem' }}
                  />
                  <small style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>Minimum 10 characters.</small>
                </div>

                <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                  <label className="form-label" style={{ fontSize: '0.85rem' }}>
                    Proof / Evidence (Optional)
                  </label>
                  <textarea
                    className="input-field"
                    rows={2}
                    placeholder="e.g. Serial numbers, device password/passcode hint, receipt number, or stickers..."
                    value={claimEvidence}
                    onChange={(e) => setClaimEvidence(e.target.value)}
                    style={{ fontSize: '0.9rem' }}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShowClaimModal(false)}
                    disabled={submittingClaim}
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary" disabled={submittingClaim}>
                    {submittingClaim ? 'Submitting Claim...' : 'Submit Claim'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
