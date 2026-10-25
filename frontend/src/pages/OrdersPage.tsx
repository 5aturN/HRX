// Заказы: прогресс, создание, статусы. Сборка идёт в выбранный заказ.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";
import { toast } from "../App";

const ST: any = { new: "Новый", work: "В работе", done: "Готов", shipped: "Отгружен" };
export default function OrdersPage({ onPick }: { onPick: (orderId: number | null) => void }) {
  const [orders, setOrders] = useState<any[]>([]);
  const [cust, setCust] = useState("");
  const c = tgColors();
  const load = async () => { try { setOrders(await api("/api/orders")); } catch (e: any) { toast(e.message, false); } };
  useEffect(() => { load(); }, []);
  const add = async () => { if (!cust.trim()) { toast("Укажите покупателя", false); return; } try { await api("/api/orders", "", { customer: cust, items: [] }); setCust(""); toast("Заказ создан"); load(); } catch (e: any) { toast(e.message, false); } };
  const st = async (id: number, status: string) => { try { await api("/api/orders/" + id + "/status", "", { status }); toast("Статус: " + ST[status]); load(); } catch (e: any) { toast(e.message, false); } };
  return (
    <div>
      <h2 style={{ margin: "8px 16px" }}>Заказы</h2>
      <div style={{ margin: "0 16px" }}><button className="hrx-btn ghost" onClick={() => onPick(null)}>Просто на склад (без заказа)</button></div>
      {orders.map((o: any) => { const need = o.items.reduce((s: number, i: any) => s + i.need, 0); const done = o.items.reduce((s: number, i: any) => s + i.done, 0); const pc = need ? Math.round((done / need) * 100) : 0;
        return (<div key={o.id} className="hrx-panel" style={{ background: c.card, color: c.text }}><b>{o.customer}</b> <small>· {ST[o.status] || o.status}</small><div className="hrx-progress"><i style={{ width: pc + "%" }} /></div><small>{done}/{need} ({pc}%)</small>
        {o.items.map((i: any, k: number) => (<div key={k} style={{ fontSize: 13, opacity: .7 }}>{i.product}: {i.done}/{i.need}</div>))}
        <div className="hrx-row"><button className="hrx-btn" onClick={() => onPick(o.id)}>Собирать</button>
        {o.status === "new" && <button className="hrx-btn ghost" onClick={() => st(o.id, "work")}>В работу</button>}
        {o.status === "work" && <button className="hrx-btn ghost" onClick={() => st(o.id, "done")}>Готов</button>}
        {o.status === "done" && <button className="hrx-btn ghost" onClick={() => st(o.id, "shipped")}>Отгружен</button>}</div></div>); })}
      <div className="hrx-panel" style={{ background: c.card, color: c.text }}><div className="hrx-row"><input className="hrx-inp" style={{ background: c.bg, color: c.text }} placeholder="Новый покупатель" value={cust} onChange={(e) => setCust(e.target.value)} /><button className="hrx-btn" style={{ width: 80 }} onClick={add}>+</button></div></div>
    </div>
  );
}
