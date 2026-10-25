// Сборка: изделия, состав, проверка, кнопка собрать.
import { useEffect, useState } from "react";
import { api } from "../api/client";

type Prod = { id: number; sku: string; name: string; kind: string; qty: number };
type Comp = { id: number; sku: string; name: string; need: number; have: number; ok: boolean };

export default function AssemblePage() {
  const [prods, setProds] = useState<Prod[]>([]);
  const [sel, setSel] = useState<number | null>(null);
  const [comp, setComp] = useState<Comp[]>([]);
  const [chem, setChem] = useState<{ name: string; note: string | null }[]>([]);
  const [qty, setQty] = useState(1);
  const [msg, setMsg] = useState("");
  const load = async () => setProds(await api("/api/products"));
  useEffect(() => { load(); }, []);
  const open = async (id: number) => { setSel(id); setMsg(""); const b = await api("/api/products/" + id + "/bom"); setComp(b.components); setChem(b.chemistry); };
  const check = async () => { if (sel == null) return; const b = await api("/api/assemble/check", "", { product_id: sel, qty });
    setMsg(b.can ? "Можно собирать" : "Не хватает: " + b.missing.map((m: any) => m.sku + " (надо " + m.need + ", есть " + m.have + ")").join(", ")); };
  const go = async () => { if (sel == null) return; try { setMsg("Собираю..."); const b = await api("/api/assemble", "", { product_id: sel, qty, order_id: null });
    setMsg("Готово: " + b.product + " x" + b.qty + (b.low?.length ? ". Ниже порога: " + b.low.join(", ") : "")); open(sel); load();
    } catch (e: any) { setMsg("Ошибка: " + e.message); } };
  return (
    <div>
      <h2 style={{ margin: "8px 16px" }}>Сборка</h2>
      {prods.map((p) => (<button key={p.id} className="hrx-btn ghost" onClick={() => open(p.id)}>{p.name} (на складе {p.qty})</button>))}
      {sel != null && (<div className="hrx-panel" style={{ margin: "12px 16px" }}><h3>Состав</h3>
        <ul>{comp.map((c) => (<li key={c.id} className={c.ok ? "hrx-ok" : "hrx-bad"}>{c.sku} — {c.name}: надо {c.need}, есть {c.have}</li>))}</ul>
        {chem.length > 0 && <div className="hrx-msg">Химия: {chem.map((c) => c.name).join(", ")}</div>}
        <div className="hrx-row"><input className="hrx-inp" type="number" min={1} max={100} value={qty} onChange={(e) => setQty(Number(e.target.value))} />
        <button className="hrx-btn ghost" onClick={check}>Проверить</button></div>
        <button className="hrx-btn" onClick={go}>Собрать</button>
        {msg && <div className="hrx-msg">{msg}</div>}
      </div>)}
    </div>
  );
}
