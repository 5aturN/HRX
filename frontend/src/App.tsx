// Скелет Mini App: тёмная тема из Telegram.themeParams, крупные кнопки.
import { useEffect, useState } from "react";

export default function App() {
  const [user, setUser] = useState("Гость");
  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp;
    tg?.ready(); tg?.expand();
    const u = tg?.initDataUnsafe?.user;
    if (u) setUser(u.first_name || u.username || "Пользователь");
    document.body.style.background = tg?.themeParams?.bg_color || "#17212b";
    document.body.style.color = tg?.themeParams?.text_color || "#fff";
  }, []);
  return (
    <main style={{ padding: 16, fontFamily: "system-ui" }}>
      <h1>HRXWarehouse</h1>
      <p>Привет, {user}! Скелет Mini App (шаг 0).</p>
      <button style={{ fontSize: 20, padding: "16px 24px" }}>Приёмка (скоро)</button>
    </main>
  );
}
