import React from 'react';

/**
 * Surface container. Hover lifts and brightens when `interactive`. Optional
 * `glow` adds an aurora wash bleeding from the top of the card.
 */
export function Card({ interactive = false, glow = false, padding = 'var(--space-6)', as = 'div', children, style, onClick, ...rest }) {
  const [hover, setHover] = React.useState(false);
  const El = as;
  const lifted = interactive && hover;
  return (
    <El
      onClick={onClick}
      onMouseEnter={() => interactive && setHover(true)}
      onMouseLeave={() => interactive && setHover(false)}
      style={{
        position: 'relative',
        padding,
        background: 'var(--surface-card)',
        border: `1px solid ${lifted ? 'var(--line-strong)' : 'var(--line-soft)'}`,
        borderRadius: 'var(--radius-lg)',
        boxShadow: lifted
          ? 'var(--edge-highlight), var(--shadow-lg)'
          : 'var(--edge-highlight), var(--shadow-md)',
        transform: lifted ? 'translateY(-3px)' : 'none',
        transition: 'transform var(--dur-base) var(--ease-out), border-color var(--dur-base) var(--ease-out), box-shadow var(--dur-base) var(--ease-out)',
        cursor: interactive ? 'pointer' : 'default',
        overflow: 'hidden',
        ...style,
      }}
      {...rest}
    >
      {glow && (
        <span aria-hidden style={{
          position: 'absolute', inset: 0, pointerEvents: 'none',
          background: 'radial-gradient(110% 70% at 30% 0%, rgba(240,138,60,0.18), rgba(240,138,60,0) 55%), radial-gradient(110% 70% at 80% 0%, rgba(61,123,255,0.18), rgba(61,123,255,0) 55%)',
          opacity: lifted ? 1 : 0.7,
          transition: 'opacity var(--dur-slow) var(--ease-out)',
        }} />
      )}
      <div style={{ position: 'relative' }}>{children}</div>
    </El>
  );
}
