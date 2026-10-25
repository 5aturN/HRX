// Склад Гидробот: стиль iOS-списков, главная, склад, кабинет.
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
import { css, tgColors } from "./theme";

type Tab = "home" | "receipt" | "warehouse" | "assemble" | "orders" | "moves" | "reports" | "profile" | "catalog";

const TABS: { id: Tab; e: string; label: string }[] = [
  { id: "home", e: "H", label: "Главная" },
  { id: "warehouse", e: "W", label: "Склад" },
  { id: "assemble", e: "A", label: "Сборка" },
  { id: "receipt", e: "+", label: "Приемка" },
  { id: "profile", e: "U", label: "Кабинет" },
];

export default function App() {
  const [tab, setTab] = useState<Tab>("home");
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    tg?.ready(); tg?.expand();
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
      <div className="hrx-top" style={{ background: c.card, color: c.text }}>
        <img src="/logo.png" alt="Гидробот" />
        <b>Склад Гидробот</b>
      </div>
      {tab === "home" && <HomePage go={go} />}
      {tab === "receipt" && (<div><ReceiptPage onDone={() => setRefresh(refresh + 1)} /></div>)}
      {tab === "warehouse" && <WarehousePage />}
      {tab === "assemble" && <AssemblePage />}
      {tab === "orders" && <OrdersPage onPick={() => go("assemble")} />}
      {tab === "moves" && <MovesPage />}
      {tab === "reports" && <ReportsPage />}
      {tab === "profile" && <ProfilePage />}
      {tab === "catalog" && <CatalogPage />}
      <div className="hrx-tabs" style={{ background: c.card }}>
        {TABS.map((t) => (<button key={t.id} className={tab === t.id ? "on" : ""} style={{ color: tab === t.id ? "#007aff" : c.text }} onClick={() => go(t.id)}><span className="e">{t.e}</span>{t.label}</button>))}
      </div>
    </div>
  );
}
