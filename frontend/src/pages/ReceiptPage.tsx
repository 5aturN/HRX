// Приемка: шапка + строки, фото позиции сразу.
import { useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";

type Row = { kind: string; sku: string; name: string; decimal: string; folder_id: number; qty: number; photo?: File };

export default function ReceiptPage({ onDone }: { onDone: () => void }) {
  const [supplier, setSupplier] = useState("");
  const [upd, setUpd] = useState("");
  const [invoice, setInvoice] = useState("");
  const [rows, setRows] = useState<Row[]>([{ kind: "standard", sku: "", name: "", decimal: "", folder_id: 1, qty: 1 }]);
  const [msg, setMsg] = useState("");
  const c = tgColors();
  const set = (i: number, k: string, v: any) => { const cp = [...rows]; (cp[i] as any)[k] = v; setRows(cp); };
  const send = async () => {
    try {
      setMsg("Отправляю...");
      const body = { supplier, upd_no: upd || null, invoice_no: invoice || null, items: rows.map((x) => ({ kind: x.kind, sku: x.sku, name: x.name, decimal: x.decimal || null, folder_id: x.folder_id, qty: x.qty })) };
      const r = await api("/api/supplies", "", body);
      const tg = (window as any).Telegram?.WebApp;
      for (const x of rows) {
        if (x.photo && x.sku) {
          try {
            const all = await api("/api/stock?q=" + encodeURIComponent(x.sku));
            const it = all.find((a: any) => a.sku === x.sku);
            if (it) { const fd = new FormData(); fd.append("file", x.photo);
              await fetch("/api/items/" + it.id + "/photo", { method: "POST", headers: { "X-Telegram-Init-Data": tg?.initData || "" }, body: fd }); }
          } catch {}
        }
      }
      setMsg("Принято: поставка " + r.id + ", позиций " + r.positions);
      onDone();
    } catch (e: any) { setMsg("Ошибка: " + e.message); }
  };
  return (
    <div>
      <h2 style={{ margin: "8px 16px" }}>Приемка</h2>
      <div className="hrx-panel" style={{ background: c.card, color: c.text }}>
        <input className="hrx-inp" style={{ background: c.bg, color: c.text }} placeholder="Поставщик" value={supplier} onChange={(e) => setSupplier(e.target.value)} />
        <div className="hrx-row"><input className="hrx-inp" style={{ background: c.bg, color: c.text }} placeholder="УПД (можно позже)" value={upd} onChange={(e) => setUpd(e.target.value)} />
        <input className="hrx-inp" style={{ background: c.bg, color: c.text }} placeholder="Счет" value={invoice} onChange={(e) => setInvoice(e.target.value)} /></div>
      </div>
      {rows.map((r, i) => (
        <div key={i} className="hrx-panel" style={{ background: c.card, color: c.text }}>
          <div className="hrx-row"><select className="hrx-inp" style={{ background: c.bg, color: c.text }} value={r.kind} onChange={(e) => set(i, "kind", e.target.value)}><option value="standard">Покупнина</option><option value="detail">Деталь</option></select>
          <input className="hrx-inp" style={{ background: c.bg, color: c.text }} type="number" min={1} value={r.qty} onChange={(e) => set(i, "qty", Number(e.target.value))} /></div>
          <input className="hrx-inp" style={{ background: c.bg, color: c.text }} placeholder="Артикул" value={r.sku} onChange={(e) => set(i, "sku", e.target.value)} />
          <input className="hrx-inp" style={{ background: c.bg, color: c.text }} placeholder="Название" value={r.name} onChange={(e) => set(i, "name", e.target.value)} />
          {r.kind === "detail" && <input className="hrx-inp" style={{ background: c.bg, color: c.text }} placeholder="Децимальный" value={r.decimal} onChange={(e) => set(i, "decimal", e.target.value)} />}
          <input className="hrx-inp" style={{ background: c.bg, color: c.text }} type="file" accept="image/*" onChange={(e) => set(i, "photo", e.target.files?.[0])} />
        </div>))}
      <div style={{ margin: "0 16px" }}><button className="hrx-btn ghost" onClick={() => setRows([...rows, { kind: "standard", sku: "", name: "", decimal: "", folder_id: 1, qty: 1 }])}>+ Позиция</button>
      <button className="hrx-btn" onClick={send}>Принять</button></div>
      {msg && <div className="hrx-msg">{msg}</div>}
    </div>
  );
}
