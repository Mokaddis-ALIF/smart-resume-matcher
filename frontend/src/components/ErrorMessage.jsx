/**
 * Reusable error message component.
 */
export default function ErrorMessage({ message, onRetry }) {
  if (!message) return null;
  return (
    <div style={{
      padding: "12px 16px", borderRadius: 8,
      background: "#fef2f2", border: "1px solid #fecaca",
      color: "#dc2626", fontSize: 13, marginBottom: 16,
      display: "flex", justifyContent: "space-between", alignItems: "center",
    }}>
      <span>{message}</span>
      {onRetry && (
        <button
          onClick={onRetry}
          style={{
            fontSize: 12, padding: "4px 12px", borderRadius: 6,
            border: "1px solid #fecaca", background: "#fff",
            color: "#dc2626", cursor: "pointer",
          }}
        >
          Retry
        </button>
      )}
    </div>
  );
}
