async function getApiHealth() {
  const baseUrl = process.env.API_BASE_URL ?? "http://localhost:8000";
  const res = await fetch(`${baseUrl}/health`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API health check failed: ${res.status}`);
  }
  return (await res.json()) as { status: string };
}

export default async function HomePage() {
  const health = await getApiHealth();

  return (
    <div className="stack">
      <div>
        <h1 style={{ margin: 0, letterSpacing: -0.3 }}>Dashboard</h1>
        <div className="muted" style={{ marginTop: 6 }}>
          Build a canonical CV database, then generate variants and exports.
        </div>
      </div>

      <div className="card">
        <div className="cardInner row" style={{ justifyContent: "space-between" }}>
          <div>
            <div style={{ fontWeight: 800 }}>Backend</div>
            <div className="muted" style={{ marginTop: 4, fontSize: 12 }}>
              FastAPI + SQLite (local volume)
            </div>
          </div>
          <span className="badge">health: {health.status}</span>
        </div>
      </div>

      <div className="split">
        <div className="card">
          <div className="cardInner stack">
            <div style={{ fontWeight: 800 }}>Start here</div>
            <div className="muted" style={{ fontSize: 12, lineHeight: 1.6 }}>
              1) Add Entries (experiences/projects/publications)\n
              2) Create a Variant (rules + section ordering)\n
              3) Preview + Export (LaTeX / HTML / LinkedIn)
            </div>
            <div className="row">
              <a className="btn btnPrimary" href="/entries">
                Go to Entries
              </a>
              <a className="btn" href="/variants">
                Go to Variants
              </a>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="cardInner stack">
            <div style={{ fontWeight: 800 }}>Export mindset</div>
            <div className="muted" style={{ fontSize: 12, lineHeight: 1.6 }}>
              Keep entries rich and reusable. Variants should be lightweight (tags + limits), and exporters should be
              deterministic so a “submitted CV” can be reproduced.
            </div>
            <details>
              <summary style={{ cursor: "pointer", fontWeight: 700 }}>LLM features (optional)</summary>
              <div className="muted" style={{ fontSize: 12, marginTop: 8, lineHeight: 1.6 }}>
                The API already exposes rewrite/keywords/consistency endpoints (stubbed). Later we can wire hosted
                providers and/or Ollama.
              </div>
            </details>
          </div>
        </div>
      </div>
    </div>
  );
}


