import { useState, useEffect } from "react";
import { trainModels, getEvaluationResults } from "../services/api";

export default function Evaluation() {
  const [data, setData] = useState(null);
  const [training, setTraining] = useState(false);
  const [message, setMessage] = useState("");
  const [selectedModel, setSelectedModel] = useState(null);
  const [activeTab, setActiveTab] = useState("dataset1");

  useEffect(() => {
    getEvaluationResults().then(setData).catch(() => { });
  }, []);

  const handleTrain = async () => {
    setTraining(true);
    setMessage("Training classifiers on both datasets... this may take 2-3 minutes");
    try {
      await trainModels();
      setMessage("Training complete on both datasets");
      getEvaluationResults().then(setData);
    } catch (err) {
      setMessage("Training failed: " + err.message);
    } finally {
      setTraining(false);
      setTimeout(() => setMessage(""), 8000);
    }
  };

  const currentData = data?.[activeTab];
  const models = currentData?.results ? Object.keys(currentData.results) : [];
  const metrics = ["accuracy", "precision", "recall", "f1_score"];
  const metricLabels = { accuracy: "Accuracy", precision: "Precision", recall: "Recall", f1_score: "F1 Score" };
  const modelColors = {
    "SVM": "#4f46e5",
    "Random Forest": "#059669",
    "KNN": "#d97706",
    "Naive Bayes": "#dc2626",
  };

  const bestModel = models.length > 0
    ? models.reduce((a, b) => currentData.results[a].f1_score > currentData.results[b].f1_score ? a : b)
    : null;

  const datasetTabs = [
    { key: "dataset1", label: "Dataset 1: AI Resume Screening", desc: "Skills + Education + Experience + Certifications → Job Role (4 classes)" },
    { key: "dataset2", label: "Dataset 2: Resume Data", desc: "Skills + Degree + Field + Career Objective → Job Position (28 classes)" },
  ];

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h2>Model Evaluation</h2>
          <p>Compare ML classifier performance across two datasets</p>
        </div>
        <button className="btn btn-primary" onClick={handleTrain} disabled={training}>
          {training ? "Training..." : data ? "Retrain Models" : "Train Models"}
        </button>
      </div>

      {message && (
        <div style={{ padding: "10px 16px", borderRadius: 8, background: "#eef2ff", color: "#4338ca", fontSize: 13, marginBottom: 16, fontWeight: 500 }}>
          {message}
        </div>
      )}

      {!data ? (
        <div className="card" style={{ textAlign: "center", padding: 40, color: "#6b7280" }}>
          <p style={{ fontSize: 16, marginBottom: 4 }}>No evaluation data yet</p>
          <p style={{ fontSize: 13 }}>Click "Train Models" to train classifiers on both datasets</p>
        </div>
      ) : (
        <>
          {/* Dataset tabs */}
          <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
            {datasetTabs.map(tab => (
              <button
                key={tab.key}
                onClick={() => { setActiveTab(tab.key); setSelectedModel(null); }}
                style={{
                  flex: 1, padding: "12px 16px", borderRadius: 8, cursor: "pointer",
                  border: activeTab === tab.key ? "2px solid #4f46e5" : "1px solid #d1d5db",
                  background: activeTab === tab.key ? "#eef2ff" : "#fff",
                  textAlign: "left",
                }}
              >
                <div style={{ fontSize: 14, fontWeight: 600, color: activeTab === tab.key ? "#4f46e5" : "#374151" }}>
                  {tab.label}
                </div>
                <div style={{ fontSize: 11, color: "#9ca3af", marginTop: 2 }}>{tab.desc}</div>
                {data[tab.key] && !data[tab.key].error && (
                  <div style={{ fontSize: 11, color: "#6b7280", marginTop: 4 }}>
                    {data[tab.key].dataset_size} resumes · {data[tab.key].categories?.length} categories
                  </div>
                )}
              </button>
            ))}
          </div>

          {!currentData || currentData.error ? (
            <div className="card" style={{ textAlign: "center", padding: 30, color: "#6b7280" }}>
              <p>{currentData?.error || "No data for this dataset. Click Train Models."}</p>
            </div>
          ) : (
            <>
              {/* Dataset info */}
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 20 }}>
                <InfoCard label="Dataset Size" value={currentData.dataset_size} />
                <InfoCard label="Training Set" value={currentData.train_size} />
                <InfoCard label="Test Set" value={currentData.test_size} />
                <InfoCard label="Features" value={currentData.feature_count} />
              </div>

              {/* Best model highlight */}
              {bestModel && (
                <div className="card" style={{ marginBottom: 20, background: "#f0fdf4", borderColor: "#bbf7d0" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <span style={{ fontSize: 28 }}>🏆</span>
                    <div>
                      <div style={{ fontSize: 15, fontWeight: 700, color: "#059669" }}>Best Model: {bestModel}</div>
                      <div style={{ fontSize: 13, color: "#6b7280" }}>
                        F1: {currentData.results[bestModel].f1_score}% | Accuracy: {currentData.results[bestModel].accuracy}% | CV: {currentData.results[bestModel].cv_mean_accuracy}% (±{currentData.results[bestModel].cv_std}%)
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Metric comparison bars */}
              <div className="card" style={{ marginBottom: 20 }}>
                <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 16 }}>Model Comparison</h3>
                {metrics.map(metric => (
                  <div key={metric} style={{ marginBottom: 20 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8, color: "#374151" }}>{metricLabels[metric]}</div>
                    {models.map(model => {
                      const value = currentData.results[model][metric];
                      const isMax = value === Math.max(...models.map(m => currentData.results[m][metric]));
                      return (
                        <div key={model} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
                          <span style={{ fontSize: 12, width: 100, textAlign: "right", color: "#6b7280", flexShrink: 0 }}>{model}</span>
                          <div style={{ flex: 1, height: 20, background: "#f3f4f6", borderRadius: 4, overflow: "hidden" }}>
                            <div style={{
                              height: "100%", width: `${value}%`,
                              background: modelColors[model],
                              borderRadius: 4, transition: "width 0.5s ease",
                              opacity: isMax ? 1 : 0.6,
                            }} />
                          </div>
                          <span style={{ fontSize: 12, fontWeight: isMax ? 700 : 400, color: isMax ? modelColors[model] : "#6b7280", width: 50, flexShrink: 0 }}>
                            {value}%
                          </span>
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>

              {/* Training time & CV */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20 }}>
                <div className="card">
                  <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>Training Time</h3>
                  {models.map(model => (
                    <div key={model} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #f3f4f6", fontSize: 13 }}>
                      <span style={{ color: "#374151" }}>{model}</span>
                      <span style={{ fontWeight: 600, color: modelColors[model] }}>{currentData.results[model].train_time_seconds}s</span>
                    </div>
                  ))}
                </div>
                <div className="card">
                  <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>Cross-Validation (5-Fold)</h3>
                  {models.map(model => (
                    <div key={model} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #f3f4f6", fontSize: 13 }}>
                      <span style={{ color: "#374151" }}>{model}</span>
                      <span style={{ fontWeight: 600, color: modelColors[model] }}>
                        {currentData.results[model].cv_mean_accuracy}% <span style={{ fontWeight: 400, color: "#9ca3af" }}>±{currentData.results[model].cv_std}%</span>
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Per-model detail */}
              <div className="card" style={{ marginBottom: 20 }}>
                <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>Per-Class Metrics</h3>
                <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
                  {models.map(model => (
                    <button
                      key={model}
                      onClick={() => setSelectedModel(selectedModel === model ? null : model)}
                      style={{
                        padding: "6px 14px", borderRadius: 6, fontSize: 13, fontWeight: 500, cursor: "pointer",
                        border: selectedModel === model ? `2px solid ${modelColors[model]}` : "1px solid #d1d5db",
                        background: selectedModel === model ? modelColors[model] + "10" : "#fff",
                        color: selectedModel === model ? modelColors[model] : "#6b7280",
                      }}
                    >
                      {model}
                    </button>
                  ))}
                </div>

                {selectedModel && currentData.results[selectedModel].per_class_report && (
                  <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
                      <thead>
                        <tr style={{ borderBottom: "2px solid #e5e7eb" }}>
                          <th style={{ textAlign: "left", padding: "8px 10px", color: "#6b7280" }}>Category</th>
                          <th style={{ textAlign: "right", padding: "8px 10px", color: "#6b7280" }}>Precision</th>
                          <th style={{ textAlign: "right", padding: "8px 10px", color: "#6b7280" }}>Recall</th>
                          <th style={{ textAlign: "right", padding: "8px 10px", color: "#6b7280" }}>F1 Score</th>
                          <th style={{ textAlign: "right", padding: "8px 10px", color: "#6b7280" }}>Support</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(currentData.results[selectedModel].per_class_report)
                          .sort((a, b) => b[1].f1_score - a[1].f1_score)
                          .map(([cat, m]) => (
                            <tr key={cat} style={{ borderBottom: "1px solid #f3f4f6" }}>
                              <td style={{ padding: "7px 10px", fontWeight: 500 }}>{cat}</td>
                              <td style={{ padding: "7px 10px", textAlign: "right", color: colorByScore(m.precision) }}>{m.precision}%</td>
                              <td style={{ padding: "7px 10px", textAlign: "right", color: colorByScore(m.recall) }}>{m.recall}%</td>
                              <td style={{ padding: "7px 10px", textAlign: "right", fontWeight: 600, color: colorByScore(m.f1_score) }}>{m.f1_score}%</td>
                              <td style={{ padding: "7px 10px", textAlign: "right", color: "#9ca3af" }}>{m.support}</td>
                            </tr>
                          ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* Confusion Matrix */}
              {selectedModel && currentData.results[selectedModel].confusion_matrix && (
                <div className="card">
                  <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12 }}>
                    Confusion Matrix — {selectedModel}
                  </h3>
                  <div style={{ overflowX: "auto" }}>
                    <div style={{ display: "inline-block", minWidth: "fit-content" }}>
                      <div style={{ display: "flex", marginBottom: 2 }}>
                        <div style={{ width: 80, flexShrink: 0 }} />
                        {currentData.categories.map((cat, i) => (
                          <div key={i} style={{
                            width: 28, height: 60, fontSize: 9, color: "#6b7280",
                            display: "flex", alignItems: "flex-end", justifyContent: "center",
                            transform: "rotate(-45deg)", transformOrigin: "center",
                            whiteSpace: "nowrap", overflow: "hidden",
                          }}>
                            {cat.slice(0, 6)}
                          </div>
                        ))}
                      </div>
                      {currentData.results[selectedModel].confusion_matrix.map((row, i) => {
                        const maxVal = Math.max(...row);
                        return (
                          <div key={i} style={{ display: "flex", marginBottom: 1 }}>
                            <div style={{
                              width: 80, flexShrink: 0, fontSize: 9, color: "#6b7280",
                              display: "flex", alignItems: "center", justifyContent: "flex-end",
                              paddingRight: 6, overflow: "hidden", whiteSpace: "nowrap",
                            }}>
                              {currentData.categories[i]?.slice(0, 10)}
                            </div>
                            {row.map((val, j) => {
                              const intensity = maxVal > 0 ? val / maxVal : 0;
                              const isDiagonal = i === j;
                              return (
                                <div key={j} style={{
                                  width: 28, height: 28, fontSize: 9, fontWeight: isDiagonal ? 700 : 400,
                                  display: "flex", alignItems: "center", justifyContent: "center",
                                  background: isDiagonal
                                    ? `rgba(79, 70, 229, ${0.1 + intensity * 0.7})`
                                    : val > 0 ? `rgba(239, 68, 68, ${intensity * 0.3})` : "#fafafa",
                                  color: intensity > 0.5 ? "#fff" : "#374151",
                                  borderRadius: 2,
                                }}>
                                  {val > 0 ? val : ""}
                                </div>
                              );
                            })}
                          </div>
                        );
                      })}
                      <div style={{ fontSize: 10, color: "#9ca3af", marginTop: 8 }}>
                        Rows = Actual | Columns = Predicted | Diagonal = Correct
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}

function InfoCard({ label, value }) {
  return (
    <div className="card" style={{ textAlign: "center" }}>
      <div style={{ fontSize: 12, color: "#6b7280", marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 700, color: "#1a1a2e" }}>{value?.toLocaleString()}</div>
    </div>
  );
}

function colorByScore(score) {
  if (score >= 80) return "#059669";
  if (score >= 60) return "#d97706";
  return "#dc2626";
}
