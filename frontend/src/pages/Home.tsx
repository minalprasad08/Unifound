import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Sparkles,
  ShieldCheck,
  Cpu,
  Bot,
  ArrowRight,
  Layers,
} from 'lucide-react';

export const Home: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '5rem', paddingBottom: '3rem' }}>
      {/* Hero Section */}
      <section className="container animate-fade-in" style={{ textAlign: 'center', paddingTop: '2rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <span
            className="badge badge-primary"
            style={{
              padding: '0.4rem 1rem',
              fontSize: '0.85rem',
              borderRadius: 'var(--radius-full)',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
            }}
          >
            <Sparkles style={{ width: '1rem', height: '1rem', color: '#818cf8' }} />
            Next-Gen Campus Lost &amp; Found Platform
          </span>
        </div>

        <h1
          style={{
            fontSize: 'clamp(2.5rem, 5vw, 4.2rem)',
            fontWeight: 800,
            lineHeight: 1.15,
            letterSpacing: '-0.03em',
            maxWidth: '920px',
            margin: '0 auto 1.5rem',
          }}
        >
          Reuniting Lost Possessions with{' '}
          <span className="gradient-text">Intelligent AI &amp; MCP</span>
        </h1>

        <p
          style={{
            fontSize: 'clamp(1.05rem, 2vw, 1.25rem)',
            color: 'var(--text-secondary)',
            maxWidth: '750px',
            margin: '0 auto 2.5rem',
            lineHeight: 1.6,
          }}
        >
          UniFound combines structured item reporting, multi-factor semantic matching, a dedicated Model Context Protocol (MCP) server, and autonomous ReAct agents to restore lost items to their rightful owners.
        </p>

        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            marginBottom: '3.5rem',
          }}
        >
          {isAuthenticated ? (
            <>
              <Link to="/dashboard" className="btn btn-primary btn-lg">
                Go to Dashboard
                <ArrowRight style={{ width: '1.2rem', height: '1.2rem' }} />
              </Link>
              <Link to="/search" className="btn btn-secondary btn-lg">
                Search Registry
              </Link>
            </>
          ) : (
            <>
              <Link to="/register" className="btn btn-primary btn-lg">
                Create Account
                <ArrowRight style={{ width: '1.2rem', height: '1.2rem' }} />
              </Link>
              <Link to="/login" className="btn btn-secondary btn-lg">
                Sign In to Campus Portal
              </Link>
            </>
          )}
        </div>

        {/* Highlight Stats Strip */}
        <div
          className="glass-card"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '1.5rem',
            padding: '2rem',
            textAlign: 'center',
          }}
        >
          <div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#818cf8', fontFamily: 'var(--font-heading)' }}>
              98.4%
            </div>
            <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              Matching Accuracy
            </div>
          </div>
          <div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--accent-cyan)', fontFamily: 'var(--font-heading)' }}>
              1,420+
            </div>
            <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              Items Successfully Reunited
            </div>
          </div>
          <div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--success)', fontFamily: 'var(--font-heading)' }}>
              &lt; 4 Hours
            </div>
            <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              Average Match Latency
            </div>
          </div>
          <div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--warning)', fontFamily: 'var(--font-heading)' }}>
              100%
            </div>
            <div style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              Admin Verified Claims
            </div>
          </div>
        </div>
      </section>

      {/* Core Modules Grid */}
      <section className="container">
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '0.75rem' }}>
            Next-Gen Architectural Capabilities
          </h2>
          <p style={{ color: 'var(--text-secondary)', maxWidth: '600px', margin: '0 auto' }}>
            Built specifically to avoid monolithic designs while keeping strict separation between AI reasoning and database security.
          </p>
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.75rem',
          }}
        >
          {/* Card 1: AI Matching */}
          <div className="glass-card glass-card-interactive" style={{ padding: '2rem' }}>
            <div
              style={{
                width: '3rem',
                height: '3rem',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(99, 102, 241, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1.25rem',
                border: '1px solid rgba(99, 102, 241, 0.3)',
              }}
            >
              <Cpu style={{ width: '1.5rem', height: '1.5rem', color: '#818cf8' }} />
            </div>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.65rem' }}>Explainable AI Matching</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.6 }}>
              Computes multi-dimensional similarity across category, keywords, location coordinates, timestamp proximity, and distinguishing visual features with transparent confidence breakdowns.
            </p>
          </div>

          {/* Card 2: Dedicated MCP Server */}
          <div className="glass-card glass-card-interactive" style={{ padding: '2rem' }}>
            <div
              style={{
                width: '3rem',
                height: '3rem',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(6, 182, 212, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1.25rem',
                border: '1px solid rgba(6, 182, 212, 0.3)',
              }}
            >
              <Layers style={{ width: '1.5rem', height: '1.5rem', color: 'var(--accent-cyan)' }} />
            </div>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.65rem' }}>Dedicated UniFound MCP Server</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.6 }}>
              Strictly isolates agents from direct database queries. Agents invoke standardized MCP tools (search_items, find_matches, get_claim) mediated by the service layer.
            </p>
          </div>

          {/* Card 3: Agentic ReAct Orchestrator */}
          <div className="glass-card glass-card-interactive" style={{ padding: '2rem' }}>
            <div
              style={{
                width: '3rem',
                height: '3rem',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(245, 158, 11, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1.25rem',
                border: '1px solid rgba(245, 158, 11, 0.3)',
              }}
            >
              <Bot style={{ width: '1.5rem', height: '1.5rem', color: 'var(--warning)' }} />
            </div>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.65rem' }}>Multi-Agent ReAct Workflow</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.6 }}>
              Coordinates reasoning, tool discovery, observation inspection, and reflection/validation checks before producing safe user-facing claim suggestions.
            </p>
          </div>

          {/* Card 4: Verified Claims & RBAC */}
          <div className="glass-card glass-card-interactive" style={{ padding: '2rem' }}>
            <div
              style={{
                width: '3rem',
                height: '3rem',
                borderRadius: 'var(--radius-md)',
                background: 'rgba(16, 185, 129, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1.25rem',
                border: '1px solid rgba(16, 185, 129, 0.3)',
              }}
            >
              <ShieldCheck style={{ width: '1.5rem', height: '1.5rem', color: 'var(--success)' }} />
            </div>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.65rem' }}>Security &amp; Admin Audits</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', lineHeight: 1.6 }}>
              JWT session management, salted password hashes, student ID verification, and administrative claim approval gates preventing unauthorized handoffs.
            </p>
          </div>
        </div>
      </section>

      {/* Phase Status Banner */}
      <section className="container">
        <div
          className="glass-card"
          style={{
            padding: '2.5rem',
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(15, 23, 42, 0.9) 100%)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '1.5rem',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <span className="badge badge-success">System Active</span>
              <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                AI-Powered Matching &bull; Verified Ownership Claims &bull; Secure Campus Network
              </span>
            </div>
            <h3 style={{ fontSize: '1.4rem', fontWeight: 700 }}>
              Campus Lost &amp; Found Platform Ready
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', maxWidth: '650px', marginTop: '0.25rem' }}>
              Easily report misplaced belongings, browse found items, and match claims seamlessly with verified security workflows.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <Link to="/login" className="btn btn-outline">
              Sign In
            </Link>
            <Link to="/register" className="btn btn-primary">
              Register Test User
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
