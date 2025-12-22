"use client";

import { useEffect, useRef, useState } from "react";

export function ResizableSplit({
  storageKey,
  left,
  right
}: {
  storageKey: string;
  left: React.ReactNode;
  right: React.ReactNode | null;
}) {
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const [ratio, setRatio] = useState(0.52);
  const [dragging, setDragging] = useState(false);

  useEffect(() => {
    const raw = localStorage.getItem(storageKey);
    if (!raw) return;
    const n = Number(raw);
    if (!Number.isFinite(n)) return;
    setRatio(Math.min(0.75, Math.max(0.3, n)));
  }, [storageKey]);

  useEffect(() => {
    localStorage.setItem(storageKey, String(ratio));
  }, [storageKey, ratio]);

  useEffect(() => {
    function onMove(e: PointerEvent) {
      if (!dragging) return;
      const el = wrapRef.current;
      if (!el) return;
      const r = el.getBoundingClientRect();
      const x = e.clientX - r.left;
      const next = x / r.width;
      setRatio(Math.min(0.75, Math.max(0.3, next)));
    }
    function onUp() {
      setDragging(false);
    }
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    };
  }, [dragging]);

  if (!right) {
    return (
      <div style={{ height: "100%", overflow: "hidden" }}>
        {left}
      </div>
    );
  }

  return (
    <>
      <style jsx>{`
        .rs-wrap {
          display: flex;
          height: 100%;
          gap: 0;
          overflow: hidden;
        }
        
        .rs-left {
          min-width: 0;
          height: 100%;
          overflow: hidden;
        }
        
        .rs-right {
          flex: 1;
          min-width: 0;
          height: 100%;
          overflow: hidden;
        }
        
        .rs-gutter {
          width: 8px;
          flex-shrink: 0;
          cursor: col-resize;
          transition: background 0.15s ease;
          position: relative;
        }
        
        .rs-gutter:hover {
          background: rgba(124,92,255,0.15);
        }
        
        .rs-gutter:hover .rs-handle {
          background: rgba(124,92,255,0.6);
          height: 60px;
        }
        
        .rs-handle {
          position: absolute;
          left: 50%;
          top: 50%;
          transform: translate(-50%, -50%);
          width: 4px;
          height: 40px;
          border-radius: 2px;
          transition: all 0.15s ease;
        }
        
        /* Mobile: stack vertically */
        @media (max-width: 768px) {
          .rs-wrap {
            flex-direction: column !important;
          }
          .rs-left {
            flex: none !important;
            height: 45vh !important;
            max-height: 45vh !important;
          }
          .rs-right {
            flex: 1 !important;
            height: auto !important;
          }
          .rs-gutter {
            display: none !important;
          }
        }
      `}</style>
      
      <div className="rs-wrap" ref={wrapRef}>
        <div 
          className="rs-left"
          style={{ flex: `0 0 ${ratio * 100}%` }}
        >
          {left}
        </div>
        <div
          className="rs-gutter"
          role="separator"
          aria-orientation="vertical"
          onPointerDown={(e) => {
            (e.currentTarget as HTMLDivElement).setPointerCapture(e.pointerId);
            setDragging(true);
          }}
          style={{
            background: dragging ? "rgba(124,92,255,0.25)" : "transparent",
          }}
          title="Drag to resize"
        >
          <div 
            className="rs-handle"
            style={{
              background: dragging ? "rgba(124,92,255,0.8)" : "rgba(255,255,255,0.2)",
              height: dragging ? 60 : 40,
            }} 
          />
        </div>
        <div className="rs-right">
          {right}
        </div>
      </div>
    </>
  );
}
