// Склад Гидробот: шапка с логотипом, главный экран-карточки, нижние вкладки.
import { useEffect, useState } from "react";
import ReceiptPage from "./pages/ReceiptPage";
import StockPage from "./pages/StockPage";
import AssemblePage from "./pages/AssemblePage";
import ReportsPage from "./pages/ReportsPage";
import OrdersPage from "./pages/OrdersPage";
import AdminPage from "./pages/AdminPage";
import MovesPage from "./pages/MovesPage";
import { T, css, tgColors } from "./theme";

type Tab = "home" | "receipt" | "stock" | "assemble" | "orders" | "moves" | "reports" | "admin";

const TABS: { id: Tab; emo: string; label: string }[] = [
  { id: "home", emo: "H", label: "Главная" },
  { id: "receipt", emo: "P", label: "Приёмка" },
  { id: "stock", emo: "S", label: "Остатки" },
  { id: "assemble", emo: "A", label: "Сборка" },
  { id: "moves", emo: "M", label: "Движения" },
];

export default function App() {
  const [user, setUser] = useState("Гость");
  const [tab, setTab] = useState<Tab>("home");
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    tg?.ready(); tg?.expand();
    const u = tg?.initDataUnsafe?.user;
    if (u) setUser(u.first_name || u.username || "Пользователь");
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
  }, []);
  const go = (t: Tab) => { (window as any).Telegram?.WebApp?.HapticFeedback?.impactOccurred?.("light"); setTab(t); };
  const cards: { t: Tab; emo: string; title: string; sub: string; lime?: boolean }[] = [
    { t: "receipt", emo: "P", title: "Приёмка", sub: "Поставка и документы", lime: true },
    { t: "assemble", emo: "A", title: "Сборка", sub: "Изделия и подсборки" },
    { t: "stock", emo: "S", title: "Остатки", sub: "Поиск по складу" },
    { t: "orders", emo: "O", title: "Заказы", sub: "Прогресс" },
    { t: "moves", emo: "M", title: "Брак и возврат", sub: "Списание" },
    { t: "reports", emo: "R", title: "Отчёты", sub: "Excel и движения" },
    { t: "admin", emo: "U", title: "Люди", sub: "Доступы" },
  ];
  return (
    <div className="hrx-shell">
      <div className="hrx-top">
        <img src="/logo.png" alt="Гидробот" />
        <div><b>Склад Гидробот</b><small>Привет, {user}</small></div>
      </div>
      <div className="hrx-wrap">
        {tab === "home" && (<div className="hrx-grid">{cards.map((c) => (<button key={c.t} className={"hrx-card" + (c.lime ? " lime" : "")} onClick={() => go(c.t)}><span className="emo">{c.emo}</span><b>{c.title}</b><small>{c.sub}</small></button>))}</div>)}
        {tab === "receipt" && <ReceiptPage onDone={() => setRefresh(refresh + 1)} />}
        {tab === "stock" && <StockPage key={refresh} />}
        {tab === "assemble" && <AssemblePage />}
        {tab === "orders" && <OrdersPage onPick={() => go("assemble")} />}
        {tab === "moves" && <MovesPage />}
        {tab === "reports" && <ReportsPage />}
        {tab === "admin" && <AdminPage />}
      </div>
      <div className="hrx-tabs">{TABS.map((t) => (<button key={t.id} className={tab === t.id ? "on" : ""} onClick={() => go(t.id)}><span className="e">{t.emo}</span>{t.label}</button>))}</div>
    </div>
  );
}
