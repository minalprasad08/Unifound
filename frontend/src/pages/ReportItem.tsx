import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { itemApi } from '../services/api';
import { ItemType } from '../types/auth';
import {
  Upload,
  AlertCircle,
  CheckCircle2,
  Calendar,
  MapPin,
  Tag,
  FileText,
  X,
  Sparkles,
} from 'lucide-react';

interface ReportItemProps {
  initialType?: ItemType;
}

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

export const ReportItem: React.FC<ReportItemProps> = ({ initialType = 'LOST' }) => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [itemType, setItemType] = useState<ItemType>(initialType);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [location, setLocation] = useState('');
  // Default to current local datetime in ISO format for datetime-local
  const [incidentDate, setIncidentDate] = useState(() => {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    return now.toISOString().slice(0, 16);
  });
  const [description, setDescription] = useState('');
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const [uploadingImage, setUploadingImage] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate size (< 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('Selected image exceeds 5MB size limit.');
      return;
    }

    // Validate type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Please select a valid image file (.jpg, .jpeg, .png, .webp).');
      return;
    }

    setError(null);
    setUploadingImage(true);

    // Create local blob preview
    const localPreview = URL.createObjectURL(file);
    setPreviewUrl(localPreview);

    try {
      const response = await itemApi.uploadImage(file);
      setImageUrl(response.image_url);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload image. Please try again.');
      setPreviewUrl(null);
      setImageUrl(null);
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
    setError(null);
    setSuccess(null);

    if (title.trim().length < 2) {
      setError('Title must be at least 2 characters.');
      return;
    }

    if (description.trim().length < 5) {
      setError('Please provide a detailed description (at least 5 characters).');
      return;
    }

    if (!location.trim()) {
      setError('Please specify where the item was lost or found.');
      return;
    }

    setSubmitting(true);

    try {
      const payload = {
        title: title.trim(),
        category,
        location: location.trim(),
        incident_date: new Date(incidentDate).toISOString(),
        description: description.trim(),
        image_url: imageUrl || undefined,
      };

      const created =
        itemType === 'LOST'
          ? await itemApi.createLost(payload)
          : await itemApi.createFound(payload);

      setSuccess(`Report filed successfully! Reference ID #${created.id}`);
      setTimeout(() => {
        navigate(`/items/${created.id}`);
      }, 1200);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit report. Please check fields.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="container animate-fade-in" style={{ paddingTop: '2rem', maxWidth: '820px' }}>
      <div className="glass-card" style={{ padding: '2.5rem' }}>
        {/* Header with Type Selector */}
        <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
          <div
            style={{
              display: 'inline-flex',
              padding: '0.35rem',
              background: 'var(--bg-glass)',
              borderRadius: 'var(--radius-full)',
              border: '1px solid var(--border-color)',
              marginBottom: '1.25rem',
            }}
          >
            <button
              type="button"
              className={`btn ${itemType === 'LOST' ? 'btn-primary' : 'btn-ghost'}`}
              style={{
                borderRadius: 'var(--radius-full)',
                padding: '0.45rem 1.5rem',
                fontSize: '0.9rem',
              }}
              onClick={() => setItemType('LOST')}
            >
              Report Lost Item
            </button>
            <button
              type="button"
              className={`btn ${itemType === 'FOUND' ? 'btn-primary' : 'btn-ghost'}`}
              style={{
                borderRadius: 'var(--radius-full)',
                padding: '0.45rem 1.5rem',
                fontSize: '0.9rem',
              }}
              onClick={() => setItemType('FOUND')}
            >
              Report Found Item
            </button>
          </div>

          <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>
            {itemType === 'LOST' ? 'Report a Lost Item' : 'Report a Found Item'}
          </h1>
          <p style={{ color: 'var(--text-secondary)', marginTop: '0.35rem' }}>
            {itemType === 'LOST'
              ? 'Submit detailed information to notify campus finders and security personnel.'
              : 'Log an item you discovered on campus so the rightful owner can retrieve it safely.'}
          </p>
        </div>

        {error && (
          <div
            className="glass-card animate-fade-in"
            style={{
              padding: '1rem',
              marginBottom: '1.5rem',
              background: 'var(--danger-bg)',
              borderColor: 'var(--danger)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              color: 'var(--danger)',
            }}
          >
            <AlertCircle style={{ width: '1.25rem', height: '1.25rem', flexShrink: 0 }} />
            <span style={{ fontSize: '0.9rem' }}>{error}</span>
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
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              color: 'var(--success)',
            }}
          >
            <CheckCircle2 style={{ width: '1.25rem', height: '1.25rem', flexShrink: 0 }} />
            <span style={{ fontSize: '0.9rem' }}>{success}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
            {/* Title */}
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label" htmlFor="title">
                Item Title *
              </label>
              <input
                id="title"
                type="text"
                className="input-field"
                placeholder={itemType === 'LOST' ? 'e.g., Space Grey MacBook Air in leather sleeve' : 'e.g., Set of keys with blue carabiner'}
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>

            {/* Category */}
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

            {/* Incident Date */}
            <div className="form-group">
              <label className="form-label" htmlFor="incidentDate">
                <Calendar style={{ width: '0.85rem', height: '0.85rem', marginRight: '0.35rem', display: 'inline' }} />
                {itemType === 'LOST' ? 'Date & Time Lost *' : 'Date & Time Found *'}
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

            {/* Location */}
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label" htmlFor="location">
                <MapPin style={{ width: '0.85rem', height: '0.85rem', marginRight: '0.35rem', display: 'inline' }} />
                Campus Location *
              </label>
              <input
                id="location"
                type="text"
                className="input-field"
                placeholder="e.g., Main Library, 3rd Floor Quiet Study Pods or Science Hall 104"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                required
              />
            </div>

            {/* Description */}
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label" htmlFor="description">
                <FileText style={{ width: '0.85rem', height: '0.85rem', marginRight: '0.35rem', display: 'inline' }} />
                Detailed Description *
              </label>
              <textarea
                id="description"
                className="input-field"
                rows={4}
                placeholder="Include identifying marks, colors, stickers, brand, engravings, or any distinctive features that verify ownership..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
              />
            </div>

            {/* Image Upload Area */}
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label">
                Optional Item Photo
              </label>

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
                  <img
                    src={previewUrl}
                    alt="Preview"
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
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
                    transition: 'border-color 0.2s ease',
                  }}
                >
                  <Upload
                    style={{
                      width: '2rem',
                      height: '2rem',
                      margin: '0 auto 0.75rem',
                      color: 'var(--text-muted)',
                    }}
                  />
                  <div style={{ fontSize: '0.95rem', fontWeight: 600 }}>Click to attach an image</div>
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
              onClick={() => navigate('/my-reports')}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting || uploadingImage}
              style={{ minWidth: '160px' }}
            >
              {submitting ? (
                'Submitting...'
              ) : (
                <>
                  <Sparkles style={{ width: '1rem', height: '1rem', marginRight: '0.5rem' }} />
                  Submit {itemType === 'LOST' ? 'Lost' : 'Found'} Report
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
