// Mini App: тёмная тема из Telegram, крупные кнопки.
import { useEffect, useState } from "react";
import ReceiptPage from "./pages/ReceiptPage";
import StockPage from "./pages/StockPage";
import AssemblePage from "./pages/AssemblePage";
import ReportsPage from "./pages/ReportsPage";
import OrdersPage from "./pages/OrdersPage";
import AdminPage from "./pages/AdminPage";

type Tab = "receipt" | "stock" | "assemble" | "orders" | "reports" | "admin";

export default function App() {
  const [user, setUser] = useState("Гость");
  const [tab, setTab] = useState<Tab>("receipt");
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    tg?.ready(); tg?.expand();
    const u = tg?.initDataUnsafe?.user;
    if (u) setUser(u.first_name || u.username || "Пользователь");
    document.body.style.background = tg?.themeParams?.bg_color || "#17212b";
    document.body.style.color = tg?.themeParams?.text_color || "#fff";
  }, []);
  const tabBtn = (active: boolean): any => ({ fontSize: 18, padding: "12px 8px", flex: 1, opacity: active ? 1 : 0.6 });
  return (
    <main style={{ padding: 16, fontFamily: "system-ui", maxWidth: 640, margin: "0 auto" }}>
      <h1>HRXWarehouse</h1>
      <p>Привет, {user}!</p>
      <div style={{ display: "flex", gap: 6, marginBottom: 12, flexWrap: "wrap" }}>
        <button style={tabBtn(tab === "receipt")} onClick={() => setTab("receipt")}>Приёмка</button>
        <button style={tabBtn(tab === "stock")} onClick={() => setTab("stock")}>Остатки</button>
        <button style={tabBtn(tab === "assemble")} onClick={() => setTab("assemble")}>Сборка</button>
        <button style={tabBtn(tab === "orders")} onClick={() => setTab("orders")}>Заказы</button>
        <button style={tabBtn(tab === "reports")} onClick={() => setTab("reports")}>Отчёты</button>
        <button style={tabBtn(tab === "admin")} onClick={() => setTab("admin")}>Люди</button>
      </div>
      {tab === "receipt" && <ReceiptPage onDone={() => setRefresh(refresh + 1)} />}
      {tab === "stock" && <StockPage key={refresh} />}
      {tab === "assemble" && <AssemblePage />}
      {tab === "orders" && <OrdersPage onPick={() => setTab("assemble")} />}
      {tab === "reports" && <ReportsPage />}
      {tab === "admin" && <AdminPage />}
    </main>
  );
}
