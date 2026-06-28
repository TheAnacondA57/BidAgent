import React from 'react';

/**
 * Text input with optional leading icon, label, hint/error, and a focus glow
 * that animates the aurora border.
 */
export function Input({
  label, hint, error, iconLeft, type = 'text',
  value, onChange, placeholder, disabled = false, id,
  style, ...rest
}) {
  const [focus, setFocus] = React.useState(false);
  const reactId = React.useId();
  const inputId = id || reactId;
  const borderColor = error ? 'var(--danger-500)' : focus ? 'var(--cool-500)' : 'var(--line-soft)';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 7, ...style }}>
      {label && (
        <label htmlFor={inputId} style={{ font: 'var(--fw-medium) var(--text-sm)/1 var(--font-sans)', color: 'var(--text-secondary)' }}>
          {label}
        </label>
      )}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 9,
        padding: iconLeft ? '0 14px' : '0', paddingLeft: iconLeft ? 14 : 0,
        background: 'var(--surface-input)',
        border: `1px solid ${borderColor}`,
        borderRadius: 'var(--radius-md)',
        boxShadow: focus ? '0 0 0 3px var(--focus-ring), var(--edge-highlight)' : 'var(--edge-highlight)',
        transition: 'border-color var(--dur-base) var(--ease-out), box-shadow var(--dur-base) var(--ease-out)',
        opacity: disabled ? 0.5 : 1,
      }}>
        {iconLeft && <span style={{ display: 'inline-flex', width: 18, height: 18, color: focus ? 'var(--cool-300)' : 'var(--text-muted)', flex: 'none', transition: 'color var(--dur-base) var(--ease-out)' }}>{iconLeft}</span>}
        <input
          id={inputId}
          type={type}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          onFocus={() => setFocus(true)}
          onBlur={() => setFocus(false)}
          style={{
            flex: 1, width: '100%', minWidth: 0,
            padding: iconLeft ? '11px 14px 11px 0' : '11px 14px',
            border: 'none', outline: 'none', background: 'transparent',
            color: 'var(--text-primary)',
            font: 'var(--fw-regular) var(--text-base)/1.3 var(--font-sans)',
          }}
          {...rest}
        />
      </div>
      {(hint || error) && (
        <span style={{ font: 'var(--text-xs)/1.4 var(--font-sans)', color: error ? 'var(--danger-500)' : 'var(--text-muted)' }}>
          {error || hint}
        </span>
      )}
    </div>
  );
}
