// Отчёты: фильтр по датам, лента движений, Excel.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";
import { toast } from "../App";

export default function ReportsPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [df, setDf] = useState("");
  const [dto, setDto] = useState("");
  const [busy, setBusy] = useState(false);
  const c = tgColors();
  const load = async () => { setBusy(true); try { let q = "/api/moves?"; if (df) q += "date_from=" + df + "&"; if (dto) q += "date_to=" + dto; setRows(await api(q)); } catch (e: any) { toast(e.message, false); } setBusy(false); };
  useEffect(() => { load(); }, []);
  const xl = () => { const tg = (window as any).Telegram?.WebApp; let q = "/api/report/excel?init=" + encodeURIComponent(tg?.initData || ""); if (df) q += "&date_from=" + df; if (dto) q += "&date_to=" + dto; window.open(q, "_blank"); toast("Excel формируется"); };
  const inp: any = { background: c.card, color: c.text };
  return (
    <div>
      <h2 style={{ margin: "8px 16px" }}>Отчёты</h2>
      <div style={{ margin: "0 16px" }}><div className="hrx-row"><input className="hrx-inp" style={inp} type="date" value={df} onChange={(e) => setDf(e.target.value)} /><input className="hrx-inp" style={inp} type="date" value={dto} onChange={(e) => setDto(e.target.value)} /></div>
      <div className="hrx-row"><button className="hrx-btn ghost" disabled={busy} onClick={load}>{busy ? "..." : "Показать"}</button><button className="hrx-btn" onClick={xl}>Excel</button></div></div>
      <div className="hrx-sec">Движения · {rows.length}</div>
      <div className="hrx-list" style={{ background: c.card, color: c.text }}>
        {rows.slice(0, 60).map((r: any) => (<div key={r.id} className="hrx-cell"><span className="tx">{r.name}<small>{r.mtype_ru} · {r.date ? r.date.slice(0, 16).replace("T", " ") : ""}</small></span><span className="sum">{r.qty}<small>{r.sku}</small></span></div>))}
        {rows.length === 0 && !busy && <div className="hrx-cell">Пока пусто</div>}
        {busy && <div className="hrx-cell">Загрузка...</div>}
      </div>
    </div>
  );
}
