// Отчёты: движения с фильтрами + Excel.
import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function ReportsPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [df, setDf] = useState("");
  const [dto, setDto] = useState("");
  const load = async () => { let q = "/api/moves?"; if (df) q += "date_from=" + df + "&"; if (dto) q += "date_to=" + dto; setRows(await api(q)); };
  useEffect(() => { load(); }, []);
  const xl = () => { let q = "/api/report/excel?"; if (df) q += "date_from=" + df + "&"; if (dto) q += "date_to=" + dto; window.open(q, "_blank"); };
  return (
    <div>
      <h2>Отчёты</h2>
      <div className="hrx-row"><input className="hrx-inp" type="date" value={df} onChange={(e) => setDf(e.target.value)} /><input className="hrx-inp" type="date" value={dto} onChange={(e) => setDto(e.target.value)} /></div>
      <div className="hrx-row"><button className="hrx-btn ghost" onClick={load}>Показать</button><button className="hrx-btn" onClick={xl}>Excel</button></div>
      <table className="hrx-table"><thead><tr><th>Дата</th><th>Тип</th><th>Артикул</th><th>Кол.</th></tr></thead><tbody>
        {rows.slice(0, 100).map((r: any) => (<tr key={r.id}><td>{r.date?.slice(0, 16).replace("T", " ")}</td><td>{r.mtype_ru}</td><td>{r.sku}</td><td>{r.qty}</td></tr>))}
      </tbody></table>
    </div>
  );
}
