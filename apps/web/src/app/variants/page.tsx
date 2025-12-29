"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  DndContext,
  DragOverlay,
  closestCenter,
  pointerWithin,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragStartEvent,
  DragEndEvent,
  useDroppable,
  useDraggable,
  CollisionDetection,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { SaveIndicator } from "@/hooks/useAutosave";

// Types
type Entry = {
  id: string;
  type: string;
  data: Record<string, unknown>;
  tags: string[];
};

type Variant = {
  id: string;
  name: string;
  rules: Record<string, unknown>;
  sections: string[];
  has_layout: boolean;
  created_at: string;
  updated_at: string;
};

type Layout = {
  variant_id: string;
  sections: Record<string, string[]>;
};

type ActiveDrag = 
  | { type: "entry"; entry: Entry }
  | { type: "section"; sectionId: string; label: string };

type SaveStatus = "idle" | "saving" | "saved" | "error";

const SECTION_OPTIONS = [
  { id: "experience", label: "Experience" },
  { id: "education", label: "Education" },
  { id: "projects", label: "Projects" },
  { id: "publications", label: "Publications" },
  { id: "awards", label: "Awards" },
  { id: "skills", label: "Skills" },
  { id: "volunteering", label: "Volunteering" },
  { id: "certifications", label: "Certifications" },
  { id: "talks", label: "Talks" },
  { id: "languages", label: "Languages" },
  { id: "references", label: "References" },
];

function getEntryTitle(entry: Entry): string {
  const d = entry.data || {};
  return (
    (d.role as string) ||
    (d.title as string) ||
    (d.name as string) ||
    (d.degree as string) ||
    (d.category as string) ||
    entry.type
  );
}

function getEntrySubtitle(entry: Entry): string {
  const d = entry.data || {};
  return (
    (d.company as string) ||
    (d.organization as string) ||
    (d.school as string) ||
    (d.issuer as string) ||
    (d.venue as string) ||
    ""
  );
}

function LibraryEntry({ entry }: { entry: Entry }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: `library-${entry.id}`,
    data: { type: "library", entry },
  });

  const style = transform
    ? {
        transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
      }
    : undefined;

  return (
    <div
      ref={setNodeRef}
      style={{
        ...style,
        opacity: isDragging ? 0.5 : 1,
        padding: 10,
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: 10,
        cursor: "grab",
        touchAction: "none",
      }}
      {...attributes}
      {...listeners}
    >
      <div style={{ display: "flex", gap: 6, marginBottom: 4 }}>
        <span style={{
          fontSize: 10,
          padding: "2px 6px",
          background: "rgba(124, 92, 255, 0.2)",
          borderRadius: 4,
          color: "rgba(255,255,255,0.8)",
        }}>
          {entry.type}
        </span>
      </div>
      <div style={{ fontWeight: 600, fontSize: 12 }}>{getEntryTitle(entry)}</div>
      {getEntrySubtitle(entry) && (
        <div style={{ fontSize: 10, color: "rgba(255,255,255,0.5)", marginTop: 2 }}>
          {getEntrySubtitle(entry)}
        </div>
      )}
    </div>
  );
}

function SectionEntry({ entry, onRemove }: { entry: Entry; onRemove: () => void }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: entry.id,
    data: { type: "entry-in-section", entry },
  });

  return (
    <div
      ref={setNodeRef}
      style={{
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
        padding: 8,
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.1)",
        borderRadius: 8,
        display: "flex",
        alignItems: "center",
        gap: 8,
      }}
    >
      <div
        {...attributes}
        {...listeners}
        style={{
          cursor: "grab",
          padding: "2px 4px",
          color: "rgba(255,255,255,0.4)",
          fontSize: 12,
        }}
      >
        ⋮⋮
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 600, fontSize: 12, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {getEntryTitle(entry)}
        </div>
      </div>
      <button
        onClick={onRemove}
        style={{
          padding: "2px 6px",
          fontSize: 12,
          background: "rgba(255,77,109,0.1)",
          border: "1px solid rgba(255,77,109,0.3)",
          borderRadius: 4,
          color: "#ff4d6d",
          cursor: "pointer",
        }}
      >
        ×
      </button>
    </div>
  );
}

