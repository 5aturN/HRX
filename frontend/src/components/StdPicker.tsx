// Выбор стандарта из каталога: код -> название и фото сами.
import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function StdPicker({ value, onPick }: { value: string; onPick: (code: string, title: string) => void }) {
  const [all, setAll] = useState<any[]>([]);
  const [q, setQ] = useState(value || "");
  const [open, setOpen] = useState(false);
  useEffect(() => { api("/api/catalog").then(setAll).catch(() => setAll([])); }, []);
  const hit = all.filter((x) => !q || x.code.includes(q.toUpperCase()) || (x.title || "").toLowerCase().includes(q.toLowerCase())).slice(0, 8);
  const cur = all.find((x) => x.code === value);
  return (
    <div>
      <div className="hrx-row">
        {value && cur?.has_photo ? (<img src={"/api/catalog/" + value + "/photo"} alt="" style={{ width: 52, height: 52, borderRadius: 12, objectFit: "cover" }} />) : null}
        <input className="hrx-inp" placeholder="Стандарт: DIN912, ISO7380..." value={q} onFocus={() => setOpen(true)} onChange={(e) => { setQ(e.target.value); setOpen(true); }} />
      </div>
      {cur && <div style={{ fontSize: 13, opacity: .6 }}>{cur.title}</div>}
      {open && hit.length > 0 && (<div>
        {hit.map((x) => (
          <button key={x.code} className="hrx-cell" onClick={() => { onPick(x.code, x.title); setQ(x.code); setOpen(false); }}>
            {x.has_photo ? (<img src={"/api/catalog/" + x.code + "/photo"} alt="" style={{ width: 44, height: 44, borderRadius: 10, objectFit: "cover" }} />) : (<span>?</span>)}
            <span className="tx"><b>{x.code}</b><small>{x.title}</small></span>
          </button>))}
      </div>)}
    </div>
  );
}
