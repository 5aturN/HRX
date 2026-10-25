// Экран приёмки: шапка поставки + строки (деталь/покупнина) + кнопка.
// Крупные кнопки, тёмная тема из Telegram.
import { useState } from "react";
import { api } from "../api/client";

type Row = { kind: "detail" | "standard"; sku: string; name: string; decimal: string; folder_id: number; qty: number };

export default function ReceiptPage({ onDone }: { onDone: () => void }) {
  const [supplier, setSupplier] = useState("");
  const [upd, setUpd] = useState("");
  const [invoice, setInvoice] = useState("");
  const [rows, setRows] = useState<Row[]>([{ kind: "standard", sku: "", name: "", decimal: "", folder_id: 1, qty: 1 }]);
  const [msg, setMsg] = useState("");
  const add = () => setRows([...rows, { kind: "standard", sku: "", name: "", decimal: "", folder_id: 1, qty: 1 }]);
  const send = async () => {
    try {
      setMsg("Отправляю...");
      const r = await api("/api/supplies", "", { supplier, upd_no: upd || null, invoice_no: invoice || null, items: rows.map((x) => ({ ...x, decimal: x.decimal || null })) });
      setMsg("Принято: поставка №" + r.id + ", позиций " + r.positions);
      onDone();
    } catch (e: any) { setMsg("Ошибка: " + e.message); }
  };
  const inp = { fontSize: 18, padding: 12, margin: "4px 0", width: "100%", boxSizing: "border-box" as const };
  return (
    <div>
      <h2>Приёмка</h2>
      <input style={inp} placeholder="Поставщик" value={supplier} onChange={(e) => setSupplier(e.target.value)} />
      <input style={inp} placeholder="№ УПД (можно позже)" value={upd} onChange={(e) => setUpd(e.target.value)} />
      <input style={inp} placeholder="№ счёта" value={invoice} onChange={(e) => setInvoice(e.target.value)} />
      {rows.map((r, i) => (
        <div key={i} style={{ border: "1px solid #555", borderRadius: 8, padding: 8, margin: "8px 0" }}>
          <select style={inp} value={r.kind} onChange={(e) => { const c = [...rows]; c[i].kind = e.target.value as any; setRows(c); }}>
            <option value="standard">Покупнина</option>
            <option value="detail">Деталь (наша)</option>
          </select>
          <input style={inp} placeholder="Артикул" value={r.sku} onChange={(e) => { const c = [...rows]; c[i].sku = e.target.value; setRows(c); }} />
          <input style={inp} placeholder="Название" value={r.name} onChange={(e) => { const c = [...rows]; c[i].name = e.target.value; setRows(c); }} />
          {r.kind === "detail" && <input style={inp} placeholder="Децимальный (обязательно)" value={r.decimal} onChange={(e) => { const c = [...rows]; c[i].decimal = e.target.value; setRows(c); }} />}
          <input style={inp} type="number" min={1} placeholder="Кол-во" value={r.qty} onChange={(e) => { const c = [...rows]; c[i].qty = Number(e.target.value); setRows(c); }} />
        </div>
      ))}
      <button style={{ fontSize: 20, padding: 16, width: "100%" }} onClick={add}>+ Позиция</button>
      <button style={{ fontSize: 22, padding: 18, width: "100%", marginTop: 8 }} onClick={send}>Принять</button>
      <p>{msg}</p>
    </div>
  );
}
