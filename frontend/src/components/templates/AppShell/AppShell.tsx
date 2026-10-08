// frontend/src/components/templates/AppShell/AppShell.tsx

import { useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import clsx from "clsx";
import { Sidebar, Topbar } from "../../organisms";
import "./AppShell.css";

const SIDEBAR_STORAGE_KEY = "kiko.sidebar.collapsed";

export function AppShell() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => {
    return localStorage.getItem(SIDEBAR_STORAGE_KEY) === "true";
  });

  useEffect(() => {
    localStorage.setItem(SIDEBAR_STORAGE_KEY, String(isSidebarCollapsed));
  }, [isSidebarCollapsed]);

  return (
    <div
      className={clsx("app-shell", {
        "app-shell--sidebar-collapsed": isSidebarCollapsed,
      })}
    >
      <Sidebar
        isCollapsed={isSidebarCollapsed}
        onToggle={() => setIsSidebarCollapsed((value) => !value)}
      />

      <div className="app-shell__main">
        <Topbar />
        <main className="app-shell__content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
