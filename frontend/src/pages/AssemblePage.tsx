// Сборка: изделия с фото, состав с фото (банку видно сразу), кнопка дособрать.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";

export default function AssemblePage() {
  const [prods, setProds] = useState<any[]>([]);
  const [sel, setSel] = useState<number | null>(null);
  const [comp, setComp] = useState<any[]>([]);
  const [chem, setChem] = useState<any[]>([]);
  const [qty, setQty] = useState(1);
  const [msg, setMsg] = useState("");
  const [needSubs, setNeedSubs] = useState<any[]>([]);
  const c = tgColors();
  const load = async () => setProds(await api("/api/products"));
  useEffect(() => { load(); }, []);
  const open = async (id: number) => { setSel(id); setMsg(""); setNeedSubs([]); const b = await api("/api/products/" + id + "/bom"); setComp(b.components); setChem(b.chemistry); };
  const check = async () => { if (sel == null) return; const b = await api("/api/assemble/check", "", { product_id: sel, qty }); setNeedSubs(b.need_subassemblies || []);
    setMsg(b.can ? "Можно собирать" : "Не хватает: " + b.missing.map((m: any) => m.sku + " (надо " + m.need + ", есть " + m.have + ")").join(", ")); };
  const buildSub = async (id: number) => { try { const r = await api("/api/assemble", "", { product_id: id, qty: 1, order_id: null }); setMsg("Дособрано: " + r.product); open(sel!); load(); } catch (e: any) { setMsg("Ошибка: " + e.message); } };
  const go = async () => { if (sel == null) return; try { setMsg("Собираю..."); const b = await api("/api/assemble", "", { product_id: sel, qty, order_id: null });
    setMsg("Готово: " + b.product + " x" + b.qty + (b.low?.length ? ". Ниже порога: " + b.low.join(", ") : "")); open(sel); load();
    } catch (e: any) { setMsg("Ошибка: " + e.message); } };
  const th: any = { width: 52, height: 52, borderRadius: 12, objectFit: "cover" };
  return (
    <div>
      <h2 style={{ margin: "8px 16px" }}>Сборка</h2>
      <div className="hrx-list" style={{ background: c.card, color: c.text }}>
        {prods.map((p) => (<button key={p.id} className="hrx-cell" onClick={() => open(p.id)}>
          {p.has_photo ? (<img src={"/api/items/" + p.id + "/photo"} alt="" style={th} />) : (<div className="hrx-thumb ph">?</div>)}
          <span className="tx">{p.name}<small>{p.sku} · на складе {p.qty}</small></span><span>›</span></button>))}
      </div>
      {sel != null && (<div className="hrx-panel" style={{ background: c.card, color: c.text, margin: "12px 16px" }}><h3>Состав</h3>
        <div className="hrx-list">
          {comp.map((x) => (<div key={x.id} className="hrx-cell">
            {x.has_photo ? (<img src={"/api/items/" + x.id + "/photo"} alt="" style={th} />) : (<div className="hrx-thumb ph">?</div>)}
            <span className="tx">{x.name}<small>{x.sku}: надо {x.need}, есть {x.have}</small></span>
            <span className={x.ok ? "hrx-ok" : "hrx-bad"}>{x.ok ? "✓" : "!"}</span></div>))}
        </div>
        {chem.length > 0 && (<div><div className="hrx-sec">Химия (не списывается)</div><div className="hrx-list" style={{ background: c.bg, color: c.text }}>
          {chem.map((x: any, i: number) => (<div key={i} className="hrx-cell">
            {x.has_photo ? (<img src={"/api/items/" + x.id + "/photo"} alt="" style={th} />) : (<div className="hrx-thumb ph">?</div>)}
            <span className="tx">{x.name}<small>{x.note || ""}</small></span></div>))}
        </div></div>)}
        {needSubs.length > 0 && (<div><div className="hrx-sec">Дособрать</div>
          {needSubs.map((s: any) => (<button key={s.item_id} className="hrx-btn ghost" onClick={() => buildSub(s.item_id)}>Дособрать: {s.name} (есть {s.have}, надо {s.need})</button>))}
        </div>)}
        <div className="hrx-row"><input className="hrx-inp" style={{ background: c.bg, color: c.text }} type="number" min={1} max={100} value={qty} onChange={(e) => setQty(Number(e.target.value))} />
        <button className="hrx-btn ghost" onClick={check}>Проверить</button></div>
        <button className="hrx-btn" onClick={go}>Собрать</button>
        {msg && <div className="hrx-msg">{msg}</div>}
      </div>)}
    </div>
  );
}
