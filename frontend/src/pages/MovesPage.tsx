// Брак, возврат, выдача в проект — всё в одном месте.
import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function MovesPage() {
  const [items, setItems] = useState<any[]>([]);
  const [q, setQ] = useState("");
  const [sel, setSel] = useState<any>(null);
  const [qty, setQty] = useState(1);
  const [reason, setReason] = useState("");
  const [projects, setProjects] = useState<any[]>([]);
  const [proj, setProj] = useState<number | null>(null);
  const [msg, setMsg] = useState("");
  const find = async () => setItems(await api("/api/stock?q=" + encodeURIComponent(q)));
  useEffect(() => { api("/api/projects").then(setProjects).catch(() => setProjects([])); }, []);
  const go = async (path: string, extra: any = {}) => {
    if (!sel) { setMsg("Сначала выберите позицию"); return; }
    try { setMsg("Отправляю...");
      const r = await api(path, "", { item_id: sel.id, qty, reason: reason || null, project_folder_id: proj, ...extra });
      setMsg("Готово: " + r.sku + ", остаток " + r.qty);
      find();
    } catch (e: any) { setMsg("Ошибка: " + e.message); }
  };
  return (
    <div>
      <h2>Брак и возврат</h2>
      <div className="hrx-row"><input className="hrx-inp" placeholder="Найти позицию..." value={q} onChange={(e) => setQ(e.target.value)} /><button className="hrx-btn" style={{ width: 120 }} onClick={find}>Найти</button></div>
      {items.slice(0, 8).map((i: any) => (<button key={i.id} className="hrx-btn ghost" onClick={() => setSel(i)}>{i.sku} — {i.name} (ост. {i.qty})</button>))}
      {sel && (<div className="hrx-panel"><b>{sel.sku} — {sel.name}</b>
        <div className="hrx-row"><input className="hrx-inp" type="number" min={1} value={qty} onChange={(e) => setQty(Number(e.target.value))} /><input className="hrx-inp" placeholder="Причина (для брака обязательно)" value={reason} onChange={(e) => setReason(e.target.value)} /></div>
        <div className="hrx-row"><select className="hrx-inp" value={proj ?? ""} onChange={(e) => setProj(e.target.value ? Number(e.target.value) : null)}><option value="">Проект...</option>{projects.map((p: any) => (<option key={p.id} value={p.id}>{p.name}</option>))}</select></div>
        <button className="hrx-btn violet" onClick={() => go("/api/scrap")}>В брак</button>
        <button className="hrx-btn ghost" onClick={() => go("/api/unscrap")}>Вернуть на склад</button>
        <button className="hrx-btn ghost" onClick={() => { if (!proj) { setMsg("Выберите проект"); return; } go("/api/to-project"); }}>Выдать в проект</button>
      </div>)}
      {msg && <div className="hrx-msg">{msg}</div>}
    </div>
  );
}
