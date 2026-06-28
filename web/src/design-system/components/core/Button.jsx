import React from 'react';

const SIZES = {
  sm: { padding: '8px 16px', font: 'var(--text-sm)', radius: 'var(--radius-pill)', icon: 16, gap: 7 },
  md: { padding: '11px 22px', font: 'var(--text-base)', radius: 'var(--radius-pill)', icon: 18, gap: 8 },
  lg: { padding: '15px 30px', font: 'var(--text-lg)', radius: 'var(--radius-pill)', icon: 20, gap: 10 },
};

/**
 * BidAgent primary button. The signature control: glassy dark pill with an
 * aurora gradient hairline that intensifies into a glow on hover, plus a
 * spring press. Variants: primary | accent | secondary | ghost | cool.
 */
export function Button({
  variant = 'primary',
  size = 'md',
  iconLeft,
  iconRight,
  loading = false,
  disabled = false,
  full = false,
  href,
  onClick,
  type = 'button',
  children,
  style,
  ...rest
}) {
  const [hover, setHover] = React.useState(false);
  const [press, setPress] = React.useState(false);
  const s = SIZES[size] || SIZES.md;
  const isDisabled = disabled || loading;

  const base = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: s.gap,
    width: full ? '100%' : 'auto',
    padding: s.padding,
    font: `var(--fw-medium) ${s.font}/1 var(--font-sans)`,
    letterSpacing: '-0.01em',
    borderRadius: s.radius,
    border: '1px solid transparent',
    cursor: isDisabled ? 'not-allowed' : 'pointer',
    opacity: isDisabled ? 0.5 : 1,
    transform: press ? 'scale(0.96)' : hover ? 'translateY(-1px)' : 'none',
    transition: `transform var(--dur-fast) var(--ease-spring), box-shadow var(--dur-base) var(--ease-out), background var(--dur-base) var(--ease-out), border-color var(--dur-base) var(--ease-out)`,
    textDecoration: 'none',
    whiteSpace: 'nowrap',
    userSelect: 'none',
    WebkitTapHighlightColor: 'transparent',
  };

  const variants = {
    primary: {
      color: 'var(--text-primary)',
      background: `linear-gradient(var(--bg-elevated),var(--bg-elevated)) padding-box, var(--grad-aurora) border-box`,
      boxShadow: hover
        ? 'var(--edge-highlight), 0 8px 30px -6px rgba(240,138,60,0.35), 0 8px 30px -6px rgba(61,123,255,0.35)'
        : 'var(--edge-highlight), var(--shadow-md)',
    },
    accent: {
      color: 'var(--text-on-accent)',
      background: hover
        ? 'linear-gradient(120deg,#F79A50,#F08A3C)'
        : 'var(--warm-500)',
      borderColor: 'transparent',
      boxShadow: hover ? 'var(--glow-warm)' : 'var(--shadow-sm)',
    },
    cool: {
      color: '#fff',
      background: hover ? 'linear-gradient(120deg,#5C90FF,#3D7BFF)' : 'var(--cool-500)',
      borderColor: 'transparent',
      boxShadow: hover ? 'var(--glow-cool)' : 'var(--shadow-sm)',
    },
    secondary: {
      color: 'var(--text-primary)',
      background: hover ? 'var(--surface-2)' : 'var(--surface-1)',
      borderColor: hover ? 'var(--line-strong)' : 'var(--line-soft)',
      boxShadow: 'var(--edge-highlight)',
    },
    ghost: {
      color: hover ? 'var(--text-primary)' : 'var(--text-secondary)',
      background: hover ? 'var(--surface-1)' : 'transparent',
      borderColor: 'transparent',
    },
  };

  const handlers = {
    onMouseEnter: () => setHover(true),
    onMouseLeave: () => { setHover(false); setPress(false); },
    onMouseDown: () => setPress(true),
    onMouseUp: () => setPress(false),
    onClick: isDisabled ? undefined : onClick,
  };

  const spinner = (
    <span style={{
      width: s.icon, height: s.icon, borderRadius: '50%',
      border: '2px solid currentColor', borderTopColor: 'transparent',
      display: 'inline-block', animation: 'ba-spin 0.7s linear infinite',
    }} />
  );

  const content = (
    <>
      {loading ? spinner : iconLeft && <span style={{ display: 'inline-flex', width: s.icon, height: s.icon }}>{iconLeft}</span>}
      {children && <span style={{ opacity: loading ? 0.7 : 1 }}>{children}</span>}
      {!loading && iconRight && <span style={{ display: 'inline-flex', width: s.icon, height: s.icon }}>{iconRight}</span>}
    </>
  );

  const finalStyle = { ...base, ...variants[variant], ...style };

  if (href && !isDisabled) {
    return <a href={href} style={finalStyle} {...handlers} {...rest}>{content}</a>;
  }
  return (
    <button type={type} disabled={isDisabled} style={finalStyle} {...handlers} {...rest}>
      {content}
    </button>
  );
}
