"use client";

import { useEffect, useMemo, useState } from "react";

type Variant = {
  id: string;
  name: string;
  updated_at: string;
};

type Tab = "pdf" | "html";

export function PreviewPane() {
  const [variants, setVariants] = useState<Variant[]>([]);
  const [variantId, setVariantId] = useState<string>("");
  const [tab, setTab] = useState<Tab>("pdf");
  const [refreshKey, setRefreshKey] = useState(0);

  function reload() {
    setRefreshKey((k) => k + 1);
  }

  useEffect(() => {
    const saved = localStorage.getItem("seewee.activeVariantId");
    if (saved) setVariantId(saved);
  }, []);

  useEffect(() => {
    if (variantId) localStorage.setItem("seewee.activeVariantId", variantId);
  }, [variantId]);

  useEffect(() => {
    async function load() {
      const res = await fetch("/api/variants", { cache: "no-store" });
      const json = (await res.json()) as Variant[];
      setVariants(json);
      if (!variantId && json.length) setVariantId(json[0].id);
    }
    load().catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const pdfSrc = useMemo(() => (variantId ? `/api/variants/${variantId}/preview/pdf?k=${refreshKey}` : ""), [variantId, refreshKey]);
  const htmlSrc = useMemo(() => (variantId ? `/api/variants/${variantId}/preview/html?k=${refreshKey}` : ""), [variantId, refreshKey]);

  return (
    <div style={{ 
      display: "flex", 
      flexDirection: "column", 
      height: "100%",
      gap: 12,
      overflow: "hidden",
    }}>
      <div className="card" style={{ flexShrink: 0 }}>
        <div style={{ padding: 14 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <div>
              <div style={{ fontWeight: 700, fontSize: 14 }}>Live Preview</div>
              <div className="muted" style={{ fontSize: 11, marginTop: 2 }}>
                {tab === "pdf" ? "LaTeX → PDF" : "Academic Pages style"}
              </div>
            </div>
            <div style={{ display: "flex", gap: 6 }}>
              <button 
                className="btn" 
                onClick={reload} 
                title="Reload Preview"
                style={{ padding: "6px 10px", fontSize: 14 }}
              >
                ↻
              </button>
              <button 
                className={`btn ${tab === "pdf" ? "btnPrimary" : ""}`} 
                onClick={() => setTab("pdf")}
                style={{ padding: "6px 12px", fontSize: 12 }}
              >
                PDF
              </button>
              <button 
                className={`btn ${tab === "html" ? "btnPrimary" : ""}`} 
                onClick={() => setTab("html")}
                style={{ padding: "6px 12px", fontSize: 12 }}
              >
                HTML
              </button>
            </div>
          </div>

          <select 
            className="select" 
            value={variantId} 
            onChange={(e) => setVariantId(e.target.value)}
            style={{ width: "100%", padding: "8px 12px", fontSize: 13 }}
          >
            {variants.length === 0 ? <option value="">No variants yet</option> : null}
            {variants.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="card" style={{ flex: 1, overflow: "hidden", minHeight: 0 }}>
        {!variantId ? (
          <div style={{ 
            height: "100%", 
            display: "flex", 
            alignItems: "center", 
            justifyContent: "center",
            padding: 20,
          }}>
            <div className="muted" style={{ textAlign: "center" }}>
              Create a variant to see preview
            </div>
          </div>
        ) : (
          <div style={{ height: "100%", background: "rgba(0,0,0,0.15)" }}>
            {tab === "pdf" ? (
              <iframe
                key={pdfSrc}
                src={pdfSrc}
                style={{ width: "100%", height: "100%", border: "none" }}
                title="PDF Preview"
              />
            ) : (
              <iframe
                key={htmlSrc}
                src={htmlSrc}
                style={{ width: "100%", height: "100%", border: "none", background: "#fff" }}
                title="HTML Preview"
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
