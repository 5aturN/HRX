// Приемка: шапка + строки. Стандарт выбирается из каталога — название и фото сами.
import { useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";
import StdPicker from "../components/StdPicker";

type Row = { kind: string; sku: string; name: string; decimal: string; folder_id: number; qty: number; std_code: string };

const EMPTY = { kind: "standard", sku: "", name: "", decimal: "", folder_id: 1, qty: 1, std_code: "" };

export default function ReceiptPage({ onDone }: { onDone: () => void }) {
  const [supplier, setSupplier] = useState("");
  const [upd, setUpd] = useState("");
  const [invoice, setInvoice] = useState("");
  const [rows, setRows] = useState<Row[]>([{ ...EMPTY }]);
  const [msg, setMsg] = useState("");
  const c = tgColors();
  const set = (i: number, k: string, v: any) => { const cp = [...rows]; (cp[i] as any)[k] = v; setRows(cp); };
  const send = async () => {
    try {
      setMsg("Отправляю...");
      const body = { supplier, upd_no: upd || null, invoice_no: invoice || null,
        items: rows.map((x) => ({ kind: x.kind, sku: x.sku, name: x.name || null, decimal: x.decimal || null, folder_id: x.folder_id, qty: x.qty, std_code: x.std_code || null })) };
      const r = await api("/api/supplies", "", body);
      setMsg("Принято: поставка " + r.id + ", позиций " + r.positions);
      onDone();
    } catch (e: any) { setMsg("Ошибка: " + e.message); }
  };
  const inp = { background: c.bg, color: c.text };
  return (
    <div>
      <h2 style={{ margin: "8px 16px" }}>Приемка</h2>
      <div className="hrx-panel" style={{ background: c.card, color: c.text }}>
        <input className="hrx-inp" style={inp} placeholder="Поставщик" value={supplier} onChange={(e) => setSupplier(e.target.value)} />
        <div className="hrx-row"><input className="hrx-inp" style={inp} placeholder="УПД (можно позже)" value={upd} onChange={(e) => setUpd(e.target.value)} />
        <input className="hrx-inp" style={inp} placeholder="Счет" value={invoice} onChange={(e) => setInvoice(e.target.value)} /></div>
      </div>
      {rows.map((r, i) => (
        <div key={i} className="hrx-panel" style={{ background: c.card, color: c.text }}>
          <div className="hrx-row"><select className="hrx-inp" style={inp} value={r.kind} onChange={(e) => set(i, "kind", e.target.value)}><option value="standard">Покупнина</option><option value="detail">Деталь</option></select>
          <input className="hrx-inp" style={inp} type="number" min={1} value={r.qty} onChange={(e) => set(i, "qty", Number(e.target.value))} /></div>
          {r.kind === "standard" && (<StdPicker value={r.std_code} onPick={(code, title) => { set(i, "std_code", code); if (!r.name) set(i, "name", title); }} />)}
          <input className="hrx-inp" style={inp} placeholder="Артикул (размер: М6х20)" value={r.sku} onChange={(e) => set(i, "sku", e.target.value)} />
          <input className="hrx-inp" style={inp} placeholder="Название (подставится из каталога)" value={r.name} onChange={(e) => set(i, "name", e.target.value)} />
          {r.kind === "detail" && <input className="hrx-inp" style={inp} placeholder="Децимальный" value={r.decimal} onChange={(e) => set(i, "decimal", e.target.value)} />}
        </div>))}
      <div style={{ margin: "0 16px" }}><button className="hrx-btn ghost" onClick={() => setRows([...rows, { ...EMPTY }])}>+ Позиция</button>
      <button className="hrx-btn" onClick={send}>Принять</button></div>
      {msg && <div className="hrx-msg">{msg}</div>}
    </div>
  );
}
