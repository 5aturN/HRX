// Каркас: шапка с логотипом, тосты, вкладки с SVG-иконками, haptic.
import { useEffect, useState } from "react";
import ReceiptPage from "./pages/ReceiptPage";
import StockPage from "./pages/StockPage";
import AssemblePage from "./pages/AssemblePage";
import ReportsPage from "./pages/ReportsPage";
import OrdersPage from "./pages/OrdersPage";
import AdminPage from "./pages/AdminPage";
import MovesPage from "./pages/MovesPage";
import HomePage from "./pages/HomePage";
import WarehousePage from "./pages/WarehousePage";
import ProfilePage from "./pages/ProfilePage";
import CatalogPage from "./pages/CatalogPage";
import FavsPage from "./pages/FavsPage";
import { css, tgColors } from "./theme";

type Tab = "home" | "receipt" | "warehouse" | "assemble" | "orders" | "moves" | "reports" | "profile" | "catalog" | "favs" | "stock" | "admin";

function haptic(kind: "light" | "success" | "error" = "light") {
  try {
    const h = (window as any).Telegram?.WebApp?.HapticFeedback;
    if (!h) return;
    if (kind === "light") h.impactOccurred?.("light");
    else h.notificationOccurred?.(kind);
  } catch {
    /* не в Telegram — тихо */
  }
}

function Icon({ d }: { d: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={d} />
    </svg>
  );
}

const P_HOME = "M3 10.5 12 3l9 7.5M5 9.5V21h14V9.5";
const P_BOX = "M21 8 12 3 3 8v8l9 5 9-5V8zM3 8l9 5 9-5M12 13v8";
const P_HAMMER = "m15 12-8.5 8.5a2.1 2.1 0 1 1-3-3L12 9M17.5 3.5l3 3L12 15l-3-3 8.5-8.5z";
const P_USER = "M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z";
const P_PLUS = "M12 5v14M5 12h14";

const TABS: { id: Tab; label: string; icon: string; fab?: boolean }[] = [
  { id: "home", label: "Главная", icon: P_HOME },
  { id: "warehouse", label: "Склад", icon: P_BOX },
  { id: "receipt", label: "Приёмка", icon: P_PLUS, fab: true },
  { id: "assemble", label: "Сборка", icon: P_HAMMER },
  { id: "profile", label: "Кабинет", icon: P_USER },
];

let toastTimer: number | undefined;

export function toast(msg: string, ok = true) {
  let el = document.getElementById("hrx-toast");
  if (!el) {
    el = document.createElement("div");
    el.id = "hrx-toast";
    document.body.appendChild(el);
  }
  el.className = "hrx-toast " + (ok ? "ok" : "err");
  el.textContent = msg;
  el.style.display = "block";
  if (ok) haptic("success");
  else haptic("error");
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => {
    const t = document.getElementById("hrx-toast");
    if (t) t.style.display = "none";
  }, 2200);
}

export default function App() {
  const [tab, setTab] = useState<Tab>("home");
  const [refresh, setRefresh] = useState(0);
  const [, setThemeTick] = useState(0);
  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    tg?.ready();
    tg?.expand();
    try {
      tg?.disableVerticalSwipes?.();
    } catch {
      /* старые клиенты */
    }
    try {
      tg?.setHeaderColor?.("bg_color");
    } catch {
      /* не поддерживается */
    }
    try {
      tg?.setBackgroundColor?.("#1a1a2e");
    } catch {
      /* не поддерживается */
    }
    const c = tgColors();
    document.body.style.background = c.bg;
    document.body.style.color = c.text;
    let st = document.getElementById("hrx-style");
    if (!st) {
      st = document.createElement("style");
      st.id = "hrx-style";
      document.head.appendChild(st);
    }
    st.textContent = css;
    const onTheme = () => {
      const nc = tgColors();
      document.body.style.background = nc.bg;
      document.body.style.color = nc.text;
      setThemeTick((t) => t + 1);
    };
    try {
      tg?.onEvent?.("themeChanged", onTheme);
    } catch {
      /* не поддерживается */
    }
    return () => {
      try {
        tg?.offEvent?.("themeChanged", onTheme);
      } catch {
        /* не поддерживается */
      }
    };
  }, []);
  const go = (t: Tab) => {
    haptic("light");
    setTab(t);
    window.scrollTo(0, 0);
  };
  const c = tgColors();
  return (
    <div className="hrx-shell">
      <div className="hrx-top" style={{ background: c.bg, color: c.text }}>
        <img src="/logo.png" alt="Гидробот" />
        <div>
          <b>Склад Гидробот</b>
          <small>производство</small>
        </div>
      </div>
      {tab === "home" && <HomePage go={go} />}
      {tab === "receipt" && <ReceiptPage onDone={() => setRefresh(refresh + 1)} />}
      {tab === "warehouse" && <WarehousePage key={refresh} />}
      {tab === "stock" && <StockPage />}
      {tab === "assemble" && <AssemblePage />}
      {tab === "orders" && <OrdersPage onPick={() => go("assemble")} />}
      {tab === "moves" && <MovesPage />}
      {tab === "reports" && <ReportsPage />}
      {tab === "profile" && <ProfilePage />}
      {tab === "catalog" && <CatalogPage />}
      {tab === "favs" && <FavsPage />}
      {tab === "admin" && <AdminPage />}
      <nav className="hrx-tabs" style={{ background: c.bg }}>
        {TABS.map((t) =>
          t.fab ? (
            <button key={t.id} onClick={() => go(t.id)} aria-label={t.label} title={t.label}>
              <span className="hrx-fab">
                <Icon d={t.icon} />
              </span>
              <span style={{ color: tab === t.id ? "#dff83a" : c.text }}>{t.label}</span>
            </button>
          ) : (
            <button
              key={t.id}
              className={tab === t.id ? "on" : ""}
              style={{ color: tab === t.id ? "#dff83a" : c.text }}
              onClick={() => go(t.id)}
            >
              <Icon d={t.icon} />
              {t.label}
            </button>
          ),
        )}
      </nav>
    </div>
  );
}
