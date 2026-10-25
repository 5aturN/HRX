// Склад: дерево папок + поиск, карточки с фотками.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";

function Node({ n, depth }: { n: any; depth: number }) {
  const [open, setOpen] = useState(depth < 1);
  const c = tgColors();
  return (
    <div className="hrx-folder" style={{ background: c.card, color: c.text }}>
      <button className="hrx-folder-h" style={{ background: "transparent", color: c.text }} onClick={() => setOpen(!open)}>
        <span>{open ? "v" : ">"}</span><span style={{ flex: 1, textAlign: "left" }}>{n.name}</span>
        <small style={{ opacity: .5 }}>{n.n_items} поз · {n.qty} шт</small>
      </button>
      {open && (<div>
        {(n.items || []).map((i: any) => (<div key={i.id} className="hrx-cell">
          {i.has_photo ? (<img className="hrx-thumb" src={"/api/items/" + i.id + "/photo"} alt="" />) : (<div className="hrx-thumb ph">?</div>)}
          <span className="tx">{i.name}<small>{i.sku} · ост. {i.qty}</small></span>
        </div>))}
        {(n.children || []).map((k: any) => (<Node key={k.id} n={k} depth={depth + 1} />))}
      </div>)}
    </div>
  );
}

export default function WarehousePage() {
  const [tree, setTree] = useState<any[]>([]);
  const [q, setQ] = useState("");
  const [found, setFound] = useState<any[]>([]);
  useEffect(() => { api("/api/folders/tree").then(setTree).catch(() => setTree([])); }, []);
  const find = async () => setFound(await api("/api/stock?q=" + encodeURIComponent(q)));
  const c = tgColors();
  return (
    <div>
      <h2 style={{ margin: "8px 16px" }}>Склад</h2>
      <div style={{ margin: "0 16px" }}><div className="hrx-row"><input className="hrx-inp" style={{ background: c.card, color: c.text }} placeholder="Найти..." value={q} onChange={(e) => setQ(e.target.value)} /><button className="hrx-btn" style={{ width: 110 }} onClick={find}>Найти</button></div></div>
      {q && found.length > 0 && (<div className="hrx-list" style={{ background: c.card, color: c.text }}>{found.slice(0, 20).map((i: any) => (<div key={i.id} className="hrx-cell">
        {i.has_photo ? (<img className="hrx-thumb" src={"/api/items/" + i.id + "/photo"} alt="" />) : (<div className="hrx-thumb ph">?</div>)}
        <span className="tx">{i.name}<small>{i.sku} · {i.folder} · ост. {i.qty}</small></span></div>))}</div>)}
      <div className="hrx-sec">Папки</div>
      {(tree[0]?.children || tree).map((n: any) => (<Node key={n.id} n={n} depth={0} />))}
    </div>
  );
}
