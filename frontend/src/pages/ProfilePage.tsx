// Кабинет: аватар, имя, должность, роли, моя статистика.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";

export default function ProfilePage() {
  const [me, setMe] = useState<any>(null);
  const [msg, setMsg] = useState("");
  const load = async () => { try { setMe(await api("/api/me")); } catch {} };
  useEffect(() => { load(); }, []);
  const c = tgColors();
  const up = async (f: File | undefined) => {
    if (!f) return;
    const fd = new FormData(); fd.append("file", f);
    const tg = (window as any).Telegram?.WebApp;
    const r = await fetch("/api/me/avatar", { method: "POST", headers: { "X-Telegram-Init-Data": tg?.initData || "" }, body: fd });
    setMsg(r.ok ? "Аватар обновлен" : "Ошибка: " + (await r.text())); load();
  };
  if (!me) return (<div className="hrx-msg">Загрузка...</div>);
  return (
    <div>
      <div className="hrx-hero">
        {me.has_avatar ? (<img src={"/api/users/" + me.id + "/avatar"} alt="" />) : (<div className="init" style={{ width: 96, height: 96, borderRadius: 48, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 40, color: "#fff", background: "linear-gradient(135deg,#007aff,#5e2bff)" }}>{(me.first_name?.[0] || "?")}</div>)}
        <h1>{me.first_name} {me.last_name || ""}</h1>
        <p>@{me.username || "?"} · {me.position || "должность не указана"}</p>
      </div>
      <div className="hrx-list" style={{ background: c.card, color: c.text }}>
        <div className="hrx-cell"><span className="tx">Роли<small>{(me.roles || []).join(", ")}</small></span></div>
        <div className="hrx-cell"><span className="tx">Мои движения за неделю<small>{me.week_moves}</small></span></div>
        <div className="hrx-cell"><span className="tx">Статус<small>{me.status}</small></span></div>
      </div>
      <div className="hrx-panel" style={{ background: c.card, color: c.text }}>
        <b>Сменить фото</b>
        <input className="hrx-inp" type="file" accept="image/*" onChange={(e) => up(e.target.files?.[0])} />
      </div>
      {msg && <div className="hrx-msg">{msg}</div>}
    </div>
  );
}
