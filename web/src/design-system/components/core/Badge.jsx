import React from 'react';

const TONES = {
  neutral: { color: 'var(--text-secondary)', bg: 'var(--surface-2)', dot: 'var(--text-muted)' },
  success: { color: 'var(--success-500)', bg: 'var(--success-bg)', dot: 'var(--success-500)' },
  warning: { color: 'var(--warning-500)', bg: 'var(--warning-bg)', dot: 'var(--warning-500)' },
  danger:  { color: 'var(--danger-500)',  bg: 'var(--danger-bg)',  dot: 'var(--danger-500)' },
  info:    { color: 'var(--info-500)',    bg: 'var(--info-bg)',    dot: 'var(--info-500)' },
  warm:    { color: 'var(--warm-500)',     bg: 'rgba(240,138,60,0.14)', dot: 'var(--warm-500)' },
};

/**
 * Status pill. Optional leading dot (with a soft pulse when `pulse`).
 */
export function Badge({ tone = 'neutral', dot = false, pulse = false, children, style, ...rest }) {
  const t = TONES[tone] || TONES.neutral;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '3px 10px',
      font: 'var(--fw-medium) var(--text-xs)/1.4 var(--font-sans)',
      letterSpacing: '0.01em',
      color: t.color, background: t.bg,
      borderRadius: 'var(--radius-pill)',
      border: '1px solid transparent',
      ...style,
    }} {...rest}>
      {dot && (
        <span style={{
          width: 6, height: 6, borderRadius: '50%', background: t.dot, flex: 'none',
          animation: pulse ? 'ba-pulse-ring 1.8s var(--ease-out) infinite' : 'none',
        }} />
      )}
      {children}
    </span>
  );
}
