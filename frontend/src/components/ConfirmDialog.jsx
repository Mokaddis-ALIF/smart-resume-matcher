import { useEffect, useRef } from "react";

/**
 * Reusable confirmation modal — replaces the native window.confirm().
 *
 * Renders a centered dialog over a dimmed, blurred backdrop. Clicking the
 * backdrop or pressing Escape cancels; Enter confirms. The confirm button is
 * auto-focused so keyboard users can act immediately.
 *
 * Props:
 *   open         — boolean, whether the dialog is shown
 *   title        — heading text
 *   message      — body text (string or node)
 *   confirmLabel — confirm button text (default "Delete")
 *   cancelLabel  — cancel button text (default "Cancel")
 *   danger       — red destructive styling on confirm (default true)
 *   busy         — show a spinner + disable buttons while the action runs
 *   onConfirm    — called when the user confirms
 *   onCancel     — called when the user cancels / dismisses
 */
export default function ConfirmDialog({
  open,
  title = "Are you sure?",
  message = "",
  confirmLabel = "Delete",
  cancelLabel = "Cancel",
  danger = true,
  busy = false,
  onConfirm,
  onCancel,
}) {
  const confirmRef = useRef(null);

  useEffect(() => {
    if (!open) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    confirmRef.current?.focus();

    const onKey = (e) => {
      if (busy) return;
      if (e.key === "Escape") { e.preventDefault(); onCancel?.(); }
      if (e.key === "Enter")  { e.preventDefault(); onConfirm?.(); }
    };
    window.addEventListener("keydown", onKey, true);
    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener("keydown", onKey, true);
    };
  }, [open, busy, onConfirm, onCancel]);

  if (!open) return null;

  const accent = danger ? "#dc2626" : "#4f46e5";
  const accentBg = danger ? "#fee2e2" : "#eef2ff";

  return (
    <div
      role="alertdialog"
      aria-modal="true"
      aria-label={title}
      onClick={() => !busy && onCancel?.()}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 10000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
        background: "rgba(15, 23, 42, 0.55)",
        backdropFilter: "blur(3px)",
        WebkitBackdropFilter: "blur(3px)",
        animation: "cd-fade 0.16s ease",
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: "#fff",
          borderRadius: 16,
          padding: "26px 26px 22px",
          width: "100%",
          maxWidth: 400,
          boxShadow: "0 24px 64px rgba(0,0,0,0.28)",
          animation: "cd-pop 0.18s ease",
        }}
      >
        {/* Icon */}
        <div
          style={{
            width: 48,
            height: 48,
            borderRadius: "50%",
            background: accentBg,
            color: accent,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 24,
            marginBottom: 16,
          }}
        >
          {danger ? "🗑️" : "❓"}
        </div>

        <h3 style={{ fontSize: 17, fontWeight: 700, color: "#0f172a", marginBottom: 8 }}>
          {title}
        </h3>
        <div style={{ fontSize: 13.5, color: "#64748b", lineHeight: 1.6, marginBottom: 22 }}>
          {message}
        </div>

        <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
          <button
            type="button"
            onClick={() => !busy && onCancel?.()}
            disabled={busy}
            style={{
              padding: "9px 18px",
              borderRadius: 9,
              fontSize: 13.5,
              fontWeight: 600,
              border: "1px solid #e2e8f0",
              background: "#fff",
              color: "#475569",
              cursor: busy ? "not-allowed" : "pointer",
              opacity: busy ? 0.6 : 1,
              transition: "background 0.13s",
            }}
            onMouseEnter={(e) => { if (!busy) e.currentTarget.style.background = "#f8fafc"; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = "#fff"; }}
          >
            {cancelLabel}
          </button>
          <button
            ref={confirmRef}
            type="button"
            onClick={() => !busy && onConfirm?.()}
            disabled={busy}
            style={{
              padding: "9px 18px",
              borderRadius: 9,
              fontSize: 13.5,
              fontWeight: 600,
              border: "none",
              background: accent,
              color: "#fff",
              cursor: busy ? "not-allowed" : "pointer",
              opacity: busy ? 0.75 : 1,
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              transition: "filter 0.13s",
            }}
            onMouseEnter={(e) => { if (!busy) e.currentTarget.style.filter = "brightness(0.92)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.filter = "none"; }}
          >
            {busy && (
              <span
                style={{
                  width: 14,
                  height: 14,
                  border: "2px solid rgba(255,255,255,0.4)",
                  borderTopColor: "#fff",
                  borderRadius: "50%",
                  animation: "cd-spin 0.7s linear infinite",
                }}
              />
            )}
            {busy ? "Deleting…" : confirmLabel}
          </button>
        </div>
      </div>

      <style>{`
        @keyframes cd-fade { from { opacity: 0; } to { opacity: 1; } }
        @keyframes cd-pop  { from { transform: scale(0.95) translateY(6px); opacity: 0; } to { transform: scale(1) translateY(0); opacity: 1; } }
        @keyframes cd-spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
