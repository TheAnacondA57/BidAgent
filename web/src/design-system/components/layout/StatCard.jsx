import React from 'react';
import { Card } from './Card.jsx';

/**
 * Metric card: a label, a big mono value, and an optional trend delta.
 * Built on Card so it inherits hover/glow behavior.
 */
export function StatCard({ label, value, delta, trend, icon, glow = false, style, ...rest }) {
  const trendColor = trend === 'up' ? 'var(--success-500)' : trend === 'down' ? 'var(--danger-500)' : 'var(--text-muted)';
  return (
    <Card interactive glow={glow} padding="var(--space-5)" style={{ minWidth: 0, ...style }} {...rest}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 10 }}>
        <span style={{ font: 'var(--fw-medium) var(--text-sm)/1 var(--font-sans)', color: 'var(--text-secondary)' }}>{label}</span>
        {icon && (
          <span style={{
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            width: 30, height: 30, borderRadius: 'var(--radius-sm)',
            background: 'var(--surface-3)', color: 'var(--warm-500)', flex: 'none',
          }}>
            <span style={{ width: 16, height: 16, display: 'inline-flex' }}>{icon}</span>
          </span>
        )}
      </div>
      <div style={{ marginTop: 12, display: 'flex', alignItems: 'baseline', gap: 10, flexWrap: 'wrap' }}>
        <span style={{ font: 'var(--fw-medium) var(--text-3xl)/1 var(--font-mono)', color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>{value}</span>
        {delta && (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 3, font: 'var(--fw-medium) var(--text-sm)/1 var(--font-mono)', color: trendColor }}>
            {trend === 'up' && <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M7 17L17 7M9 7h8v8"/></svg>}
            {trend === 'down' && <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M7 7l10 10M17 9v8H9"/></svg>}
            {delta}
          </span>
        )}
      </div>
    </Card>
  );
}
