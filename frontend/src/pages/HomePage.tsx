// Главная: логотип, кабинет, цифры, избранное, сегодня делали.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";

export default function HomePage({ go }: { go: (t: any) => void }) {
  const [me, setMe] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [favs, setFavs] = useState<any[]>([]);
  const [recent, setRecent] = useState<any[]>([]);
  useEffect(() => {
    api("/api/me").then(setMe).catch(() => setMe(null));
    api("/api/stats").then(setStats).catch(() => setStats(null));
    api("/api/favorites").then(setFavs).catch(() => setFavs([]));
    api("/api/recent").then(setRecent).catch(() => setRecent([]));
  }, []);
  const c = tgColors();
  return (
    <div>
      <div className="hrx-hero"><img src="/logo.png" alt="Гидробот" /><h1>Склад Гидробот</h1><p>Все для сборки в одном месте</p></div>
      <div className="hrx-me" style={{ background: c.card, color: c.text }} onClick={() => go("profile")}>
        {me && me.has_avatar ? (<img src={"/api/users/" + me.id + "/avatar"} alt="" />) : (<div className="init">?</div>)}
        <div><b>{me ? (me.first_name || me.username || "Гость") : "..."}</b><small>{me?.position || (me?.roles || []).join(", ") || ""}</small></div>
        <span style={{ marginLeft: "auto", opacity: .3 }}>›</span>
      </div>
      {stats && (<div className="hrx-me" style={{ background: c.card, color: c.text }}><div><b>{stats.total_qty} шт</b><small>позиций: {stats.total_items} · ниже порога: {stats.low_count}</small></div></div>)}
      {stats && stats.low_count > 0 && (<div><div className="hrx-sec">Срочно заказать</div><div className="hrx-list" style={{ background: c.card, color: c.text }}>
        {stats.low.slice(0, 5).map((x: any) => (<div key={x.sku} className="hrx-cell"><span className="tx">{x.name}<small>{x.sku} · ост. {x.qty}</small></span></div>))}
      </div></div>)}
      {favs.length > 0 && (<div><div className="hrx-sec">Мое избранное</div><div className="hrx-list" style={{ background: c.card, color: c.text }}>
        {favs.slice(0, 5).map((x: any) => (<div key={x.id} className="hrx-cell">
          {x.has_photo ? (<img src={"/api/items/" + x.id + "/photo"} alt="" style={{ width: 44, height: 44, borderRadius: 10, objectFit: "cover" }} />) : (<div className="hrx-thumb ph">?</div>)}
          <span className="tx">{x.name}<small>{x.sku} · ост. {x.qty}</small></span></div>))}
      </div></div>)}
      {recent.length > 0 && (<div><div className="hrx-sec">Сегодня делали</div><div className="hrx-list" style={{ background: c.card, color: c.text }}>
        {recent.slice(0, 5).map((x: any, i: number) => (<div key={i} className="hrx-cell"><span className="tx">{x.name}<small>{x.mtype_ru} · {x.qty} шт</small></span></div>))}
      </div></div>)}
      <div className="hrx-sec">Склад</div>
      <div className="hrx-list" style={{ background: c.card, color: c.text }}>
        <button className="hrx-cell" onClick={() => go("receipt")}><span className="tx">Приемка</span><span>›</span></button>
        <button className="hrx-cell" onClick={() => go("warehouse")}><span className="tx">Склад</span><span>›</span></button>
        <button className="hrx-cell" onClick={() => go("favs")}><span className="tx">Избранное</span><span>›</span></button>
        <button className="hrx-cell" onClick={() => go("assemble")}><span className="tx">Сборка</span><span>›</span></button>
        <button className="hrx-cell" onClick={() => go("orders")}><span className="tx">Заказы</span><span>›</span></button>
      </div>
      <div className="hrx-sec">Еще</div>
      <div className="hrx-list" style={{ background: c.card, color: c.text }}>
        <button className="hrx-cell" onClick={() => go("moves")}><span className="tx">Брак и возврат</span><span>›</span></button>
        <button className="hrx-cell" onClick={() => go("reports")}><span className="tx">Отчеты</span><span>›</span></button>
        <button className="hrx-cell" onClick={() => go("catalog")}><span className="tx">Стандарты</span><span>›</span></button>
        <button className="hrx-cell" onClick={() => go("admin")}><span className="tx">Люди</span><span>›</span></button>
      </div>
    </div>
  );
}
