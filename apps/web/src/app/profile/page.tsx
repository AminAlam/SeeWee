"use client";

import { useEffect, useMemo, useState } from "react";

type Profile = {
  data: {
    personal?: { full_name?: string };
    links?: {
      email?: string;
      phone?: string;
      address?: string;
      github?: string;
      linkedin?: string;
    };
    content?: { summary?: string; tagline?: string };
  };
  created_at: string;
  updated_at: string;
};

const empty: Profile = {
  data: { personal: { full_name: "" }, links: {}, content: { summary: "", tagline: "" } },
  created_at: "",
  updated_at: ""
};

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile>(empty);
  const [error, setError] = useState<string | null>(null);
  const [savedAt, setSavedAt] = useState<string | null>(null);

  const data = profile.data ?? {};
  const personal = data.personal ?? {};
  const links = data.links ?? {};
  const content = data.content ?? {};

  async function load() {
    const res = await fetch("/api/profile", { cache: "no-store" });
    if (!res.ok) throw new Error(`Load failed: ${res.status}`);
    const json = (await res.json()) as Profile;
    setProfile(json);
  }

  async function save() {
    setError(null);
    const res = await fetch("/api/profile", {
      method: "PUT",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ data: profile.data })
    });
    if (!res.ok) {
      setError(`Save failed: ${res.status}`);
      return;
    }
    const json = (await res.json()) as Profile;
    setProfile(json);
    setSavedAt(new Date().toISOString());
  }

  useEffect(() => {
    load().catch((e) => setError(String(e)));
  }, []);

  const completeness = useMemo(() => {
    const score =
      (personal.full_name ? 1 : 0) +
      (links.email ? 1 : 0) +
      (links.linkedin ? 1 : 0) +
      (links.github ? 1 : 0) +
      (content.summary ? 1 : 0);
    return `${score}/5`;
  }, [personal.full_name, links.email, links.linkedin, links.github, content.summary]);

  return (
    <div className="stack" style={{ gap: 16 }}>
      <div>
        <h1 style={{ margin: 0, letterSpacing: -0.5, fontSize: 24 }}>Profile</h1>
        <div className="muted" style={{ marginTop: 6, fontSize: 13 }}>
          Used in LaTeX + HTML exports. Completeness: <span className="badge">{completeness}</span>
        </div>
      </div>

      <div className="card">
        <div style={{ padding: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16, flexWrap: "wrap", gap: 10 }}>
            <div className="muted" style={{ fontSize: 12 }}>
              Changes auto-reflect in preview after save.
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn" onClick={() => load().catch((e) => setError(String(e)))}>
                Reload
              </button>
              <button className="btn btnPrimary" onClick={() => save().catch((e) => setError(String(e)))}>
                Save
              </button>
            </div>
          </div>

          {error && <div className="error" style={{ marginBottom: 16 }}>{error}</div>}
          {savedAt && <div className="muted" style={{ marginBottom: 16, fontSize: 12 }}>Saved at {savedAt}</div>}

          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: 20 
          }}>
            <div className="stack" style={{ gap: 12 }}>
              <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>Personal</div>
              <label className="label">
                Full name
                <input
                  className="input"
                  value={personal.full_name ?? ""}
                  onChange={(e) =>
                    setProfile((p) => ({
                      ...p,
                      data: { ...p.data, personal: { ...(p.data.personal ?? {}), full_name: e.target.value } }
                    }))
                  }
                />
              </label>

              <label className="label">
                Tagline (HTML)
                <input
                  className="input"
                  value={content.tagline ?? ""}
                  onChange={(e) =>
                    setProfile((p) => ({
                      ...p,
                      data: { ...p.data, content: { ...(p.data.content ?? {}), tagline: e.target.value } }
                    }))
                  }
                  placeholder="Senior Engineer • ML • Systems"
                />
              </label>

              <label className="label">
                Executive summary
                <textarea
                  className="textarea"
                  value={content.summary ?? ""}
                  onChange={(e) =>
                    setProfile((p) => ({
                      ...p,
                      data: { ...p.data, content: { ...(p.data.content ?? {}), summary: e.target.value } }
                    }))
                  }
                  style={{ minHeight: 100 }}
                />
              </label>
            </div>

            <div className="stack" style={{ gap: 12 }}>
              <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>Links & Contact</div>
              <label className="label">
                Email
                <input
                  className="input"
                  value={links.email ?? ""}
                  onChange={(e) =>
                    setProfile((p) => ({
                      ...p,
                      data: { ...p.data, links: { ...(p.data.links ?? {}), email: e.target.value } }
                    }))
                  }
                />
              </label>
              <label className="label">
                Phone
                <input
                  className="input"
                  value={links.phone ?? ""}
                  onChange={(e) =>
                    setProfile((p) => ({
                      ...p,
                      data: { ...p.data, links: { ...(p.data.links ?? {}), phone: e.target.value } }
                    }))
                  }
                />
              </label>
              <label className="label">
                Address
                <input
                  className="input"
                  value={links.address ?? ""}
                  onChange={(e) =>
                    setProfile((p) => ({
                      ...p,
                      data: { ...p.data, links: { ...(p.data.links ?? {}), address: e.target.value } }
                    }))
                  }
                />
              </label>
              <label className="label">
                GitHub URL
                <input
                  className="input"
                  value={links.github ?? ""}
                  onChange={(e) =>
                    setProfile((p) => ({
                      ...p,
                      data: { ...p.data, links: { ...(p.data.links ?? {}), github: e.target.value } }
                    }))
                  }
                  placeholder="https://github.com/username"
                />
              </label>
              <label className="label">
                LinkedIn URL
                <input
                  className="input"
                  value={links.linkedin ?? ""}
                  onChange={(e) =>
                    setProfile((p) => ({
                      ...p,
                      data: { ...p.data, links: { ...(p.data.links ?? {}), linkedin: e.target.value } }
                    }))
                  }
                  placeholder="https://linkedin.com/in/..."
                />
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
