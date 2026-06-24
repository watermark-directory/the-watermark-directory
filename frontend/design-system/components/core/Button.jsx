import React from "react";

/**
 * Watermark Button — the flat, square-cornered action.
 * Four variants: solid (ink), forest (the signal), ghost (outline), link.
 * No radius, no shadow. Hover darkens the fill or shifts the outline to forest.
 */
export function Button({
  variant = "solid",
  size = "md",
  href,
  icon,
  iconRight,
  disabled = false,
  onClick,
  children,
  style,
  ...rest
}) {
  const sizes = {
    sm: { padding: "9px 16px", fontSize: 13 },
    md: { padding: "12px 20px", fontSize: 14 },
    lg: { padding: "14px 24px", fontSize: 15 },
  };
  const s = sizes[size] || sizes.md;

  const base = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    fontFamily: "var(--font-sans)",
    fontWeight: 700,
    letterSpacing: "0.2px",
    lineHeight: 1,
    border: "1.5px solid transparent",
    borderRadius: "var(--radius, 0)",
    cursor: disabled ? "not-allowed" : "pointer",
    textDecoration: "none",
    whiteSpace: "nowrap",
    transition: "background var(--dur) var(--ease), border-color var(--dur) var(--ease), transform var(--dur) var(--ease), color var(--dur) var(--ease)",
    opacity: disabled ? 0.45 : 1,
    padding: s.padding,
    fontSize: s.fontSize,
  };

  const variants = {
    solid: { background: "var(--ink)", color: "var(--bone-surface)", borderColor: "var(--ink)" },
    forest: { background: "var(--forest)", color: "var(--bone-surface)", borderColor: "var(--forest)" },
    ghost: { background: "transparent", color: "var(--ink)", borderColor: "var(--ink)" },
    link: { background: "transparent", color: "var(--forest)", borderColor: "transparent", padding: 0, letterSpacing: 0 },
  };

  const className = `wm-btn wm-btn--${variant}${disabled ? " is-disabled" : ""}`;
  const merged = { ...base, ...(variants[variant] || variants.solid), ...style };

  const inner = (
    <>
      {icon ? <span style={{ display: "inline-flex", flex: "0 0 auto" }} aria-hidden="true">{icon}</span> : null}
      {children}
      {iconRight ? <span style={{ display: "inline-flex", flex: "0 0 auto" }} aria-hidden="true">{iconRight}</span> : null}
    </>
  );

  if (href && !disabled) {
    return (
      <a href={href} className={className} style={merged} onClick={onClick} {...rest}>
        {inner}
      </a>
    );
  }
  return (
    <button type="button" className={className} style={merged} disabled={disabled} onClick={onClick} {...rest}>
      {inner}
    </button>
  );
}
