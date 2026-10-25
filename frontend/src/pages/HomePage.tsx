// Главная как на референсе: привет, баланс-карточка, быстрые кнопки, лента, разделы.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";

export default function HomePage({ go }: { go: (t: any) => void }) {
  const [me, setMe] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [recent, setRecent] = useState<any[]>([]);
  useEffect(() => {
    api("/api/me").then(setMe).catch(() => setMe(null));
    api("/api/stats").then(setStats).catch(() => setStats(null));
    api("/api/recent").then(setRecent).catch(() => setRecent([]));
  }, []);
  const c = tgColors();
  const nm = me ? (me.first_name || me.username || "Гость") : "...";
  return (
    <div>
      <div className="hrx-bal">
        <small>Привет, {nm} · всего на складе</small>
        <div className="n">{stats ? stats.total_qty + " шт" : "..."}</div>
        <small>позиций: {stats?.total_items ?? "?"} · ниже порога: {stats?.low_count ?? "?"}</small>
        <div className="row">
          <button className="qbtn" onClick={() => go("receipt")}><b>+</b>Принять</button>
          <button className="qbtn" onClick={() => go("assemble")}><b>A</b>Собрать</button>
          <button className="qbtn" onClick={() => go("warehouse")}><b>W</b>Найти</button>
        </div>
      </div>
      <div className="hrx-me" style={{ background: c.card, color: c.text }} onClick={() => go("profile")}>
        {me && me.has_avatar ? (<img src={"/api/users/" + me.id + "/avatar"} alt="" />) : (<div className="init">{(nm[0] || "?").toUpperCase()}</div>)}
        <div><b>{nm}</b><small>{me?.position || (me?.roles || []).join(", ") || "кабинет"}</small></div>
        <span style={{ marginLeft: "auto", opacity: .3, fontSize: 20 }}>›</span>
      </div>
      {stats && stats.low_count > 0 && (<div><div className="hrx-sec">Срочно заказать <a onClick={() => go("warehouse")}>Все</a></div><div className="hrx-list" style={{ background: c.card, color: c.text }}>
        {stats.low.slice(0, 4).map((x: any) => (<div key={x.sku} className="hrx-cell" onClick={() => go("warehouse")}><span className="tx">{x.name}<small>{x.sku} · ост. {x.qty}</small></span><span className="hrx-bad">!</span></div>))}
      </div></div>)}
      {recent.length > 0 && (<div><div className="hrx-sec">Последние движения <a onClick={() => go("reports")}>Все</a></div><div className="hrx-list" style={{ background: c.card, color: c.text }}>
        {recent.slice(0, 4).map((x: any, i: number) => (<div key={i} className="hrx-cell"><span className="tx">{x.name}<small>{x.mtype_ru} · {x.qty} шт</small></span></div>))}
      </div></div>)}
      <div className="hrx-sec">Склад</div>
      <div className="hrx-list" style={{ background: c.card, color: c.text }}>
        <button className="hrx-cell" style={{ borderBottom: ".5px solid rgba(128,128,128,.2)" }} onClick={() => go("warehouse")}><span className="ic" style={{ background: "#007aff" }}>W</span><span className="tx">Склад<small>Папки, поиск, фото</small></span><span className="ch">›</span></button>
        <button className="hrx-cell" style={{ borderBottom: ".5px solid rgba(128,128,128,.2)" }} onClick={() => go("favs")}><span className="ic" style={{ background: "#ff9500" }}>F</span><span className="tx">Избранное<small>Моё быстрое</small></span><span className="ch">›</span></button>
        <button className="hrx-cell" style={{ borderBottom: ".5px solid rgba(128,128,128,.2)" }} onClick={() => go("orders")}><span className="ic" style={{ background: "#af52de" }}>O</span><span className="tx">Заказы<small>Прогресс</small></span><span className="ch">›</span></button>
        <button className="hrx-cell" onClick={() => go("catalog")}><span className="ic" style={{ background: "#34c759" }}>S</span><span className="tx">Стандарты<small>DIN, ISO, клеи</small></span><span className="ch">›</span></button>
      </div>
      <div className="hrx-sec">Ещё</div>
      <div className="hrx-list" style={{ background: c.card, color: c.text }}>
        <button className="hrx-cell" style={{ borderBottom: ".5px solid rgba(128,128,128,.2)" }} onClick={() => go("moves")}><span className="ic" style={{ background: "#ff3b30" }}>M</span><span className="tx">Брак и возврат<small>Списание</small></span><span className="ch">›</span></button>
        <button className="hrx-cell" style={{ borderBottom: ".5px solid rgba(128,128,128,.2)" }} onClick={() => go("reports")}><span className="ic" style={{ background: "#5ac8fa" }}>R</span><span className="tx">Отчёты<small>Excel и движения</small></span><span className="ch">›</span></button>
        <button className="hrx-cell" onClick={() => go("admin")}><span className="ic" style={{ background: "#8e8e93" }}>U</span><span className="tx">Люди<small>Доступы</small></span><span className="ch">›</span></button>
      </div>
    </div>
  );
}
