"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type Entry = {
  id: string;
  type: string;
  data: Record<string, unknown>;
  tags: string[];
  created_at: string;
  updated_at: string;
};

type Variant = {
  id: string;
  name: string;
  sections: string[];
  has_layout: boolean;
  created_at: string;
  updated_at: string;
};

type Profile = {
  data: {
    personal?: { full_name?: string };
    links?: { email?: string; github?: string; linkedin?: string };
    content?: { summary?: string };
  };
};

function entryTitle(e: Entry): string {
  const d = e.data || {};
  return (
    (d.role as string) ||
    (d.title as string) ||
    (d.name as string) ||
    (d.degree as string) ||
    (d.category as string) ||
    e.type
  );
}

function entrySubtitle(e: Entry): string {
  const d = e.data || {};
  return (
    (d.company as string) ||
    (d.organization as string) ||
    (d.school as string) ||
    (d.issuer as string) ||
    ""
  );
}

const TYPE_COLORS: Record<string, string> = {
  experience: "#4aa7ff",
  education: "#7c5cff",
  project: "#ff9f40",
  publication: "#4caf50",
  skill: "#ff4d6d",
  award: "#ffd640",
  volunteering: "#00bcd4",
  certification: "#9c27b0",
  talk: "#e91e63",
  language: "#3f51b5",
  reference: "#795548",
};

