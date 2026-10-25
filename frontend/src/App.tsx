// Каркас: шапка с логотипом, тосты, вкладки.
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

type Tab = "home" | "receipt" | "warehouse" | "assemble" | "orders" | "moves" | "reports" | "profile" | "catalog" | "favs";

const TABS: { id: Tab; e: string; label: string }[] = [
  { id: "home", e: "H", label: "Главная" },
  { id: "warehouse", e: "W", label: "Склад" },
  { id: "assemble", e: "A", label: "Сборка" },
  { id: "receipt", e: "+", label: "Приёмка" },
  { id: "profile", e: "U", label: "Кабинет" },
];

export function toast(msg: string, ok = true) {
  let el = document.getElementById("hrx-toast");
  if (!el) { el = document.createElement("div"); el.id = "hrx-toast"; document.body.appendChild(el); }
  const c = tgColors();
  el.className = "hrx-toast";
  el.style.background = ok ? "#dff83a" : "#ff453a";
  el.style.color = ok ? "#111" : "#fff";
  el.textContent = msg;
  el.style.display = "block";
  (window as any).__hrxToast && clearTimeout((window as any).__hrxToast);
  (window as any).__hrxToast = setTimeout(() => { el!.style.display = "none"; }, 2200);
  void c;
}

export default function App() {
  const [tab, setTab] = useState<Tab>("home");
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    tg?.ready(); tg?.expand();
    try { tg?.disableVerticalSwipes?.(); } catch {}
    try { tg?.setHeaderColor?.("bg_color"); } catch {}
    try { tg?.setBackgroundColor?.("#1a1a2e"); } catch {}
    const c = tgColors();
    document.body.style.background = c.bg;
    document.body.style.color = c.text;
    let st = document.getElementById("hrx-style");
    if (!st) { st = document.createElement("style"); st.id = "hrx-style"; document.head.appendChild(st); }
    st.textContent = css;
  }, []);
  const go = (t: Tab) => { try { (window as any).Telegram?.WebApp?.HapticFeedback?.impactOccurred?.("light"); } catch {} setTab(t); window.scrollTo(0, 0); };
  const c = tgColors();
  return (
    <div className="hrx-shell">
      <div className="hrx-top" style={{ background: c.bg, color: c.text }}>
        <img src="/logo.png" alt="Гидробот" />
        <div><b>Склад Гидробот</b><small>производство</small></div>
      </div>
      {tab === "home" && <HomePage go={go} />}
      {tab === "receipt" && <ReceiptPage onDone={() => setRefresh(refresh + 1)} />}
      {tab === "warehouse" && <WarehousePage key={refresh} />}
      {tab === "assemble" && <AssemblePage />}
      {tab === "orders" && <OrdersPage onPick={() => go("assemble")} />}
      {tab === "moves" && <MovesPage />}
      {tab === "reports" && <ReportsPage />}
      {tab === "profile" && <ProfilePage />}
      {tab === "catalog" && <CatalogPage />}
      {tab === "favs" && <FavsPage />}
      <div className="hrx-tabs" style={{ background: c.bg }}>
        {TABS.map((t) => (<button key={t.id} className={tab === t.id ? "on" : ""} style={{ color: tab === t.id ? "#dff83a" : c.text }} onClick={() => go(t.id)}><span className="e">{t.e}</span>{t.label}</button>))}
      </div>
    </div>
  );
}
