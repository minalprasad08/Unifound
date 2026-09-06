import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { itemApi } from '../services/api';
import {
  ArrowLeft,
  Upload,
  AlertCircle,
  CheckCircle2,
  Calendar,
  MapPin,
  Tag,
  FileText,
  X,
  Save,
} from 'lucide-react';

const CATEGORIES = [
  'Electronics & Gadgets',
  'Wallets, Purses & IDs',
  'Keys & Keychains',
  'Bags & Backpacks',
  'Books, Notes & Stationery',
  'Clothing & Apparel',
  'Jewelry & Watches',
  'Eyewear',
  'Sports & Gym Equipment',
  'Other Campus Items',
];

export const EditItem: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [title, setTitle] = useState('');
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [location, setLocation] = useState('');
  const [incidentDate, setIncidentDate] = useState('');
  const [description, setDescription] = useState('');
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    const fetchItem = async () => {
      if (!id) return;
      try {
        setLoading(true);
        setError(null);
        const item = await itemApi.getItem(Number(id));

        // Check ownership or admin
        if (item.reported_by !== user?.id && user?.role !== 'ADMIN') {
          setError('You do not have permission to edit this report.');
          return;
        }

        setTitle(item.title);
        setCategory(item.category);
        setLocation(item.location);
        setDescription(item.description);
        setImageUrl(item.image_url || null);
        setPreviewUrl(item.image_url || null);

        // Format incident_date for datetime-local input
        const dateObj = new Date(item.incident_date);
        dateObj.setMinutes(dateObj.getMinutes() - dateObj.getTimezoneOffset());
        setIncidentDate(dateObj.toISOString().slice(0, 16));
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load item report.');
      } finally {
        setLoading(false);
      }
    };

    fetchItem();
  }, [id, user]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      setError('Selected image exceeds 5MB size limit.');
      return;
    }

    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Please select a valid image file (.jpg, .jpeg, .png, .webp).');
      return;
    }

    setError(null);
    setUploadingImage(true);

    const localPreview = URL.createObjectURL(file);
    setPreviewUrl(localPreview);

    try {
      const response = await itemApi.uploadImage(file);
      setImageUrl(response.image_url);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload image.');
      setPreviewUrl(imageUrl);
    } finally {
      setUploadingImage(false);
    }
  };

  const removeImage = () => {
    setImageUrl(null);
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;
    setError(null);
    setSuccess(null);

    if (title.trim().length < 2) {
      setError('Title must be at least 2 characters.');
      return;
    }

    if (description.trim().length < 5) {
      setError('Description must be at least 5 characters.');
      return;
    }

    setSubmitting(true);

    try {
      await itemApi.updateItem(Number(id), {
        title: title.trim(),
        category,
        location: location.trim(),
        incident_date: new Date(incidentDate).toISOString(),
        description: description.trim(),
        image_url: imageUrl,
      });

      setSuccess('Item report successfully updated!');
      setTimeout(() => {
        navigate(`/items/${id}`);
      }, 1000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update report.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ paddingTop: '5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
        <div className="spinner" style={{ margin: '0 auto 1rem' }} />
        Loading report details...
      </div>
    );
  }

  return (
    <div className="container animate-fade-in" style={{ paddingTop: '2rem', maxWidth: '820px' }}>
      <button
        type="button"
        className="btn btn-ghost"
        style={{ marginBottom: '1.5rem', paddingLeft: 0 }}
        onClick={() => navigate(-1)}
      >
        <ArrowLeft style={{ width: '1rem', height: '1rem', marginRight: '0.5rem' }} />
        Back to Details
      </button>

      <div className="glass-card" style={{ padding: '2.5rem' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: 800, marginBottom: '0.35rem' }}>Edit Item Report</h1>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          Update the incident details or attach a clearer photograph to help locate this item.
        </p>

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
            <AlertCircle style={{ width: '1.25rem', height: '1.25rem', flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        {success && (
          <div
            className="glass-card animate-fade-in"
            style={{
              padding: '1rem',
              marginBottom: '1.5rem',
              background: 'var(--success-bg)',
              borderColor: 'var(--success)',
              color: 'var(--success)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
            }}
          >
            <CheckCircle2 style={{ width: '1.25rem', height: '1.25rem', flexShrink: 0 }} />
            <span>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label" htmlFor="title">
                Item Title *
              </label>
              <input
                id="title"
                type="text"
                className="input-field"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="category">
                <Tag style={{ width: '0.85rem', height: '0.85rem', marginRight: '0.35rem', display: 'inline' }} />
                Category *
              </label>
              <select
                id="category"
                className="input-field"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                required
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="incidentDate">
                <Calendar style={{ width: '0.85rem', height: '0.85rem', marginRight: '0.35rem', display: 'inline' }} />
                Incident Date & Time *
              </label>
              <input
                id="incidentDate"
                type="datetime-local"
                className="input-field"
                value={incidentDate}
                onChange={(e) => setIncidentDate(e.target.value)}
                required
              />
            </div>

            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label" htmlFor="location">
                <MapPin style={{ width: '0.85rem', height: '0.85rem', marginRight: '0.35rem', display: 'inline' }} />
                Campus Location *
              </label>
              <input
                id="location"
                type="text"
                className="input-field"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                required
              />
            </div>

            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label" htmlFor="description">
                <FileText style={{ width: '0.85rem', height: '0.85rem', marginRight: '0.35rem', display: 'inline' }} />
                Detailed Description *
              </label>
              <textarea
                id="description"
                className="input-field"
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
              />
            </div>

            {/* Photo Attachment */}
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label">Item Photo</label>
              {previewUrl ? (
                <div
                  style={{
                    position: 'relative',
                    width: '180px',
                    height: '180px',
                    borderRadius: 'var(--radius-md)',
                    overflow: 'hidden',
                    border: '1px solid var(--border-color)',
                  }}
                >
                  <img src={previewUrl} alt="Item" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  <button
                    type="button"
                    onClick={removeImage}
                    style={{
                      position: 'absolute',
                      top: '0.5rem',
                      right: '0.5rem',
                      background: 'rgba(0, 0, 0, 0.65)',
                      border: 'none',
                      color: '#fff',
                      borderRadius: '50%',
                      width: '28px',
                      height: '28px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                    title="Remove Photo"
                  >
                    <X style={{ width: '1rem', height: '1rem' }} />
                  </button>
                  {uploadingImage && (
                    <div
                      style={{
                        position: 'absolute',
                        inset: 0,
                        background: 'rgba(0,0,0,0.6)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        fontSize: '0.8rem',
                      }}
                    >
                      Uploading...
                    </div>
                  )}
                </div>
              ) : (
                <div
                  onClick={() => fileInputRef.current?.click()}
                  style={{
                    border: '2px dashed var(--border-color)',
                    borderRadius: 'var(--radius-lg)',
                    padding: '2rem',
                    textAlign: 'center',
                    cursor: 'pointer',
                    background: 'var(--bg-glass)',
                  }}
                >
                  <Upload style={{ width: '2rem', height: '2rem', margin: '0 auto 0.75rem', color: 'var(--text-muted)' }} />
                  <div style={{ fontSize: '0.95rem', fontWeight: 600 }}>Click to attach or replace image</div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                    PNG, JPG, or WEBP up to 5MB
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    style={{ display: 'none' }}
                    onChange={handleFileChange}
                  />
                </div>
              )}
            </div>
          </div>

          <div style={{ marginTop: '2.5rem', display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => navigate(`/items/${id}`)}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting || uploadingImage}
              style={{ minWidth: '150px' }}
            >
              {submitting ? (
                'Saving...'
              ) : (
                <>
                  <Save style={{ width: '1rem', height: '1rem', marginRight: '0.5rem' }} />
                  Save Changes
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
