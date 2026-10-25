// Mini App: тёмная тема из Telegram, крупные кнопки, вкладки Приёмка/Остатки.
import { useEffect, useState } from "react";
import ReceiptPage from "./pages/ReceiptPage";
import StockPage from "./pages/StockPage";

export default function App() {
  const [user, setUser] = useState("Гость");
  const [tab, setTab] = useState<"receipt" | "stock">("receipt");
  const [refresh, setRefresh] = useState(0);
  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    tg?.ready(); tg?.expand();
    const u = tg?.initDataUnsafe?.user;
    if (u) setUser(u.first_name || u.username || "Пользователь");
    document.body.style.background = tg?.themeParams?.bg_color || "#17212b";
    document.body.style.color = tg?.themeParams?.text_color || "#fff";
    tg?.onEvent?.("qrTextReceived", () => {});
  }, []);
  const tabBtn = (active: boolean): any => ({ fontSize: 20, padding: "14px 10px", flex: 1, opacity: active ? 1 : 0.6 });
  return (
    <main style={{ padding: 16, fontFamily: "system-ui", maxWidth: 640, margin: "0 auto" }}>
      <h1>HRXWarehouse</h1>
      <p>Привет, {user}!</p>
      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <button style={tabBtn(tab === "receipt")} onClick={() => setTab("receipt")}>Приёмка</button>
        <button style={tabBtn(tab === "stock")} onClick={() => setTab("stock")}>Остатки</button>
      </div>
      {tab === "receipt" ? <ReceiptPage onDone={() => setRefresh(refresh + 1)} /> : <StockPage key={refresh} />}
    </main>
  );
}
