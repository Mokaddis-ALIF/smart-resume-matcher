import { useEffect } from "react";

/**
 * Full-screen blocking overlay loader.
 *
 * Renders a semi-transparent, blurred backdrop that captures ALL pointer
 * events — while it is visible the user cannot click the sidebar, navigate
 * to another page, or interact with anything behind it. Use it around any
 * async mutation that must run to completion uninterrupted (CV upload,
 * match scoring, job create/edit).
 *
 * Props:
 *   show     — boolean, whether the overlay is visible
 *   title    — main line (e.g. "Scoring candidates")
 *   subtitle — optional secondary line (e.g. live progress message)
 */
export default function BlockingLoader({ show, title = "Working…", subtitle = "" }) {
  // Lock background scroll and swallow the Escape key while active so the
  // overlay can't be dismissed or scrolled past.
  useEffect(() => {
    if (!show) return;
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const blockKeys = (e) => { if (e.key === "Escape") e.preventDefault(); };
    window.addEventListener("keydown", blockKeys, true);
    return () => {
      document.body.style.overflow = prevOverflow;
      window.removeEventListener("keydown", blockKeys, true);
    };
  }, [show]);

  if (!show) return null;

  return (
    <div
      role="alertdialog"
      aria-busy="true"
      aria-live="assertive"
      aria-label={title}
      onClick={(e) => e.stopPropagation()}
      onContextMenu={(e) => e.preventDefault()}
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "rgba(15, 23, 42, 0.55)",
        backdropFilter: "blur(3px)",
        WebkitBackdropFilter: "blur(3px)",
        animation: "bl-fade 0.18s ease",
      }}
    >
      <div
        style={{
          background: "#fff",
          borderRadius: 16,
          padding: "30px 40px",
          boxShadow: "0 20px 60px rgba(0,0,0,0.3)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 16,
          minWidth: 260,
          maxWidth: 380,
          textAlign: "center",
          animation: "bl-pop 0.2s ease",
        }}
      >
        {/* Spinner */}
        <div style={{ position: "relative", width: 54, height: 54 }}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              border: "4px solid #eef2ff",
              borderTopColor: "#4f46e5",
              borderRadius: "50%",
              animation: "bl-spin 0.8s linear infinite",
            }}
          />
        </div>

        <div>
          <div style={{ fontSize: 15, fontWeight: 700, color: "#0f172a" }}>{title}</div>
          {subtitle && (
            <div style={{ fontSize: 13, color: "#64748b", marginTop: 5, lineHeight: 1.5 }}>
              {subtitle}
            </div>
          )}
        </div>

        <div style={{ fontSize: 11.5, color: "#94a3b8", display: "flex", alignItems: "center", gap: 6 }}>
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: "#4f46e5",
              animation: "bl-blink 1.4s ease-in-out infinite",
            }}
          />
          Please wait — don't close or navigate away
        </div>
      </div>

      <style>{`
        @keyframes bl-spin { to { transform: rotate(360deg); } }
        @keyframes bl-fade { from { opacity: 0; } to { opacity: 1; } }
        @keyframes bl-pop  { from { transform: scale(0.94); opacity: 0; } to { transform: scale(1); opacity: 1; } }
        @keyframes bl-blink { 0%, 100% { opacity: 0.25; } 50% { opacity: 1; } }
      `}</style>
    </div>
  );
}
