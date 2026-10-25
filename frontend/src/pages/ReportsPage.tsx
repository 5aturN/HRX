// Экран отчётов: движения с фильтрами + кнопка скачать Excel.
import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function ReportsPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [df, setDf] = useState("");
  const [dto, setDto] = useState("");
  const load = async () => {
    let q = "/api/moves?";
    if (df) q += "date_from=" + df + "&";
    if (dto) q += "date_to=" + dto;
    setRows(await api(q));
  };
  useEffect(() => { load(); }, []);
  const xl = () => {
    let q = "/api/report/excel?";
    if (df) q += "date_from=" + df + "&";
    if (dto) q += "date_to=" + dto;
    window.open(q, "_blank");
  };
  return (
    <div>
      <h2>Отчёты</h2>
      <div style={{ display: "flex", gap: 8 }}>
        <input type="date" value={df} onChange={(e) => setDf(e.target.value)} style={{ fontSize: 16, padding: 10, flex: 1 }} />
        <input type="date" value={dto} onChange={(e) => setDto(e.target.value)} style={{ fontSize: 16, padding: 10, flex: 1 }} />
      </div>
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <button style={{ fontSize: 18, padding: 14, flex: 1 }} onClick={load}>Показать</button>
        <button style={{ fontSize: 18, padding: 14, flex: 1 }} onClick={xl}>Скачать Excel</button>
      </div>
      <table style={{ width: "100%", marginTop: 12, fontSize: 14, borderCollapse: "collapse" }}>
        <thead><tr><th>Дата</th><th>Тип</th><th>Артикул</th><th>Кол-во</th></tr></thead>
        <tbody>{rows.slice(0, 100).map((r: any) => <tr key={r.id}><td>{r.date?.slice(0, 16).replace("T", " ")}</td><td>{r.mtype_ru}</td><td>{r.sku}</td><td>{r.qty}</td></tr>)}</tbody>
      </table>
    </div>
  );
}