export default function OverviewPage() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [variants, setVariants] = useState<Variant[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [health, setHealth] = useState<string>("checking...");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [entriesRes, variantsRes, profileRes, healthRes] = await Promise.all([
          fetch("/api/entries", { cache: "no-store" }),
          fetch("/api/variants", { cache: "no-store" }),
          fetch("/api/profile", { cache: "no-store" }),
          fetch("/api/health", { cache: "no-store" }),
        ]);
        
        setEntries(await entriesRes.json());
        setVariants(await variantsRes.json());
        setProfile(await profileRes.json());
        const healthData = await healthRes.json();
        setHealth(healthData.status || "ok");
      } catch (e) {
        setHealth("error");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Group entries by type
  const entriesByType = entries.reduce((acc, e) => {
    acc[e.type] = (acc[e.type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // Recent entries (last 5)
  const recentEntries = [...entries]
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, 5);

  // Profile completeness
  const profileData = profile?.data || {};
  const profileScore = [
    profileData.personal?.full_name,
    profileData.links?.email,
    profileData.links?.github,
    profileData.links?.linkedin,
    profileData.content?.summary,
  ].filter(Boolean).length;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20, height: "100%", overflow: "auto", paddingRight: 8 }}>
      {/* Header */}
      <div>
        <h1 style={{ margin: 0, fontSize: 26, letterSpacing: -0.5 }}>Overview</h1>
        <div style={{ fontSize: 13, color: "rgba(255,255,255,0.5)", marginTop: 6 }}>
          Your CV dashboard at a glance
        </div>
      </div>

      {/* Stats Row */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: 12 }}>
        <div className="card" style={{ padding: 16 }}>
          <div style={{ fontSize: 32, fontWeight: 700, color: "#7c5cff" }}>{entries.length}</div>
          <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>Total Entries</div>
        </div>
        <div className="card" style={{ padding: 16 }}>
          <div style={{ fontSize: 32, fontWeight: 700, color: "#2dd4bf" }}>{variants.length}</div>
          <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>CV Variants</div>
        </div>
        <div className="card" style={{ padding: 16 }}>
          <div style={{ fontSize: 32, fontWeight: 700, color: "#4aa7ff" }}>{Object.keys(entriesByType).length}</div>
          <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>Entry Types</div>
        </div>
        <div className="card" style={{ padding: 16 }}>
          <div style={{ fontSize: 32, fontWeight: 700, color: profileScore >= 4 ? "#4caf50" : "#ff9f40" }}>{profileScore}/5</div>
          <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>Profile Complete</div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="overviewGrid">
        {/* Variants */}
        <div className="card" style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ padding: 16, borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ fontWeight: 700, fontSize: 14 }}>CV Variants</div>
              <Link href="/variants" className="btn" style={{ fontSize: 11, padding: "4px 10px" }}>
                Manage
              </Link>
            </div>
          </div>
          <div style={{ padding: 12, flex: 1, overflowY: "auto", maxHeight: 280 }}>
            {variants.length === 0 ? (
              <div style={{ textAlign: "center", padding: 24, color: "rgba(255,255,255,0.4)", fontSize: 12 }}>
                No variants yet.{" "}
                <Link href="/variants" style={{ color: "#7c5cff" }}>Create one</Link>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {variants.map((v) => (
                  <div
                    key={v.id}
                    style={{
                      padding: 12,
                      background: "rgba(255,255,255,0.03)",
                      border: "1px solid rgba(255,255,255,0.08)",
                      borderRadius: 10,
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: 13 }}>{v.name}</div>
                        <div style={{ fontSize: 11, color: "rgba(255,255,255,0.4)", marginTop: 2 }}>
                          {v.sections.length} sections
                        </div>
                      </div>
                      <div style={{ display: "flex", gap: 6 }}>
                        <a
                          href={`/api/variants/${v.id}/preview/pdf`}
                          target="_blank"
                          className="btn"
                          style={{ fontSize: 10, padding: "3px 8px" }}
                        >
                          PDF
                        </a>
                        <a
                          href={`/api/variants/${v.id}/preview/html`}
                          target="_blank"
                          className="btn"
                          style={{ fontSize: 10, padding: "3px 8px" }}
                        >
                          HTML
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recent Entries */}
        <div className="card" style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ padding: 16, borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ fontWeight: 700, fontSize: 14 }}>Recent Entries</div>
              <Link href="/entries" className="btn" style={{ fontSize: 11, padding: "4px 10px" }}>
                View All
              </Link>
            </div>
          </div>
          <div style={{ padding: 12, flex: 1, overflowY: "auto", maxHeight: 280 }}>
            {recentEntries.length === 0 ? (
              <div style={{ textAlign: "center", padding: 24, color: "rgba(255,255,255,0.4)", fontSize: 12 }}>
                No entries yet.{" "}
                <Link href="/entries" style={{ color: "#7c5cff" }}>Add one</Link>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {recentEntries.map((e) => (
                  <Link
                    key={e.id}
                    href="/entries"
                    style={{
                      padding: 10,
                      background: "rgba(255,255,255,0.03)",
                      border: "1px solid rgba(255,255,255,0.08)",
                      borderRadius: 10,
                      display: "block",
                      textDecoration: "none",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <div
                        style={{
                          width: 8,
                          height: 8,
                          borderRadius: "50%",
                          background: TYPE_COLORS[e.type] || "#888",
                          flexShrink: 0,
                        }}
                      />
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: 600, fontSize: 12, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {entryTitle(e)}
                        </div>
                        {entrySubtitle(e) && (
                          <div style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", marginTop: 1 }}>
                            {entrySubtitle(e)}
                          </div>
                        )}
                      </div>
                      <span style={{
                        fontSize: 9,
                        padding: "2px 6px",
                        background: `${TYPE_COLORS[e.type] || "#888"}30`,
                        borderRadius: 4,
                        color: "rgba(255,255,255,0.7)",
                        flexShrink: 0,
                      }}>
                        {e.type}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Entry Types Distribution */}
      <div className="card">
        <div style={{ padding: 16, borderBottom: "1px solid rgba(255,255,255,0.08)" }}>
          <div style={{ fontWeight: 700, fontSize: 14 }}>Entries by Type</div>
        </div>
        <div style={{ padding: 16 }}>
          {Object.keys(entriesByType).length === 0 ? (
            <div style={{ textAlign: "center", padding: 16, color: "rgba(255,255,255,0.4)", fontSize: 12 }}>
              Add entries to see the distribution
            </div>
          ) : (
            <div style={{ display: "flex", flexWrap: "wrap", gap: 10 }}>
              {Object.entries(entriesByType)
                .sort((a, b) => b[1] - a[1])
                .map(([type, count]) => (
                  <div
                    key={type}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      padding: "8px 12px",
                      background: `${TYPE_COLORS[type] || "#888"}15`,
                      border: `1px solid ${TYPE_COLORS[type] || "#888"}40`,
                      borderRadius: 8,
                    }}
                  >
                    <div
                      style={{
                        width: 10,
                        height: 10,
                        borderRadius: "50%",
                        background: TYPE_COLORS[type] || "#888",
                      }}
                    />
                    <span style={{ fontSize: 12, fontWeight: 500 }}>{type}</span>
                    <span style={{
                      fontSize: 11,
                      fontWeight: 700,
                      color: TYPE_COLORS[type] || "#888",
                    }}>
                      {count}
                    </span>
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions & Status */}
      <div className="overviewGrid">
        {/* Quick Start */}
        <div className="card">
          <div style={{ padding: 16 }}>
            <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 12 }}>Quick Start</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: 12, color: "rgba(255,255,255,0.6)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ 
                  width: 20, height: 20, borderRadius: "50%", 
                  background: entries.length > 0 ? "rgba(76, 175, 80, 0.2)" : "rgba(255,255,255,0.1)",
                  color: entries.length > 0 ? "#4caf50" : "rgba(255,255,255,0.4)",
                  display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11
                }}>
                  {entries.length > 0 ? "✓" : "1"}
                </span>
                <span style={{ color: entries.length > 0 ? "rgba(255,255,255,0.4)" : "inherit" }}>
                  Add entries (experiences, education, projects...)
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ 
                  width: 20, height: 20, borderRadius: "50%", 
                  background: profileScore >= 3 ? "rgba(76, 175, 80, 0.2)" : "rgba(255,255,255,0.1)",
                  color: profileScore >= 3 ? "#4caf50" : "rgba(255,255,255,0.4)",
                  display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11
                }}>
                  {profileScore >= 3 ? "✓" : "2"}
                </span>
                <span style={{ color: profileScore >= 3 ? "rgba(255,255,255,0.4)" : "inherit" }}>
                  Complete your profile (name, contact, summary)
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ 
                  width: 20, height: 20, borderRadius: "50%", 
                  background: variants.length > 0 ? "rgba(76, 175, 80, 0.2)" : "rgba(255,255,255,0.1)",
                  color: variants.length > 0 ? "#4caf50" : "rgba(255,255,255,0.4)",
                  display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11
                }}>
                  {variants.length > 0 ? "✓" : "3"}
                </span>
                <span style={{ color: variants.length > 0 ? "rgba(255,255,255,0.4)" : "inherit" }}>
                  Create a CV variant and arrange sections
                </span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ 
                  width: 20, height: 20, borderRadius: "50%", 
                  background: "rgba(255,255,255,0.1)",
                  color: "rgba(255,255,255,0.4)",
                  display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11
                }}>
                  4
                </span>
                Export to PDF, HTML, or LinkedIn format
              </div>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="card">
          <div style={{ padding: 16 }}>
            <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 12 }}>System Status</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 12, color: "rgba(255,255,255,0.6)" }}>Backend API</span>
                <span className="badge" style={{ 
                  background: health === "ok" ? "rgba(76, 175, 80, 0.15)" : "rgba(255, 77, 109, 0.15)",
                  borderColor: health === "ok" ? "rgba(76, 175, 80, 0.3)" : "rgba(255, 77, 109, 0.3)",
                  color: health === "ok" ? "#4caf50" : "#ff4d6d",
                  fontSize: 11,
                }}>
                  {health}
                </span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 12, color: "rgba(255,255,255,0.6)" }}>Database</span>
                <span className="badge" style={{ fontSize: 11 }}>SQLite (local)</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 12, color: "rgba(255,255,255,0.6)" }}>PDF Engine</span>
                <span className="badge" style={{ fontSize: 11 }}>LaTeX</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
