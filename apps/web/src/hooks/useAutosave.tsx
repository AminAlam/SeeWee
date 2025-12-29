"use client";

import { useEffect, useRef, useState, useCallback } from "react";

type SaveStatus = "idle" | "saving" | "saved" | "error";

export function useAutosave<T>(
  data: T,
  saveFn: (data: T) => Promise<void>,
  debounceMs: number = 800
) {
  const [status, setStatus] = useState<SaveStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastSavedRef = useRef<string>("");
  const isFirstRender = useRef(true);

  const save = useCallback(async (dataToSave: T) => {
    const serialized = JSON.stringify(dataToSave);
    if (serialized === lastSavedRef.current) {
      return; // No changes
    }

    setStatus("saving");
    setError(null);

    try {
      await saveFn(dataToSave);
      lastSavedRef.current = serialized;
      setStatus("saved");
      
      // Reset to idle after showing "saved" briefly
      setTimeout(() => setStatus("idle"), 1500);
    } catch (e) {
      setError(String(e));
      setStatus("error");
    }
  }, [saveFn]);

  useEffect(() => {
    // Skip the first render to avoid saving on initial load
    if (isFirstRender.current) {
      isFirstRender.current = false;
      lastSavedRef.current = JSON.stringify(data);
      return;
    }

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set new timeout for debounced save
    timeoutRef.current = setTimeout(() => {
      save(data);
    }, debounceMs);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [data, debounceMs, save]);

  // Mark initial data as "saved" to establish baseline
  const setInitialData = useCallback((initialData: T) => {
    lastSavedRef.current = JSON.stringify(initialData);
    isFirstRender.current = false;
  }, []);

  return { status, error, setInitialData };
}

export function SaveIndicator({ status, error }: { status: SaveStatus; error: string | null }) {
  if (status === "idle") return null;
  
  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      gap: 6,
      fontSize: 11,
      color: status === "error" ? "#ff4d6d" : "rgba(255,255,255,0.5)",
    }}>
      {status === "saving" && (
        <>
          <span style={{ 
            width: 8, 
            height: 8, 
            borderRadius: "50%", 
            background: "rgba(124, 92, 255, 0.6)",
            animation: "pulse 1s infinite",
          }} />
          Saving...
        </>
      )}
      {status === "saved" && (
        <>
          <span style={{ color: "#4caf50" }}>✓</span>
          Saved
        </>
      )}
      {status === "error" && (
        <>
          <span>✕</span>
          {error || "Save failed"}
        </>
      )}
    </div>
  );
}

