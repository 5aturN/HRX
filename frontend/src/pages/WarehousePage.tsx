// Склад: дерево папок + живой поиск с debounce, карточки с фото, избранное.
import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";
import FavStar from "../components/FavStar";

function Thumb({ id, name }: { id: number; name: string }) {
  const [err, setErr] = useState(false);
  if (err) return <div className="hrx-thumb ph">?</div>;
  return (
    <img
      className="hrx-thumb"
      src={"/api/items/" + id + "/photo"}
      alt={name}
      loading="lazy"
      onError={() => setErr(true)}
    />
  );
}

function Node({ n, depth }: { n: any; depth: number }) {
  const [open, setOpen] = useState(depth < 1);
  const c = tgColors();
  return (
    <div className="hrx-folder" style={{ background: c.card, color: c.text }}>
      <button
        className="hrx-folder-h"
        style={{ background: "transparent", color: c.text }}
        onClick={() => setOpen(!open)}
        aria-expanded={open}
      >
        <span className={"hrx-chev" + (open ? " open" : "")}>›</span>
        <span style={{ flex: 1, textAlign: "left" }}>{n.name}</span>
        <small style={{ opacity: 0.5 }}>
          {n.n_items} поз · {n.qty} шт
        </small>
      </button>
      {open && (
        <div>
          {(n.items || []).map((i: any) => (
            <div key={i.id} className="hrx-cell">
              {i.has_photo ? <Thumb id={i.id} name={i.name} /> : <div className="hrx-thumb ph">?</div>}
              <span className="tx">
                {i.name}
                <small>
                  {i.sku} · осталось {i.qty} шт
                </small>
              </span>
              <FavStar itemId={i.id} init={!!i.is_fav} />
            </div>
          ))}
          {(n.children || []).map((k: any) => (
            <Node key={k.id} n={k} depth={depth + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function WarehousePage() {
  const [tree, setTree] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [found, setFound] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);
  const timer = useRef<number | undefined>(undefined);
  useEffect(() => {
    let alive = true;
    api("/api/folders/tree")
      .then((t) => {
        if (alive) setTree(Array.isArray(t) ? t : []);
      })
      .catch(() => {
        if (alive) setTree([]);
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, []);
  // Живой поиск с debounce 300 мс, запрос /api/stock не менялся.
  useEffect(() => {
    window.clearTimeout(timer.current);
    const query = q.trim();
    if (query.length < 2) {
      setFound([]);
      setSearching(false);
      return;
    }
    setSearching(true);
    timer.current = window.setTimeout(async () => {
      try {
        const r = await api("/api/stock?q=" + encodeURIComponent(query));
        setFound(Array.isArray(r) ? r : []);
      } catch {
        setFound([]);
      } finally {
        setSearching(false);
      }
    }, 300);
    return () => window.clearTimeout(timer.current);
  }, [q]);
  const c = tgColors();
  const roots = tree[0]?.children || tree;
  return (
    <div>
      <h2 style={{ margin: "8px 16px" }}>Склад</h2>
      <div style={{ margin: "0 16px" }}>
        <input
          className="hrx-inp"
          style={{ background: c.card, color: c.text }}
          placeholder="Найти по названию или артикулу…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          enterKeyHint="search"
        />
      </div>
      {q.trim().length >= 2 && (
        <div>
          <div className="hrx-sec">
            <span>{searching ? "Ищем…" : "Найдено · " + found.length}</span>
          </div>
          <div className="hrx-list" style={{ background: c.card, color: c.text }}>
            {found.slice(0, 20).map((i: any) => (
              <div key={i.id} className="hrx-cell">
                {i.has_photo ? <Thumb id={i.id} name={i.name} /> : <div className="hrx-thumb ph">?</div>}
                <span className="tx">
                  {i.name}
                  <small>
                    {i.sku} · {i.folder} · осталось {i.qty}
                  </small>
                </span>
                <FavStar itemId={i.id} init={!!i.is_fav} />
              </div>
            ))}
            {!searching && found.length === 0 && <div className="hrx-empty">Ничего не нашли</div>}
          </div>
        </div>
      )}
      <div className="hrx-sec">Папки</div>
      {loading && (
        <div>
          <div className="hrx-skel sk-row" />
          <div className="hrx-skel sk-row" />
          <div className="hrx-skel sk-row" />
        </div>
      )}
      {!loading && roots.length === 0 && <div className="hrx-msg">Папок пока нет</div>}
      {!loading && roots.map((n: any) => <Node key={n.id} n={n} depth={0} />)}
    </div>
  );
}