function SortableSection({
  sectionId,
  label,
  entries,
  entriesById,
  onRemoveEntry,
  onRemoveSection,
}: {
  sectionId: string;
  label: string;
  entries: string[];
  entriesById: Record<string, Entry>;
  onRemoveEntry: (entryId: string) => void;
  onRemoveSection: () => void;
}) {
  const {
    attributes,
    listeners,
    setNodeRef: setSortableRef,
    transform,
    transition,
    isDragging,
  } = useSortable({
    id: `section-sortable-${sectionId}`,
    data: { type: "section-reorder", sectionId },
  });

  const { setNodeRef: setDroppableRef, isOver } = useDroppable({
    id: `section-drop-${sectionId}`,
    data: { type: "section-drop", sectionId },
  });

  return (
    <div
      ref={setSortableRef}
      style={{
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.5 : 1,
      }}
    >
      <div
        ref={setDroppableRef}
        style={{
          padding: 12,
          background: isOver ? "rgba(124, 92, 255, 0.08)" : "rgba(255,255,255,0.02)",
          border: isOver ? "2px dashed rgba(124, 92, 255, 0.5)" : "1px solid rgba(255,255,255,0.1)",
          borderRadius: 10,
          transition: "all 0.15s ease",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div
              {...attributes}
              {...listeners}
              style={{
                cursor: "grab",
                padding: "4px 6px",
                color: "rgba(255,255,255,0.4)",
                fontSize: 14,
                background: "rgba(255,255,255,0.05)",
                borderRadius: 4,
                lineHeight: 1,
              }}
              title="Drag to reorder section"
            >
              ≡
            </div>
            <div style={{ fontWeight: 600, fontSize: 13 }}>{label}</div>
          </div>
          <button
            onClick={onRemoveSection}
            style={{
              padding: "2px 8px",
              fontSize: 10,
              background: "transparent",
              border: "1px solid rgba(255,255,255,0.15)",
              borderRadius: 4,
              color: "rgba(255,255,255,0.5)",
              cursor: "pointer",
            }}
          >
            Remove
          </button>
        </div>

        <SortableContext items={entries} strategy={verticalListSortingStrategy}>
          <div style={{ display: "flex", flexDirection: "column", gap: 6, minHeight: 40 }}>
            {entries.length === 0 ? (
              <div style={{
                textAlign: "center",
                padding: 12,
                border: "1px dashed rgba(255,255,255,0.15)",
                borderRadius: 8,
                fontSize: 11,
                color: "rgba(255,255,255,0.4)",
              }}>
                Drag entries here
              </div>
            ) : (
              entries.map((entryId) => {
                const entry = entriesById[entryId];
                if (!entry) return null;
                return (
                  <SectionEntry
                    key={entryId}
                    entry={entry}
                    onRemove={() => onRemoveEntry(entryId)}
                  />
                );
              })
            )}
          </div>
        </SortableContext>
      </div>
    </div>
  );
}

function EntryOverlay({ entry }: { entry: Entry }) {
  return (
    <div style={{
      padding: 10,
      background: "rgba(30,35,50,0.95)",
      border: "1px solid rgba(124, 92, 255, 0.5)",
      borderRadius: 10,
      boxShadow: "0 10px 30px rgba(0,0,0,0.4)",
      transform: "rotate(2deg)",
    }}>
      <div style={{ fontWeight: 600, fontSize: 12 }}>{getEntryTitle(entry)}</div>
    </div>
  );
}

function SectionOverlay({ label }: { label: string }) {
  return (
    <div style={{
      padding: 14,
      background: "rgba(30,35,50,0.95)",
      border: "2px solid rgba(124, 92, 255, 0.6)",
      borderRadius: 12,
      boxShadow: "0 15px 40px rgba(0,0,0,0.5)",
      minWidth: 200,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ fontSize: 14, color: "rgba(255,255,255,0.5)" }}>≡</span>
        <span style={{ fontWeight: 700, fontSize: 14 }}>{label}</span>
      </div>
    </div>
  );
}

export default function VariantsPage() {
  const [variants, setVariants] = useState<Variant[]>([]);
  const [entries, setEntries] = useState<Entry[]>([]);
  const [selectedVariant, setSelectedVariant] = useState<Variant | null>(null);
  const [layout, setLayout] = useState<Record<string, string[]>>({});
  const [sectionOrder, setSectionOrder] = useState<string[]>([]);
  const [variantName, setVariantName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");
  const [activeDrag, setActiveDrag] = useState<ActiveDrag | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");

  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastSavedRef = useRef<string>("");
  const isInitialLoad = useRef(true);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  // Custom collision detection that prioritizes droppable sections
  const customCollisionDetection: CollisionDetection = (args) => {
    const pointerCollisions = pointerWithin(args);
    
    const activeData = args.active.data.current;
    if (activeData?.type === "library") {
      const sectionDrops = pointerCollisions.filter(
        c => c.id.toString().startsWith("section-drop-")
      );
      if (sectionDrops.length > 0) {
        return sectionDrops;
      }
    }
    
    if (pointerCollisions.length > 0) {
      return pointerCollisions;
    }
    
    return closestCenter(args);
  };

  const entriesById = useMemo(() => {
    const map: Record<string, Entry> = {};
    entries.forEach((e) => { map[e.id] = e; });
    return map;
  }, [entries]);

  const filteredLibraryEntries = useMemo(() => {
    let result = entries;
    if (typeFilter !== "all") {
      result = result.filter((e) => e.type === typeFilter);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter((e) => {
        const title = getEntryTitle(e).toLowerCase();
        const subtitle = getEntrySubtitle(e).toLowerCase();
        return title.includes(q) || subtitle.includes(q);
      });
    }
    const usedIds = new Set(Object.values(layout).flat());
    result = result.filter((e) => !usedIds.has(e.id));
    return result;
  }, [entries, typeFilter, searchQuery, layout]);

  const sectionSortableIds = useMemo(() => sectionOrder.map(s => `section-sortable-${s}`), [sectionOrder]);

  // Autosave effect
  const saveLayout = useCallback(async (
    variantId: string, 
    layoutData: Record<string, string[]>, 
    order: string[],
    name: string,
    originalName: string
  ) => {
    const orderedLayout: Record<string, string[]> = {};
    order.forEach(s => {
      orderedLayout[s] = layoutData[s] || [];
    });

    const dataToSave = JSON.stringify({ layout: orderedLayout, name });
    if (dataToSave === lastSavedRef.current) {
      return;
    }

    setSaveStatus("saving");
    try {
      await fetch(`/api/variants/${variantId}/layout`, {
        method: "PUT",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ sections: orderedLayout }),
      });
      
      if (name !== originalName) {
        await fetch(`/api/variants/${variantId}`, {
          method: "PUT",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ name }),
        });
        // Update the local variant record
        setVariants(prev => prev.map(v => v.id === variantId ? { ...v, name } : v));
        setSelectedVariant(prev => prev?.id === variantId ? { ...prev, name } : prev);
      }
      
      lastSavedRef.current = dataToSave;
      setSaveStatus("saved");
      setTimeout(() => setSaveStatus("idle"), 1500);
    } catch (e) {
      setSaveStatus("error");
      setError(String(e));
    }
  }, []);

  // Trigger autosave when layout, sectionOrder, or variantName changes
  useEffect(() => {
    if (!selectedVariant || isInitialLoad.current) {
      return;
    }

    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    saveTimeoutRef.current = setTimeout(() => {
      saveLayout(selectedVariant.id, layout, sectionOrder, variantName, selectedVariant.name);
    }, 600);

    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [layout, sectionOrder, variantName, selectedVariant, saveLayout]);

  useEffect(() => {
    async function load() {
      const [variantsRes, entriesRes] = await Promise.all([
        fetch("/api/variants", { cache: "no-store" }),
        fetch("/api/entries", { cache: "no-store" }),
      ]);
      const variantsData = (await variantsRes.json()) as Variant[];
      const entriesData = (await entriesRes.json()) as Entry[];
      setVariants(variantsData);
      setEntries(entriesData);
      if (variantsData.length > 0) {
        selectVariant(variantsData[0], entriesData);
      }
    }
    load().catch((e) => setError(String(e)));
  }, []);

  async function selectVariant(variant: Variant, allEntries?: Entry[]) {
    isInitialLoad.current = true;
    setSelectedVariant(variant);
    setVariantName(variant.name);
    const layoutRes = await fetch(`/api/variants/${variant.id}/layout`, { cache: "no-store" });
    const layoutData = (await layoutRes.json()) as Layout;
    if (Object.keys(layoutData.sections).length > 0) {
      setLayout(layoutData.sections);
      setSectionOrder(Object.keys(layoutData.sections));
      lastSavedRef.current = JSON.stringify({ layout: layoutData.sections, name: variant.name });
    } else {
      const initialLayout: Record<string, string[]> = {};
      variant.sections.forEach((s) => { initialLayout[s] = []; });
      setLayout(initialLayout);
      setSectionOrder(variant.sections);
      lastSavedRef.current = JSON.stringify({ layout: initialLayout, name: variant.name });
    }
    // Allow autosave after initial load
    setTimeout(() => { isInitialLoad.current = false; }, 100);
  }

  async function createNewVariant() {
    const res = await fetch("/api/variants", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ name: `Variant ${variants.length + 1}`, rules: {}, sections: ["experience", "education", "skills"] }),
    });
    if (res.ok) {
      const newVariant = (await res.json()) as Variant;
      const variantsRes = await fetch("/api/variants", { cache: "no-store" });
      setVariants(await variantsRes.json());
      selectVariant(newVariant);
    }
  }

  async function deleteVariant(id: string) {
    await fetch(`/api/variants/${id}`, { method: "DELETE" });
    const variantsRes = await fetch("/api/variants", { cache: "no-store" });
    const newVariants = (await variantsRes.json()) as Variant[];
    setVariants(newVariants);
    if (selectedVariant?.id === id) {
      if (newVariants.length > 0) selectVariant(newVariants[0]);
      else { setSelectedVariant(null); setLayout({}); setSectionOrder([]); }
    }
  }

  function addSection(sectionId: string) {
    if (!layout[sectionId]) {
      setLayout({ ...layout, [sectionId]: [] });
      setSectionOrder([...sectionOrder, sectionId]);
    }
  }

  function removeSection(sectionId: string) {
    const newLayout = { ...layout };
    delete newLayout[sectionId];
    setLayout(newLayout);
    setSectionOrder(sectionOrder.filter(s => s !== sectionId));
  }

  function removeEntryFromSection(sectionId: string, entryId: string) {
    setLayout({ ...layout, [sectionId]: layout[sectionId].filter((id) => id !== entryId) });
  }

  function handleDragStart(event: DragStartEvent) {
    const data = event.active.data.current;
    if (data?.type === "library" && data.entry) {
      setActiveDrag({ type: "entry", entry: data.entry });
    } else if (data?.type === "entry-in-section" && data.entry) {
      setActiveDrag({ type: "entry", entry: data.entry });
    } else if (data?.type === "section-reorder" && data.sectionId) {
      const sectionInfo = SECTION_OPTIONS.find(s => s.id === data.sectionId);
      setActiveDrag({ type: "section", sectionId: data.sectionId, label: sectionInfo?.label || data.sectionId });
    }
  }

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    setActiveDrag(null);
    if (!over) return;
    
    const activeData = active.data.current;
    const overData = over.data.current;

    // Section reordering
    if (activeData?.type === "section-reorder") {
      const activeId = active.id as string;
      const overId = over.id as string;
      
      if (activeId !== overId && overId.startsWith("section-sortable-")) {
        const activeSectionId = activeId.replace("section-sortable-", "");
        const overSectionId = overId.replace("section-sortable-", "");
        
        const oldIndex = sectionOrder.indexOf(activeSectionId);
        const newIndex = sectionOrder.indexOf(overSectionId);
        
        if (oldIndex !== -1 && newIndex !== -1) {
          setSectionOrder(arrayMove(sectionOrder, oldIndex, newIndex));
        }
      }
      return;
    }

    // Entry from library to section drop zone
    if (activeData?.type === "library" && overData?.type === "section-drop") {
      const entry = activeData.entry as Entry;
      const sectionId = overData.sectionId as string;
      if (!layout[sectionId].includes(entry.id)) {
        setLayout({ ...layout, [sectionId]: [...layout[sectionId], entry.id] });
      }
      return;
    }

    // Entry from library dropped onto an entry in a section
    if (activeData?.type === "library" && overData?.type === "entry-in-section") {
      const entry = activeData.entry as Entry;
      const overEntry = overData.entry as Entry;
      
      let targetSection: string | null = null;
      for (const [sectionId, entryIds] of Object.entries(layout)) {
        if (entryIds.includes(overEntry.id)) {
          targetSection = sectionId;
          break;
        }
      }
      
      if (targetSection && !layout[targetSection].includes(entry.id)) {
        const newSection = [...layout[targetSection]];
        const overIndex = newSection.indexOf(overEntry.id);
        newSection.splice(overIndex, 0, entry.id);
        setLayout({ ...layout, [targetSection]: newSection });
      }
      return;
    }

    // Entry reordering within/between sections
    if (activeData?.type === "entry-in-section") {
      const activeEntry = activeData.entry as Entry;
      
      let activeSection: string | null = null;
      for (const [sectionId, entryIds] of Object.entries(layout)) {
        if (entryIds.includes(activeEntry.id)) {
          activeSection = sectionId;
          break;
        }
      }
      
      if (!activeSection) return;

      if (overData?.type === "section-drop") {
        const targetSection = overData.sectionId as string;
        if (activeSection !== targetSection) {
          const newFromSection = layout[activeSection].filter(id => id !== activeEntry.id);
          const newToSection = [...layout[targetSection], activeEntry.id];
          setLayout({ ...layout, [activeSection]: newFromSection, [targetSection]: newToSection });
        }
        return;
      }

      if (overData?.type === "entry-in-section") {
        const overEntry = overData.entry as Entry;
        let overSection: string | null = null;
        for (const [sectionId, entryIds] of Object.entries(layout)) {
          if (entryIds.includes(overEntry.id)) {
            overSection = sectionId;
            break;
          }
        }
        
        if (!overSection) return;

        if (activeSection === overSection) {
          const oldIndex = layout[activeSection].indexOf(activeEntry.id);
          const newIndex = layout[activeSection].indexOf(overEntry.id);
          setLayout({ ...layout, [activeSection]: arrayMove(layout[activeSection], oldIndex, newIndex) });
        } else {
          const newFromSection = layout[activeSection].filter(id => id !== activeEntry.id);
          const newToSection = [...layout[overSection]];
          const overIndex = newToSection.indexOf(overEntry.id);
          newToSection.splice(overIndex, 0, activeEntry.id);
          setLayout({ ...layout, [activeSection]: newFromSection, [overSection]: newToSection });
        }
      }
    }
  }

  async function exportLatex() {
    if (!selectedVariant) return;
    const res = await fetch(`/api/variants/${selectedVariant.id}/export/latex`, { method: "POST" });
    if (res.ok) {
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `cv-${selectedVariant.name.toLowerCase().replace(/\s+/g, "-")}.zip`;
      a.click();
      URL.revokeObjectURL(url);
    }
  }

  const availableSections = SECTION_OPTIONS.filter((s) => !sectionOrder.includes(s.id));

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={customCollisionDetection}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 12, overflow: "hidden" }}>
        {/* Header */}
        <div style={{ flexShrink: 0 }}>
          <h1 style={{ margin: 0, fontSize: 22, letterSpacing: -0.5 }}>Variant Builder</h1>
          <div style={{ fontSize: 12, color: "rgba(255,255,255,0.5)", marginTop: 4, display: "flex", alignItems: "center", gap: 12 }}>
            <span>Drag entries into sections • Drag sections to reorder</span>
            <SaveIndicator status={saveStatus} error={error} />
          </div>
        </div>

        {/* Controls */}
        <div style={{ 
          flexShrink: 0, 
          padding: 12, 
          background: "rgba(255,255,255,0.03)", 
          borderRadius: 10, 
          border: "1px solid rgba(255,255,255,0.08)",
          display: "flex",
          flexWrap: "wrap",
          gap: 10,
          alignItems: "center",
          justifyContent: "space-between",
        }}>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
            <select
              className="select"
              value={selectedVariant?.id || ""}
              onChange={(e) => {
                const v = variants.find((v) => v.id === e.target.value);
                if (v) selectVariant(v);
              }}
              style={{ minWidth: 140, padding: "6px 10px", fontSize: 12 }}
            >
              {variants.length === 0 && <option value="">No variants</option>}
              {variants.map((v) => (
                <option key={v.id} value={v.id}>{v.name}</option>
              ))}
            </select>
            <button className="btn" onClick={createNewVariant} style={{ fontSize: 12, padding: "6px 12px" }}>
              + New
            </button>
            {selectedVariant && (
              <button className="btn btnDanger" onClick={() => deleteVariant(selectedVariant.id)} style={{ fontSize: 12, padding: "6px 12px" }}>
                Delete
              </button>
            )}
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
            <input
              className="input"
              value={variantName}
              onChange={(e) => setVariantName(e.target.value)}
              placeholder="Variant name"
              style={{ width: 140, padding: "6px 10px", fontSize: 12 }}
            />
            <button className="btn" onClick={exportLatex} disabled={!selectedVariant} style={{ fontSize: 12, padding: "6px 12px" }}>
              Export
            </button>
          </div>
        </div>

        {error && saveStatus !== "error" && <div className="error" style={{ flexShrink: 0 }}>{error}</div>}

        {/* Main area */}
        <div style={{ flex: 1, display: "flex", gap: 12, minHeight: 0, overflow: "hidden" }}>
          {/* Library */}
          <div style={{ width: 200, flexShrink: 0, display: "flex", flexDirection: "column", gap: 8, overflow: "hidden" }}>
            <div style={{ 
              padding: 10, 
              background: "rgba(255,255,255,0.03)", 
              borderRadius: 10,
              border: "1px solid rgba(255,255,255,0.08)",
              flexShrink: 0,
            }}>
              <div style={{ fontWeight: 600, fontSize: 12, marginBottom: 8 }}>Entry Library</div>
              <input
                className="input"
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{ padding: "5px 8px", fontSize: 11, marginBottom: 6 }}
              />
              <select
                className="select"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                style={{ padding: "5px 8px", fontSize: 11 }}
              >
                <option value="all">All types</option>
                {[...new Set(entries.map((e) => e.type))].map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
            <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6, paddingRight: 4 }}>
              {filteredLibraryEntries.length === 0 ? (
                <div style={{ padding: 16, textAlign: "center", fontSize: 11, color: "rgba(255,255,255,0.4)" }}>
                  {entries.length === 0 ? "No entries" : "All assigned"}
                </div>
              ) : (
                filteredLibraryEntries.map((entry) => (
                  <LibraryEntry key={entry.id} entry={entry} />
                ))
              )}
            </div>
          </div>

          {/* Sections */}
          <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 10, minWidth: 0, overflow: "hidden" }}>
            {selectedVariant ? (
              <>
                <SortableContext items={sectionSortableIds} strategy={verticalListSortingStrategy}>
                  <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 10, paddingRight: 4 }}>
                    {sectionOrder.map((sectionId) => {
                      const sectionInfo = SECTION_OPTIONS.find((s) => s.id === sectionId);
                      return (
                        <SortableSection
                          key={sectionId}
                          sectionId={sectionId}
                          label={sectionInfo?.label || sectionId}
                          entries={layout[sectionId] || []}
                          entriesById={entriesById}
                          onRemoveEntry={(entryId) => removeEntryFromSection(sectionId, entryId)}
                          onRemoveSection={() => removeSection(sectionId)}
                        />
                      );
                    })}
                  </div>
                </SortableContext>
                {availableSections.length > 0 && (
                  <div style={{ flexShrink: 0, display: "flex", gap: 6, flexWrap: "wrap", alignItems: "center" }}>
                    <span style={{ fontSize: 11, color: "rgba(255,255,255,0.4)" }}>Add section:</span>
                    {availableSections.slice(0, 6).map((s) => (
                      <button
                        key={s.id}
                        onClick={() => addSection(s.id)}
                        style={{
                          padding: "4px 8px",
                          fontSize: 10,
                          background: "transparent",
                          border: "1px solid rgba(255,255,255,0.15)",
                          borderRadius: 4,
                          color: "rgba(255,255,255,0.6)",
                          cursor: "pointer",
                        }}
                      >
                        + {s.label}
                      </button>
                    ))}
                    {availableSections.length > 6 && (
                      <span style={{ fontSize: 10, color: "rgba(255,255,255,0.3)" }}>
                        +{availableSections.length - 6} more
                      </span>
                    )}
                  </div>
                )}
              </>
            ) : (
              <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "rgba(255,255,255,0.4)" }}>
                Create or select a variant
              </div>
            )}
          </div>
        </div>
      </div>

      <DragOverlay>
        {activeDrag?.type === "entry" && <EntryOverlay entry={activeDrag.entry} />}
        {activeDrag?.type === "section" && <SectionOverlay label={activeDrag.label} />}
      </DragOverlay>
    </DndContext>
  );
}
