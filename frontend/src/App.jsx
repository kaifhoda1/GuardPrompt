import { useState, useEffect } from "react"
import axios from "axios"

const API = "http://localhost:8000/api/v1"

function DecisionBadge({ decision }) {
  const colors = {
    block: { bg: "#ff4444", label: "BLOCK" },
    flag: { bg: "#ffaa00", label: "FLAG" },
    pass: { bg: "#00cc66", label: "PASS" }
  }
  const c = colors[decision] || colors.pass
  return (
    <span style={{
      background: c.bg,
      color: "white",
      padding: "2px 10px",
      borderRadius: "4px",
      fontWeight: "bold",
      fontSize: "12px"
    }}>{c.label}</span>
  )
}

function StatCard({ label, value, color }) {
  return (
    <div style={{
      background: "#1a1a2e",
      border: `1px solid ${color}`,
      borderRadius: "8px",
      padding: "20px",
      textAlign: "center",
      minWidth: "140px"
    }}>
      <div style={{ fontSize: "36px", fontWeight: "bold", color }}>{value}</div>
      <div style={{ color: "#888", marginTop: "4px", fontSize: "14px" }}>{label}</div>
    </div>
  )
}

export default function App() {
  const [stats, setStats] = useState(null)
  const [logs, setLogs] = useState([])
  const [prompt, setPrompt] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const fetchData = async () => {
    try {
      const [s, l] = await Promise.all([
        axios.get(`${API}/stats`),
        axios.get(`${API}/logs`)
      ])
      setStats(s.data)
      setLogs(l.data)
    } catch (e) {
      console.error("Backend not reachable", e)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  const analyzePrompt = async () => {
    if (!prompt.trim()) return
    setLoading(true)
    setResult(null)
    try {
      const res = await axios.post(`${API}/analyze`, {
        prompt,
        use_semantic: false
      })
      setResult(res.data)
      fetchData()
    } catch (e) {
      console.error("Analysis failed", e)
    }
    setLoading(false)
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: "#0f0f1a",
      color: "#e0e0e0",
      fontFamily: "monospace",
      padding: "30px"
    }}>

      {/* Header */}
      <div style={{ marginBottom: "30px" }}>
        <h1 style={{ color: "#00ffcc", margin: 0, fontSize: "28px" }}>
          🛡 GuardPrompt
        </h1>
        <p style={{ color: "#666", margin: "4px 0 0 0", fontSize: "13px" }}>
          Real-time prompt injection detection dashboard
        </p>
      </div>

      {/* Stats */}
      {stats && (
        <div style={{ display: "flex", gap: "16px", marginBottom: "30px", flexWrap: "wrap" }}>
          <StatCard label="Total Requests" value={stats.total_requests} color="#00ffcc" />
          <StatCard label="Blocked" value={stats.blocked} color="#ff4444" />
          <StatCard label="Flagged" value={stats.flagged} color="#ffaa00" />
          <StatCard label="Passed" value={stats.passed} color="#00cc66" />
          <StatCard label="Avg Score" value={stats.average_score} color="#888" />
        </div>
      )}

      {/* Test Panel */}
      <div style={{
        background: "#1a1a2e",
        border: "1px solid #333",
        borderRadius: "8px",
        padding: "20px",
        marginBottom: "30px"
      }}>
        <h2 style={{ color: "#00ffcc", margin: "0 0 16px 0", fontSize: "16px" }}>
          Test a Prompt
        </h2>
        <div style={{ display: "flex", gap: "10px" }}>
          <input
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            onKeyDown={e => e.key === "Enter" && analyzePrompt()}
            placeholder="Type a prompt and press Enter or click Analyze..."
            style={{
              flex: 1,
              padding: "10px",
              background: "#0f0f1a",
              border: "1px solid #333",
              borderRadius: "6px",
              color: "#e0e0e0",
              fontFamily: "monospace",
              fontSize: "14px"
            }}
          />
          <button
            onClick={analyzePrompt}
            disabled={loading}
            style={{
              padding: "10px 20px",
              background: loading ? "#333" : "#00ffcc",
              color: "#0f0f1a",
              border: "none",
              borderRadius: "6px",
              fontWeight: "bold",
              cursor: loading ? "not-allowed" : "pointer",
              fontFamily: "monospace"
            }}
          >
            {loading ? "..." : "Analyze"}
          </button>
        </div>

        {/* Result */}
        {result && (
          <div style={{
            marginTop: "16px",
            padding: "12px",
            background: "#0f0f1a",
            borderRadius: "6px",
            border: "1px solid #333"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}>
              <DecisionBadge decision={result.decision} />
              <span style={{ color: "#888", fontSize: "13px" }}>
                Score: <strong style={{ color: "#fff" }}>{result.final_score}</strong>
              </span>
              <span style={{ color: "#888", fontSize: "13px" }}>
                Layers: <strong style={{ color: "#fff" }}>
                  {result.triggered_layers.length > 0 ? result.triggered_layers.join(", ") : "none"}
                </strong>
              </span>
            </div>
            {result.reasons.length > 0 && (
              <div style={{ color: "#ffaa00", fontSize: "13px" }}>
                {result.reasons.map((r, i) => <div key={i}>⚠ {r}</div>)}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Logs Table */}
      <div style={{
        background: "#1a1a2e",
        border: "1px solid #333",
        borderRadius: "8px",
        padding: "20px"
      }}>
        <h2 style={{ color: "#00ffcc", margin: "0 0 16px 0", fontSize: "16px" }}>
          Recent Logs
        </h2>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "13px" }}>
          <thead>
            <tr style={{ borderBottom: "1px solid #333", color: "#666" }}>
              <th style={{ textAlign: "left", padding: "8px" }}>ID</th>
              <th style={{ textAlign: "left", padding: "8px" }}>Decision</th>
              <th style={{ textAlign: "left", padding: "8px" }}>Score</th>
              <th style={{ textAlign: "left", padding: "8px" }}>Layers</th>
              <th style={{ textAlign: "left", padding: "8px" }}>Reason</th>
              <th style={{ textAlign: "left", padding: "8px" }}>Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 && (
              <tr>
                <td colSpan={6} style={{ padding: "20px", color: "#444", textAlign: "center" }}>
                  No logs yet. Send a prompt above.
                </td>
              </tr>
            )}
            {logs.map(log => (
              <tr key={log.id} style={{ borderBottom: "1px solid #222" }}>
                <td style={{ padding: "8px", color: "#666" }}>#{log.id}</td>
                <td style={{ padding: "8px" }}>
                  <DecisionBadge decision={log.decision} />
                </td>
                <td style={{ padding: "8px" }}>{log.final_score}</td>
                <td style={{ padding: "8px", color: "#888" }}>
                  {log.triggered_layers || "none"}
                </td>
                <td style={{ padding: "8px", color: "#ccc", maxWidth: "300px" }}>
                  {log.reasons ? log.reasons.slice(0, 60) + (log.reasons.length > 60 ? "..." : "") : "-"}
                </td>
                <td style={{ padding: "8px", color: "#666" }}>
                  {log.created_at ? log.created_at.slice(11, 19) : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
