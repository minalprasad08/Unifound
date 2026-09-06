import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { itemApi } from '../services/api';
import { Item, ItemType, ItemStatus } from '../types/auth';
import {
  Search,
  Filter,
  MapPin,
  Tag,
  Package,
  Clock,
  ArrowUpDown,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  ExternalLink,
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

export const SearchItems: React.FC = () => {
  const [items, setItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search & Filter State
  const [keyword, setKeyword] = useState('');
  const [itemType, setItemType] = useState<ItemType | ''>('');
  const [category, setCategory] = useState('');
  const [location, setLocation] = useState('');
  const [statusFilter, setStatusFilter] = useState<ItemStatus | ''>('');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [sortBy, setSortBy] = useState<'created_at' | 'incident_date'>('created_at');
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');
  const [page, setPage] = useState(1);
  const [pageSize] = useState(12);

  // Pagination meta
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  // Toggle filter panel on mobile
  const [showFilters, setShowFilters] = useState(false);

  const fetchSearchResults = async (targetPage = page) => {
    try {
      setLoading(true);
      setError(null);

      // Validate date order if both entered
      if (fromDate && toDate && new Date(fromDate) > new Date(toDate)) {
        setError('From Date cannot be later than To Date.');
        setLoading(false);
        return;
      }

      const params: any = {
        page: targetPage,
        page_size: pageSize,
        sort_by: sortBy,
        sort_order: sortOrder,
      };

      if (keyword.trim()) params.q = keyword.trim();
      if (itemType) params.item_type = itemType;
      if (category) params.category = category;
      if (location.trim()) params.location = location.trim();
      if (statusFilter) params.status = statusFilter;
      if (fromDate) params.from_date = new Date(fromDate).toISOString();
      if (toDate) params.to_date = new Date(toDate).toISOString();

      const data = await itemApi.searchItems(params);
      setItems(data.items);
      setTotal(data.total);
      setTotalPages(data.total_pages);
      setPage(data.page);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to search items.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSearchResults(1);
  }, [itemType, category, statusFilter, sortBy, sortOrder]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchSearchResults(1);
  };

  const handleResetFilters = () => {
    setKeyword('');
    setItemType('');
    setCategory('');
    setLocation('');
    setStatusFilter('');
    setFromDate('');
    setToDate('');
    setSortBy('created_at');
    setSortOrder('desc');
    setPage(1);
  };

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
    <div className="container animate-fade-in" style={{ paddingTop: '2rem', maxWidth: '1200px' }}>
      {/* Title Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800 }}>Search Campus Items</h1>
        <p style={{ color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
          Explore, filter, and track lost items reported by students, staff, and campus security.
        </p>
      </div>

      {/* Main Search Input Form */}
      <form onSubmit={handleSearchSubmit} style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <div style={{ position: 'relative', flex: 1, minWidth: '260px' }}>
            <Search
              style={{
                position: 'absolute',
                left: '1rem',
                top: '50%',
                transform: 'translateY(-50%)',
                color: 'var(--text-muted)',
                width: '1.2rem',
                height: '1.2rem',
              }}
            />
            <input
              type="text"
              className="input-field"
              placeholder="Search by keyword (e.g. MacBook, Hydro Flask, blue backpack, car key fob)..."
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              style={{ paddingLeft: '2.75rem', height: '3.1rem', fontSize: '0.98rem' }}
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ padding: '0 1.75rem', height: '3.1rem' }}>
            <Search style={{ width: '1rem', height: '1rem', marginRight: '0.4rem' }} />
            Search
          </button>
          <button
            type="button"
            className="btn btn-secondary"
            onClick={() => setShowFilters(!showFilters)}
            style={{ height: '3.1rem' }}
          >
            <Filter style={{ width: '1rem', height: '1rem', marginRight: '0.4rem' }} />
            {showFilters ? 'Hide Filters' : 'Filters'}
          </button>
        </div>
      </form>

      {/* Filter Toolbar / Panel */}
      <div
        className="glass-card"
        style={{
          padding: '1.5rem',
          marginBottom: '2rem',
          display: showFilters ? 'block' : 'none',
        }}
      >
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1.25rem',
          }}
        >
          {/* Item Type */}
          <div>
            <label className="form-label" style={{ fontSize: '0.82rem' }}>
              Report Type
            </label>
            <select
              className="input-field"
              value={itemType}
              onChange={(e) => setItemType(e.target.value as ItemType | '')}
              style={{ fontSize: '0.88rem' }}
            >
              <option value="">All Types (Lost & Found)</option>
              <option value="LOST">Lost Items Only</option>
              <option value="FOUND">Found Items Only</option>
            </select>
          </div>

          {/* Category */}
          <div>
            <label className="form-label" style={{ fontSize: '0.82rem' }}>
              Category
            </label>
            <select
              className="input-field"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              style={{ fontSize: '0.88rem' }}
            >
              <option value="">All Categories</option>
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* Location */}
          <div>
            <label className="form-label" style={{ fontSize: '0.82rem' }}>
              Campus Location
            </label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. Library, Science Hall..."
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              style={{ fontSize: '0.88rem' }}
            />
          </div>

          {/* Status */}
          <div>
            <label className="form-label" style={{ fontSize: '0.82rem' }}>
              Status
            </label>
            <select
              className="input-field"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as ItemStatus | '')}
              style={{ fontSize: '0.88rem' }}
            >
              <option value="">All Statuses</option>
              <option value="OPEN">Open</option>
              <option value="CLAIM_PENDING">Claim Pending</option>
              <option value="CLAIMED">Claimed</option>
              <option value="RESOLVED">Resolved</option>
              <option value="CLOSED">Closed</option>
            </select>
          </div>

          {/* From Date */}
          <div>
            <label className="form-label" style={{ fontSize: '0.82rem' }}>
              From Incident Date
            </label>
            <input
              type="date"
              className="input-field"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              style={{ fontSize: '0.88rem' }}
            />
          </div>

          {/* To Date */}
          <div>
            <label className="form-label" style={{ fontSize: '0.82rem' }}>
              To Incident Date
            </label>
            <input
              type="date"
              className="input-field"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              style={{ fontSize: '0.88rem' }}
            />
          </div>

          {/* Sort Field */}
          <div>
            <label className="form-label" style={{ fontSize: '0.82rem' }}>
              Sort By
            </label>
            <select
              className="input-field"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'created_at' | 'incident_date')}
              style={{ fontSize: '0.88rem' }}
            >
              <option value="created_at">Date Reported</option>
              <option value="incident_date">Incident Date</option>
            </select>
          </div>

          {/* Sort Order */}
          <div>
            <label className="form-label" style={{ fontSize: '0.82rem' }}>
              Order
            </label>
            <select
              className="input-field"
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as 'desc' | 'asc')}
              style={{ fontSize: '0.88rem' }}
            >
              <option value="desc">Newest First</option>
              <option value="asc">Oldest First</option>
            </select>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={handleResetFilters}
            style={{ fontSize: '0.85rem' }}
          >
            <RotateCcw style={{ width: '0.85rem', height: '0.85rem', marginRight: '0.35rem' }} />
            Reset All
          </button>
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={() => fetchSearchResults(1)}
            style={{ fontSize: '0.85rem' }}
          >
            Apply Filters
          </button>
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

      {/* Results Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '1.25rem',
        }}
      >
        <div style={{ fontSize: '0.92rem', color: 'var(--text-secondary)' }}>
          Showing <strong>{items.length}</strong> of <strong>{total}</strong> results
          {keyword && <span> matching "<em>{keyword}</em>"</span>}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          <ArrowUpDown style={{ width: '0.9rem', height: '0.9rem' }} />
          <span>{sortBy === 'created_at' ? 'Report Date' : 'Incident Date'} ({sortOrder.toUpperCase()})</span>
        </div>
      </div>

      {/* Loading State */}
      {loading ? (
        <div style={{ padding: '5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <div className="spinner" style={{ margin: '0 auto 1rem' }} />
          Searching database...
        </div>
      ) : items.length === 0 ? (
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
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700 }}>No items match your criteria</h3>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '420px', marginTop: '0.5rem', fontSize: '0.9rem' }}>
            Try adjusting your search terms, removing filters, or searching for broader campus locations.
          </p>
          <button className="btn btn-secondary" style={{ marginTop: '1.5rem' }} onClick={handleResetFilters}>
            Clear All Filters
          </button>
        </div>
      ) : (
        /* Results Grid */
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
            gap: '1.5rem',
            marginBottom: '2.5rem',
          }}
        >
          {items.map((item) => (
            <div
              key={item.id}
              className="glass-card"
              style={{
                padding: '1.5rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                {/* Photo Thumbnail */}
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
                    <img src={item.image_url} alt={item.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
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
                    <span>Incident: {new Date(item.incident_date).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>

              {/* Card Action */}
              <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
                <Link
                  to={`/items/${item.id}`}
                  className="btn btn-secondary btn-sm"
                  style={{ width: '100%', justifyContent: 'center' }}
                >
                  <ExternalLink style={{ width: '0.85rem', height: '0.85rem', marginRight: '0.4rem' }} />
                  View Item Details
                </Link>
              </div>
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
            onClick={() => fetchSearchResults(page - 1)}
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
            onClick={() => fetchSearchResults(page + 1)}
          >
            Next
            <ChevronRight style={{ width: '1rem', height: '1rem', marginLeft: '0.25rem' }} />
          </button>
        </div>
      )}
    </div>
  );
};
