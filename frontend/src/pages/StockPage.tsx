// Экран остатков: поиск + русские колонки + подсветка нехватки.
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
      <div style={{ display: "flex", gap: 8 }}>
        <input style={{ fontSize: 18, padding: 12, flex: 1 }} placeholder="Артикул, название, децимальный..." value={q} onChange={(e) => setQ(e.target.value)} />
        <button style={{ fontSize: 18, padding: 12 }} onClick={load}>Найти</button>
      </div>
      <table style={{ width: "100%", marginTop: 12, borderCollapse: "collapse", fontSize: 15 }}>
        <thead><tr><th>Артикул</th><th>Наименование</th><th>Остаток</th><th>Порог</th></tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} style={{ background: r.low ? "#5a1a1a" : "transparent" }}>
              <td>{r.sku}</td><td>{r.name}</td><td>{r.qty}</td><td>{r.threshold}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length === 0 && <p>Ничего не нашлось</p>}
    </div>
  );
}
