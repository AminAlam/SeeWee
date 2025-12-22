"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { ResizableSplit } from "@/components/ResizableSplit";
import { PreviewPane } from "@/components/PreviewPane";

const NAV_ITEMS = [
  { href: "/", label: "Overview", icon: "◉", description: "Dashboard" },
  { href: "/entries", label: "Entries", icon: "◈", description: "CV blocks" },
  { href: "/variants", label: "Variants", icon: "◇", description: "Builder" },
  { href: "/profile", label: "Profile", icon: "○", description: "Info" },
];

function NavItem({
  href,
  label,
  icon,
  description,
  collapsed,
  index,
}: {
  href: string;
  label: string;
  icon: string;
  description: string;
  collapsed: boolean;
  index: number;
}) {
  const pathname = usePathname();
  const active = pathname === href || (href !== "/" && pathname?.startsWith(`${href}/`));

  return (
    <Link
      href={href}
      className="nav-item"
      data-active={active}
      style={{
        display: "flex",
        alignItems: "center",
        gap: collapsed ? 0 : 12,
        padding: collapsed ? "12px" : "10px 14px",
        borderRadius: 10,
        background: active ? "rgba(124, 92, 255, 0.18)" : "transparent",
        border: active ? "1px solid rgba(124, 92, 255, 0.4)" : "1px solid transparent",
        transition: "all 0.2s ease",
        justifyContent: collapsed ? "center" : "flex-start",
        animationDelay: `${index * 40}ms`,
      }}
    >
      <span style={{ 
        fontSize: 16, 
        opacity: active ? 1 : 0.6,
        transition: "opacity 0.2s ease",
      }}>
        {icon}
      </span>
      {!collapsed && (
        <div style={{ minWidth: 0 }}>
          <div style={{ fontWeight: 600, fontSize: 13 }}>{label}</div>
          <div style={{ fontSize: 10, color: "rgba(255,255,255,0.45)", marginTop: 1 }}>{description}</div>
        </div>
      )}
    </Link>
  );
}

