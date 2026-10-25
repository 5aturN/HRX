// Звездочка избранного: своё у каждого.
import { useState } from "react";
import { api } from "../api/client";

export default function FavStar({ itemId, init }: { itemId: number; init?: boolean }) {
  const [fav, setFav] = useState(!!init);
  const go = async (e: any) => { e.stopPropagation(); const r = await api("/api/favorites/" + itemId, "", {}); setFav(r.fav); };
  return (<span onClick={go} style={{ fontSize: 22, cursor: "pointer", opacity: fav ? 1 : .3 }}>{fav ? "★" : "☆"}</span>);
}
