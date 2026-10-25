// Приёмка: шапка поставки + строки, выбор деталь/покупнина.
import { useState } from "react";
import { api } from "../api/client";

type Row = { kind: "detail" | "standard"; sku: string; name: string; decimal: string; folder_id: number; qty: number };

export default function ReceiptPage({ onDone }: { onDone: () => void }) {
  const [supplier, setSupplier] = useState("");
  const [upd, setUpd] = useState("");
  const [invoice, setInvoice] = useState("");
  const [rows, setRows] = useState<Row[]>([{ kind: "standard", sku: "", name: "", decimal: "", folder_id: 1, qty: 1 }]);
  const [msg, setMsg] = useState("");
  const set = (i: number, k: keyof Row, v: any) => { const c = [...rows]; (c[i] as any)[k] = v; setRows(c); };
  const send = async () => {
    try {
      setMsg("Отправляю...");
      const r = await api("/api/supplies", "", { supplier, upd_no: upd || null, invoice_no: invoice || null, items: rows.map((x) => ({ ...x, decimal: x.decimal || null })) });
      setMsg("Принято: поставка №" + r.id + ", позиций " + r.positions);
      onDone();
    } catch (e: any) { setMsg("Ошибка: " + e.message); }
  };
  return (
    <div>
      <h2>Приёмка</h2>
      <input className="hrx-inp" placeholder="Поставщик" value={supplier} onChange={(e) => setSupplier(e.target.value)} />
      <div className="hrx-row"><input className="hrx-inp" placeholder="№ УПД (можно позже)" value={upd} onChange={(e) => setUpd(e.target.value)} /><input className="hrx-inp" placeholder="№ счёта" value={invoice} onChange={(e) => setInvoice(e.target.value)} /></div>
      {rows.map((r, i) => (
        <div key={i} className="hrx-panel">
          <div className="hrx-row">
            <select className="hrx-inp" value={r.kind} onChange={(e) => set(i, "kind", e.target.value)}><option value="standard">Покупнина</option><option value="detail">Деталь (наша)</option></select>
            <input className="hrx-inp" type="number" min={1} value={r.qty} onChange={(e) => set(i, "qty", Number(e.target.value))} />
          </div>
          <input className="hrx-inp" placeholder="Артикул" value={r.sku} onChange={(e) => set(i, "sku", e.target.value)} />
          <input className="hrx-inp" placeholder="Название" value={r.name} onChange={(e) => set(i, "name", e.target.value)} />
          {r.kind === "detail" && <input className="hrx-inp" placeholder="Децимальный (обязательно)" value={r.decimal} onChange={(e) => set(i, "decimal", e.target.value)} />}
        </div>
      ))}
      <button className="hrx-btn ghost" onClick={() => setRows([...rows, { kind: "standard", sku: "", name: "", decimal: "", folder_id: 1, qty: 1 }])}>+ Позиция</button>
      <button className="hrx-btn" onClick={send}>Принять поставку</button>
      {msg && <div className="hrx-msg">{msg}</div>}
    </div>
  );
}
