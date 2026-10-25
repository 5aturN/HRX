// Главная: логотип, кабинет, разделы. Стиль iOS-списков.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";

export default function HomePage({ go }: { go: (t: any) => void }) {
  const [me, setMe] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  useEffect(() => {
    api("/api/me").then(setMe).catch(() => setMe(null));
    api("/api/stats").then(setStats).catch(() => setStats(null));
  }, []);
  const c = tgColors();
  const ini = "?";
  return (
    <div>
      <div className="hrx-hero">
        <img src="/logo.png" alt="Гидробот" />
        <h1>Склад Гидробот</h1>
        <p>Все для сборки в одном месте</p>
      </div>
      <div className="hrx-me" style={{ background: c.card, color: c.text }} onClick={() => go("profile")}>
        {me && me.has_avatar ? (<img src={"/api/users/" + me.id + "/avatar"} alt="" />) : (<div className="init">{ini}</div>)}
        <div><b>{me ? (me.first_name || me.username || "Гость") : "..."}</b></div>
      </div>
      {stats && (<div className="hrx-me" style={{ background: c.card, color: c.text }}><div><b>{stats.total_qty} шт</b></div></div>)}
      <div className="hrx-sec">Склад</div>
      <div className="hrx-list" style={{ background: c.card, color: c.text }}>
        <button className="hrx-cell" onClick={() => go("receipt")}><span className="tx">Приемка</span></button>
        <button className="hrx-cell" onClick={() => go("warehouse")}><span className="tx">Склад</span></button>
        <button className="hrx-cell" onClick={() => go("assemble")}><span className="tx">Сборка</span></button>
        <button className="hrx-cell" onClick={() => go("orders")}><span className="tx">Заказы</span></button>
      </div>
      <div className="hrx-sec">Еще</div>
      <div className="hrx-list" style={{ background: c.card, color: c.text }}>
        <button className="hrx-cell" onClick={() => go("moves")}><span className="tx">Брак и возврат</span></button>
        <button className="hrx-cell" onClick={() => go("reports")}><span className="tx">Отчеты</span></button>
        <button className="hrx-cell" onClick={() => go("admin")}><span className="tx">Люди</span></button>
      </div>
    </div>
  );
}
