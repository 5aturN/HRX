// Брак, возврат, выдача в проект: поиск с фото, тосты, тактильный отклик.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";
import { toast } from "../App";

export default function MovesPage() {
  const [items, setItems] = useState<any[]>([]);
  const [q, setQ] = useState("");
  const [sel, setSel] = useState<any>(null);
  const [qty, setQty] = useState(1);
  const [reason, setReason] = useState("");
  const [projects, setProjects] = useState<any[]>([]);
  const [proj, setProj] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const c = tgColors();
  const find = async () => { try { setItems(await api("/api/stock?q=" + encodeURIComponent(q))); } catch (e: any) { toast(e.message, false); } };
  useEffect(() => { api("/api/projects").then(setProjects).catch(() => setProjects([])); }, []);
  const buzz = (t: string) => { try { (window as any).Telegram?.WebApp?.HapticFeedback?.notificationOccurred?.(t); } catch {} };
  const go = async (path: string, label: string) => {
    if (!sel) { toast("Сначала выберите позицию", false); return; }
    if (qty < 1) { toast("Количество минимум 1", false); return; }
    setBusy(true);
    try {
      const r = await api(path, "", { item_id: sel.id, qty, reason: reason || null, project_folder_id: proj });
      buzz("success"); toast(label + ": " + r.sku + ", остаток " + r.qty);
      setSel({ ...sel, qty: r.qty }); find();
    } catch (e: any) { buzz("error"); toast(e.message, false); }
    setBusy(false);
  };
  const inp: any = { background: c.card, color: c.text };
  return (
    <div>
      <h2 style={{ margin: "8px 16px" }}>Брак и возврат</h2>
      <div style={{ margin: "0 16px" }}><div className="hrx-row"><input className="hrx-inp" style={inp} placeholder="Найти позицию..." value={q} onChange={(e) => setQ(e.target.value)} /><button className="hrx-btn" style={{ width: 110 }} onClick={find}>Найти</button></div></div>
      {items.length > 0 && (<div className="hrx-list" style={{ background: c.card, color: c.text }}>
        {items.slice(0, 8).map((i: any) => (<button key={i.id} className="hrx-cell" style={{ borderBottom: ".5px solid rgba(128,128,128,.2)" }} onClick={() => { setSel(i); buzz("light"); }}>
          {i.has_photo ? (<img src={"/api/items/" + i.id + "/photo"} alt="" className="hrx-thumb" />) : (<div className="hrx-thumb ph">?</div>)}
          <span className="tx">{i.name}<small>{i.sku} · ост. {i.qty}</small></span>{sel?.id === i.id && <span>✓</span>}</button>))}
      </div>)}
      {sel && (<div className="hrx-panel" style={{ background: c.card, color: c.text }}>
        <div className="hrx-cell"><b>{sel.sku} — {sel.name}</b></div>
        <div className="hrx-row"><input className="hrx-inp" style={inp} type="number" min={1} value={qty} onChange={(e) => setQty(Number(e.target.value))} />
        <input className="hrx-inp" style={inp} placeholder="Причина" value={reason} onChange={(e) => setReason(e.target.value)} /></div>
        <select className="hrx-inp" style={inp} value={proj ?? ""} onChange={(e) => setProj(e.target.value ? Number(e.target.value) : null)}><option value="">Проект для выдачи...</option>{projects.map((p: any) => (<option key={p.id} value={p.id}>{p.name}</option>))}</select>
        <button className="hrx-btn" style={{ background: "#ff453a", color: "#fff" }} disabled={busy} onClick={() => go("/api/scrap", "В брак")}>В брак</button>
        <button className="hrx-btn ghost" disabled={busy} onClick={() => go("/api/unscrap", "Возврат")}>Вернуть на склад</button>
        <button className="hrx-btn ghost" disabled={busy} onClick={() => { if (!proj) { toast("Выберите проект", false); return; } go("/api/to-project", "Выдано"); }}>Выдать в проект</button>
      </div>)}
    </div>
  );
}
