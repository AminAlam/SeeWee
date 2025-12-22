"use client";

import { useCallback, useEffect, useState } from "react";

type Entry = {
  id: string;
  type: string;
  data: Record<string, unknown>;
  tags: string[];
  created_at: string;
  updated_at: string;
};

type SchemaProperty = {
  type: string;
  title?: string;
  description?: string;
  default?: unknown;
  format?: string;
  items?: { type: string };
};

type Schema = {
  title: string;
  type: string;
  properties: Record<string, SchemaProperty>;
  required?: string[];
};

const TYPE_COLORS: Record<string, string> = {
  experience: "rgba(74, 167, 255, 0.2)",
  education: "rgba(124, 92, 255, 0.2)",
  project: "rgba(255, 159, 64, 0.2)",
  publication: "rgba(76, 175, 80, 0.2)",
  skill: "rgba(255, 77, 109, 0.2)",
  award: "rgba(255, 214, 64, 0.2)",
  volunteering: "rgba(0, 188, 212, 0.2)",
  certification: "rgba(156, 39, 176, 0.2)",
  talk: "rgba(233, 30, 99, 0.2)",
  language: "rgba(63, 81, 181, 0.2)",
  reference: "rgba(121, 85, 72, 0.2)",
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
    (d.venue as string) ||
    ""
  );
}

function FormField({ propKey, prop, value, onChange }: {
  propKey: string;
  prop: SchemaProperty;
  value: unknown;
  onChange: (key: string, value: unknown) => void;
}) {
  const label = prop.title || propKey;
  
  if (prop.type === "array" && prop.items?.type === "string") {
    const arrValue = Array.isArray(value) ? value : [];
    return (
      <label className="label">
        <span style={{ fontSize: 12 }}>{label}</span>
        <textarea
          className="textarea"
          value={arrValue.join("\n")}
          onChange={(e) => onChange(propKey, e.target.value.split("\n").filter(Boolean))}
          style={{ minHeight: 80, fontSize: 12 }}
          placeholder="One item per line..."
        />
      </label>
    );
  }

  return (
    <label className="label">
      <span style={{ fontSize: 12 }}>{label}</span>
      <input
        className="input"
        type={prop.format === "date" ? "date" : "text"}
        value={(value as string) || ""}
        onChange={(e) => onChange(propKey, e.target.value)}
        style={{ fontSize: 12 }}
        placeholder={prop.description}
      />
    </label>
  );
}

