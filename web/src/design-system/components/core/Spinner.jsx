import React from 'react';

/**
 * Loading spinner. Aurora-tinted ring by default.
 */
export function Spinner({ size = 20, thickness = 2, tone = 'aurora', label = 'Loading', style, ...rest }) {
  const colors = {
    aurora: 'var(--warm-500)',
    cool: 'var(--cool-500)',
    muted: 'var(--text-muted)',
    inherit: 'currentColor',
  };
  return (
    <span
      role="status"
      aria-label={label}
      style={{
        display: 'inline-block', width: size, height: size,
        borderRadius: '50%',
        border: `${thickness}px solid var(--line-soft)`,
        borderTopColor: colors[tone] || colors.aurora,
        animation: 'ba-spin 0.7s linear infinite',
        ...style,
      }}
      {...rest}
    />
  );
}
