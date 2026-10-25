// Экран заказов: список с прогрессом + создание. Сверху всегда "просто на склад".
import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function OrdersPage({ onPick }: { onPick: (orderId: number | null) => void }) {
  const [orders, setOrders] = useState<any[]>([]);
  const [cust, setCust] = useState("");
  const load = async () => setOrders(await api("/api/orders"));
  useEffect(() => { load(); }, []);
  const add = async () => {
    if (!cust.trim()) return;
    await api("/api/orders", "", { customer: cust, items: [] });
    setCust(""); load();
  };
  return (
    <div>
      <h2>Заказы</h2>
      <button style={{ fontSize: 20, padding: 16, width: "100%" }} onClick={() => onPick(null)}>Просто на склад (без заказа)</button>
      {orders.map((o: any) => (
        <div key={o.id} style={{ border: "1px solid #555", borderRadius: 8, padding: 8, margin: "8px 0" }}>
          <b>{o.customer}</b> — {o.status}
          <ul>{o.items.map((i: any, k: number) => <li key={k}>{i.product}: {i.done}/{i.need}</li>)}</ul>
          <button style={{ fontSize: 18, padding: 12, width: "100%" }} onClick={() => onPick(o.id)}>Собирать в этот заказ</button>
        </div>
      ))}
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <input placeholder="Новый покупатель" value={cust} onChange={(e) => setCust(e.target.value)} style={{ fontSize: 18, padding: 12, flex: 1 }} />
        <button style={{ fontSize: 18, padding: 12 }} onClick={add}>+</button>
      </div>
    </div>
  );
}