export default function EntriesPage() {
  const [entries, setEntries] = useState<Entry[]>([]);
  const [schemas, setSchemas] = useState<Record<string, Schema>>({});
  const [editId, setEditId] = useState<string | null>(null);
  const [formType, setFormType] = useState<string>("experience");
  const [formData, setFormData] = useState<Record<string, unknown>>({});
  const [formTags, setFormTags] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const loadEntries = useCallback(async () => {
    const res = await fetch("/api/entries", { cache: "no-store" });
    const json = (await res.json()) as Entry[];
    setEntries(json);
  }, []);

  const loadSchemas = useCallback(async () => {
    const res = await fetch("/api/entries/types", { cache: "no-store" });
    const json = (await res.json()) as Record<string, Schema>;
    setSchemas(json);
  }, []);

  useEffect(() => {
    Promise.all([loadEntries(), loadSchemas()]).catch((e) => setError(String(e)));
  }, [loadEntries, loadSchemas]);

  async function handleSubmit() {
    setError(null);
    const url = editId ? `/api/entries/${editId}` : "/api/entries";
    const method = editId ? "PUT" : "POST";
    const res = await fetch(url, {
      method,
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        type: formType,
        data: formData,
        tags: formTags.split(",").map((t) => t.trim()).filter(Boolean),
      }),
    });
    if (!res.ok) {
      const err = await res.text();
      setError(err);
      return;
    }
    await loadEntries();
    resetForm();
  }

  async function deleteEntry(id: string) {
    await fetch(`/api/entries/${id}`, { method: "DELETE" });
    await loadEntries();
    if (editId === id) resetForm();
  }

  function editEntry(e: Entry) {
    setEditId(e.id);
    setFormType(e.type);
    setFormData(e.data || {});
    setFormTags((e.tags || []).join(", "));
  }

  function resetForm() {
    setEditId(null);
    setFormData({});
    setFormTags("");
  }

  function handleFieldChange(key: string, value: unknown) {
    setFormData({ ...formData, [key]: value });
  }

  const activeSchema = schemas[formType];
  const types = Object.keys(schemas);
  const filteredEntries = entries.filter((e) => {
    if (filterType !== "all" && e.type !== filterType) return false;
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const title = entryTitle(e).toLowerCase();
      const subtitle = entrySubtitle(e).toLowerCase();
      return title.includes(q) || subtitle.includes(q);
    }
    return true;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 12, overflow: "hidden" }}>
      {/* Header */}
      <div style={{ flexShrink: 0 }}>
        <h1 style={{ margin: 0, fontSize: 22, letterSpacing: -0.5 }}>Entries</h1>
        <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", marginTop: 4 }}>
          Building blocks for your CV
        </div>
      </div>

      {error && <div className="error" style={{ flexShrink: 0 }}>{error}</div>}

      {/* Main area */}
      <div style={{ flex: 1, display: "grid", gridTemplateColumns: "260px 1fr", gap: 12, minHeight: 0, overflow: "hidden" }}>
        {/* Form */}
        <div style={{ display: "flex", flexDirection: "column", gap: 8, overflow: "hidden" }}>
          <div className="card" style={{ flexShrink: 0 }}>
            <div style={{ padding: 12 }}>
              <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 10 }}>
                {editId ? "Edit Entry" : "New Entry"}
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <label className="label">
                  <span style={{ fontSize: 12 }}>Type</span>
                  <select
                    className="select"
                    value={formType}
                    onChange={(e) => {
                      setFormType(e.target.value);
                      setFormData({});
                    }}
                    style={{ fontSize: 12 }}
                    disabled={!!editId}
                  >
                    {types.map((t) => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </label>
                <label className="label">
                  <span style={{ fontSize: 12 }}>Tags</span>
                  <input
                    className="input"
                    value={formTags}
                    onChange={(e) => setFormTags(e.target.value)}
                    placeholder="comma, separated"
                    style={{ fontSize: 12 }}
                  />
                </label>
              </div>
            </div>
          </div>
          <div className="card" style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column" }}>
            <div style={{ flex: 1, overflowY: "auto", padding: 12 }}>
              {activeSchema && (
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {Object.entries(activeSchema.properties).map(([key, prop]) => (
                    <FormField
                      key={key}
                      propKey={key}
                      prop={prop}
                      value={formData[key]}
                      onChange={handleFieldChange}
                    />
                  ))}
                </div>
              )}
            </div>
            <div style={{ padding: 12, borderTop: "1px solid rgba(255,255,255,0.1)", display: "flex", gap: 8, flexShrink: 0 }}>
              <button className="btn btnPrimary" onClick={handleSubmit} style={{ flex: 1, fontSize: 12 }}>
                {editId ? "Update" : "Create"}
              </button>
              {editId && (
                <button className="btn" onClick={resetForm} style={{ fontSize: 12 }}>Cancel</button>
              )}
            </div>
          </div>
        </div>

        {/* List */}
        <div style={{ display: "flex", flexDirection: "column", gap: 8, overflow: "hidden" }}>
          <div style={{ 
            flexShrink: 0, 
            display: "flex", 
            gap: 8, 
            alignItems: "center",
            flexWrap: "wrap",
          }}>
            <input
              className="input"
              placeholder="Search..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ width: 140, padding: "6px 10px", fontSize: 12 }}
            />
            <select
              className="select"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              style={{ width: 120, padding: "6px 10px", fontSize: 12 }}
            >
              <option value="all">All types</option>
              {types.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            <div style={{ marginLeft: "auto", fontSize: 11, color: "rgba(255,255,255,0.4)" }}>
              {filteredEntries.length} entries
            </div>
          </div>
          <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 8, paddingRight: 4 }}>
            {filteredEntries.length === 0 ? (
              <div style={{ 
                textAlign: "center", 
                padding: 40, 
                color: "rgba(255,255,255,0.4)",
                border: "1px dashed rgba(255,255,255,0.15)",
                borderRadius: 10,
              }}>
                {entries.length === 0 ? "No entries yet. Create one!" : "No matching entries"}
              </div>
            ) : (
              filteredEntries.map((entry) => (
                <div
                  key={entry.id}
                  onClick={() => editEntry(entry)}
                  style={{
                    padding: 12,
                    background: editId === entry.id ? "rgba(124, 92, 255, 0.15)" : "rgba(255,255,255,0.03)",
                    border: editId === entry.id ? "1px solid rgba(124, 92, 255, 0.4)" : "1px solid rgba(255,255,255,0.08)",
                    borderRadius: 10,
                    cursor: "pointer",
                    transition: "all 0.15s ease",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 10 }}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                        <span style={{
                          fontSize: 10,
                          padding: "2px 8px",
                          background: TYPE_COLORS[entry.type] || "rgba(255,255,255,0.1)",
                          borderRadius: 4,
                          fontWeight: 500,
                        }}>
                          {entry.type}
                        </span>
                        {entry.tags.length > 0 && (
                          <span style={{ fontSize: 10, color: "rgba(255,255,255,0.4)" }}>
                            {entry.tags.join(", ")}
                          </span>
                        )}
                      </div>
                      <div style={{ fontWeight: 600, fontSize: 13, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {entryTitle(entry)}
                      </div>
                      {entrySubtitle(entry) && (
                        <div style={{ fontSize: 11, color: "rgba(255,255,255,0.5)", marginTop: 2 }}>
                          {entrySubtitle(entry)}
                        </div>
                      )}
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); deleteEntry(entry.id); }}
                      style={{
                        padding: "4px 8px",
                        fontSize: 11,
                        background: "rgba(255,77,109,0.1)",
                        border: "1px solid rgba(255,77,109,0.3)",
                        borderRadius: 6,
                        color: "#ff4d6d",
                        cursor: "pointer",
                        flexShrink: 0,
                      }}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