function MobileNavItem({
  href,
  label,
  icon,
}: {
  href: string;
  label: string;
  icon: string;
}) {
  const pathname = usePathname();
  const active = pathname === href || (href !== "/" && pathname?.startsWith(`${href}/`));

  return (
    <Link
      href={href}
      className="mobile-nav-item"
      data-active={active}
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 2,
        padding: "8px 12px",
        borderRadius: 8,
        background: active ? "rgba(124, 92, 255, 0.18)" : "transparent",
        border: active ? "1px solid rgba(124, 92, 255, 0.4)" : "1px solid transparent",
        transition: "all 0.15s ease",
        flex: 1,
      }}
    >
      <span style={{ fontSize: 16, opacity: active ? 1 : 0.5 }}>{icon}</span>
      <span style={{ fontSize: 10, fontWeight: 500, opacity: active ? 1 : 0.6 }}>{label}</span>
    </Link>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const isOverview = pathname === "/";
  const showPreview = pathname === "/entries" || pathname === "/profile" || pathname === "/variants";

  return (
    <>
      <style jsx global>{`
        @keyframes fadeSlideIn {
          from {
            opacity: 0;
            transform: translateX(-8px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        .nav-item {
          animation: fadeSlideIn 0.25s ease forwards;
          opacity: 0;
        }
        
        .nav-item:hover {
          background: rgba(255,255,255,0.06) !important;
          border-color: rgba(255,255,255,0.12) !important;
        }
        
        .nav-item[data-active="true"]:hover {
          background: rgba(124, 92, 255, 0.22) !important;
          border-color: rgba(124, 92, 255, 0.5) !important;
        }
        
        .mobile-nav-item:hover {
          background: rgba(255,255,255,0.06) !important;
        }
        
        .collapse-btn {
          transition: all 0.2s ease;
        }
        
        .collapse-btn:hover {
          background: rgba(255,255,255,0.08) !important;
        }
        
        /* Desktop: show sidebar, hide mobile nav */
        @media (min-width: 769px) {
          .desktop-sidebar { display: flex !important; }
          .mobile-nav { display: none !important; }
        }
        
        /* Mobile: hide sidebar, show mobile nav */
        @media (max-width: 768px) {
          .desktop-sidebar { display: none !important; }
          .mobile-nav { display: flex !important; }
        }
      `}</style>

      <div style={{ 
        height: "100vh", 
        display: "flex", 
        flexDirection: "column",
        overflow: "hidden",
      }}>
        {/* Mobile Top Navigation */}
        <nav 
          className="mobile-nav"
          style={{
            display: "none",
            flexShrink: 0,
            padding: "8px 12px",
            background: "rgba(11, 13, 18, 0.9)",
            backdropFilter: "blur(20px)",
            borderBottom: "1px solid rgba(255,255,255,0.08)",
            gap: 4,
            justifyContent: "space-around",
          }}
        >
          {NAV_ITEMS.map((item) => (
            <MobileNavItem key={item.href} {...item} />
          ))}
        </nav>

        <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
          {/* Desktop Sidebar */}
          <aside
            className="desktop-sidebar"
            style={{
              display: "flex",
              flexDirection: "column",
              width: sidebarCollapsed ? 64 : 200,
              flexShrink: 0,
              background: "linear-gradient(180deg, rgba(18, 22, 30, 0.95) 0%, rgba(12, 15, 20, 0.95) 100%)",
              borderRight: "1px solid rgba(255,255,255,0.08)",
              transition: "width 0.25s ease",
              overflow: "hidden",
            }}
          >
            {/* Logo */}
            <div style={{ 
              padding: sidebarCollapsed ? "16px 12px" : "20px 16px",
              borderBottom: "1px solid rgba(255,255,255,0.06)",
              display: "flex",
              alignItems: "center",
              justifyContent: sidebarCollapsed ? "center" : "space-between",
              gap: 8,
            }}>
              {!sidebarCollapsed && (
                <div>
                  <div style={{ fontWeight: 800, fontSize: 18, letterSpacing: -0.5 }}>SeeWee</div>
                  <div style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", marginTop: 2 }}>CV Manager</div>
                </div>
              )}
              {sidebarCollapsed && (
                <div style={{ fontWeight: 800, fontSize: 18 }}>S</div>
              )}
            </div>

            {/* Nav Items */}
            <nav style={{ 
              flex: 1, 
              padding: sidebarCollapsed ? "12px 8px" : "12px",
              display: "flex",
              flexDirection: "column",
              gap: 4,
            }}>
              {NAV_ITEMS.map((item, i) => (
                <NavItem key={item.href} {...item} collapsed={sidebarCollapsed} index={i} />
              ))}
            </nav>

            {/* Collapse Toggle */}
            <div style={{ 
              padding: "12px",
              borderTop: "1px solid rgba(255,255,255,0.06)",
            }}>
              <button
                className="collapse-btn"
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                style={{
                  width: "100%",
                  padding: "8px",
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: 8,
                  color: "rgba(255,255,255,0.6)",
                  cursor: "pointer",
                  fontSize: 14,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 6,
                }}
                title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
              >
                <span style={{ 
                  transform: sidebarCollapsed ? "rotate(180deg)" : "rotate(0deg)",
                  transition: "transform 0.2s ease",
                  display: "inline-block",
                }}>
                  ◂
                </span>
                {!sidebarCollapsed && <span style={{ fontSize: 11 }}>Collapse</span>}
              </button>
            </div>
          </aside>

          {/* Main Content */}
          <main style={{ flex: 1, overflow: "hidden", padding: 16 }}>
            {isOverview && (
              <div style={{ 
                maxWidth: 900, 
                margin: "0 auto", 
                height: "100%", 
                overflowY: "auto",
                paddingRight: 8,
              }}>
                {children}
              </div>
            )}

            {showPreview && (
              <ResizableSplit
                storageKey="seewee.splitRatio"
                left={
                  <div style={{ 
                    height: "100%", 
                    overflowY: "auto", 
                    paddingRight: 12,
                    minWidth: 0,
                  }}>
                    {children}
                  </div>
                }
                right={
                  <div style={{ 
                    height: "100%",
                    paddingLeft: 12, 
                    borderLeft: "1px solid rgba(255,255,255,0.1)", 
                    minWidth: 0,
                    overflow: "hidden",
                  }}>
                    <PreviewPane />
                  </div>
                }
              />
            )}
          </main>
        </div>
      </div>
    </>
  );
}
