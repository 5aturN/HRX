// Экран сборки: список изделий, состав, проверка, кнопка собрать.
// Сначала предлагает дособрать подсборки, сам ничего не собирает молча.
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
  const [missing, setMissing] = useState<any[]>([]);
  const load = async () => setProds(await api("/api/products"));
  useEffect(() => { load(); }, []);
  const open = async (id: number) => {
    setSel(id); setMsg(""); setMissing([]);
    const b = await api("/api/products/" + id + "/bom");
    setComp(b.components); setChem(b.chemistry);
  };
  const check = async () => {
    if (sel == null) return;
    const b = await api("/api/assemble/check", "", { product_id: sel, qty });
    setMissing(b.missing);
    setMsg(b.can ? "Можно собирать" : "Не хватает: " + b.missing.map((m: any) => m.sku + " (надо " + m.need + ", есть " + m.have + ")").join(", "));
  };
  const go = async () => {
    if (sel == null) return;
    try {
      setMsg("Собираю...");
      const b = await api("/api/assemble", "", { product_id: sel, qty, order_id: null });
      setMsg("Готово: " + b.product + " x" + b.qty + (b.low?.length ? ". Ниже порога: " + b.low.join(", ") : ""));
      open(sel); load();
    } catch (e: any) { setMsg("Ошибка: " + e.message); }
  };
  const big = { fontSize: 20, padding: 16, width: "100%", marginTop: 8 } as const;
  return (
    <div>
      <h2>Сборка</h2>
      {prods.map((p) => (
        <button key={p.id} style={{ ...big, opacity: sel === p.id ? 1 : 0.85 }} onClick={() => open(p.id)}>
          {p.name} (на складе {p.qty})
        </button>
      ))}
      {sel != null && (
        <div style={{ marginTop: 12 }}>
          <h3>Состав</h3>
          <ul>{comp.map((c) => <li key={c.id} style={{ color: c.ok ? "#8f8" : "#f88" }}>{c.sku} — {c.name}: надо {c.need}, есть {c.have}</li>)}</ul>
          {chem.length > 0 && <p>Химия (пометка): {chem.map((c) => c.name).join(", ")}</p>}
          <label>Сколько: <input type="number" min={1} max={100} value={qty} onChange={(e) => setQty(Number(e.target.value))} style={{ fontSize: 20, padding: 8, width: 80 }} /></label>
          <button style={big} onClick={check}>Проверить</button>
          <button style={{ ...big, fontSize: 24 }} onClick={go}>Собрать</button>
          <p>{msg}</p>
          {missing.length > 0 && <p>Дособерите подсборки или дождитесь поставки</p>}
        </div>
      )}
    </div>
  );
}
