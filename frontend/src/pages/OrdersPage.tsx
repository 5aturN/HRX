// Заказы: прогресс + создание. Сверху всегда на склад.
import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function OrdersPage({ onPick }: { onPick: (orderId: number | null) => void }) {
  const [orders, setOrders] = useState<any[]>([]);
  const [cust, setCust] = useState("");
  const load = async () => setOrders(await api("/api/orders"));
  useEffect(() => { load(); }, []);
  const add = async () => { if (!cust.trim()) return; await api("/api/orders", "", { customer: cust, items: [] }); setCust(""); load(); };
  return (
    <div>
      <h2 style={{ margin: "8px 16px" }}>Заказы</h2>
      <button className="hrx-btn lime" onClick={() => onPick(null)}>Просто на склад</button>
      {orders.map((o: any) => { const need = o.items.reduce((s: number, i: any) => s + i.need, 0); const done = o.items.reduce((s: number, i: any) => s + i.done, 0); const pc = need ? Math.round((done / need) * 100) : 0;
        return (<div key={o.id} className="hrx-panel"><b>{o.customer}</b> — {o.status}<div className="hrx-progress"><i style={{ width: pc + "%" }} /></div><small>{done}/{need} ({pc}%)</small>
        <ul>{o.items.map((i: any, k: number) => (<li key={k}>{i.product}: {i.done}/{i.need}</li>))}</ul>
        <button className="hrx-btn ghost" onClick={() => onPick(o.id)}>Собирать в этот заказ</button></div>); })}
      <div className="hrx-row"><input className="hrx-inp" placeholder="Новый покупатель" value={cust} onChange={(e) => setCust(e.target.value)} /><button className="hrx-btn" style={{ width: 90 }} onClick={add}>+</button></div>
    </div>
  );
}
