/**
 * Reusable loading indicator.
 */
export default function LoadingSpinner({ text = "Loading..." }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 10,
      padding: 20, color: "#6b7280", fontSize: 14,
    }}>
      <div style={{
        width: 18, height: 18, border: "2px solid #e5e7eb",
        borderTopColor: "#4f46e5", borderRadius: "50%",
        animation: "spin 0.8s linear infinite",
      }} />
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      {text}
    </div>
  );
}
