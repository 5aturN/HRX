// Каталог стандартов: коды, названия, фото. Один раз завел — все пользуются.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";

export default function CatalogPage() {
  const [all, setAll] = useState<any[]>([]);
  const [code, setCode] = useState("");
  const [title, setTitle] = useState("");
  const [msg, setMsg] = useState("");
  const c = tgColors();
  const load = async () => { try { setAll(await api("/api/catalog")); } catch {} };
  useEffect(() => { load(); }, []);
  const add = async () => {
    if (!code.trim() || !title.trim()) { setMsg("Нужны код и название"); return; }
    try { await api("/api/catalog", "", { code, title }); setCode(""); setTitle(""); setMsg("Добавлено"); load(); }
    catch (e: any) { setMsg("Ошибка: " + e.message); }
  };
  const photo = async (cd: string, f: File | undefined) => {
    if (!f) return;
    const fd = new FormData(); fd.append("file", f);
    const tg = (window as any).Telegram?.WebApp;
    const r = await fetch("/api/catalog/" + cd + "/photo", { method: "POST", headers: { "X-Telegram-Init-Data": tg?.initData || "" }, body: fd });
    setMsg(r.ok ? "Фото обновлено" : "Ошибка"); load();
  };
  return (
    <div>
      <h2 style={{ margin: "8px 16px" }}>Стандарты</h2>
      <div className="hrx-sec">Что есть</div>
      <div className="hrx-list" style={{ background: c.card, color: c.text }}>
        {all.map((x) => (<div key={x.code} className="hrx-cell">
          {x.has_photo ? (<img src={"/api/catalog/" + x.code + "/photo"} alt="" style={{ width: 52, height: 52, borderRadius: 12, objectFit: "cover" }} />) : (<div className="hrx-thumb ph">?</div>)}
          <span className="tx"><b>{x.code}</b><small>{x.title}</small></span>
          <label style={{ fontSize: 12, opacity: .6 }}>фото<input type="file" accept="image/*" hidden onChange={(e) => photo(x.code, e.target.files?.[0])} /></label>
        </div>))}
        {all.length === 0 && <div className="hrx-cell">Пусто — добавьте первый</div>}
      </div>
      <div className="hrx-sec">Новый</div>
      <div className="hrx-panel" style={{ background: c.card, color: c.text }}>
        <input className="hrx-inp" style={{ background: c.bg, color: c.text }} placeholder="Код: DIN912" value={code} onChange={(e) => setCode(e.target.value)} />
        <input className="hrx-inp" style={{ background: c.bg, color: c.text }} placeholder="Название: Винт с цилиндрической головкой" value={title} onChange={(e) => setTitle(e.target.value)} />
        <button className="hrx-btn" onClick={add}>Добавить</button>
      </div>
      {msg && <div className="hrx-msg">{msg}</div>}
    </div>
  );
}
