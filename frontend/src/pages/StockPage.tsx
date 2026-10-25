// Остатки: поиск, русские колонки, подсветка нехватки.
import { useEffect, useState } from "react";
import { api } from "../api/client";

type Row = { id: number; sku: string; name: string; decimal: string | null; folder: string; qty: number; threshold: number; low: boolean };

export default function StockPage() {
  const [q, setQ] = useState("");
  const [rows, setRows] = useState<Row[]>([]);
  const load = async () => setRows(await api("/api/stock?q=" + encodeURIComponent(q)));
  useEffect(() => { load(); }, []);
  return (
    <div>
      <h2>Остатки</h2>
      <div className="hrx-row"><input className="hrx-inp" style={{ background: "rgba(128,128,128,.12)" }} placeholder="Артикул, название, децимальный..." value={q} onChange={(e) => setQ(e.target.value)} /><button className="hrx-btn" style={{ width: 120 }} onClick={load}>Найти</button></div>
      <table className="hrx-table"><thead><tr><th>Артикул</th><th>Наименование</th><th>Ост.</th><th>Порог</th></tr></thead><tbody>
        {rows.map((r) => (<tr key={r.id} className={r.low ? "hrx-low" : ""}><td><b>{r.sku}</b><br /><small style={{ color: "#9a9aa5" }}>{r.folder}</small></td><td>{r.name}{r.low && <span className="hrx-bad"> Низко</span>}</td><td><b>{r.qty}</b></td><td>{r.threshold}</td></tr>))}
      </tbody></table>
      {rows.length === 0 && <div className="hrx-msg">Ничего не нашлось</div>}
    </div>
  );
}
