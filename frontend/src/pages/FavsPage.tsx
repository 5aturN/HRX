// Мое избранное: частые позиции сверху, у каждого свои.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";
import FavStar from "../components/FavStar";

export default function FavsPage() {
  const [rows, setRows] = useState<any[]>([]);
  const load = async () => { try { setRows(await api("/api/favorites")); } catch {} };
  useEffect(() => { load(); }, []);
  const c = tgColors();
  return (
    <div><h2 style={{ margin: "8px 16px" }}>Избранное</h2>
    <div className="hrx-list" style={{ background: c.card, color: c.text }}>
      {rows.map((x) => (<div key={x.id} className="hrx-cell">
        {x.has_photo ? (<img src={"/api/items/" + x.id + "/photo"} alt="" style={{ width: 52, height: 52, borderRadius: 12, objectFit: "cover" }} />) : (<div className="hrx-thumb ph">?</div>)}
        <span className="tx">{x.name}<small>{x.sku} · ост. {x.qty}</small></span><FavStar itemId={x.id} init />
      </div>))}
      {rows.length === 0 && <div className="hrx-cell">Пусто — нажмите звезду на позиции</div>}
    </div></div>
  );
}
