// Люди: заявки с аватарами, роли, блок. Только админ.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";
import { toast } from "../App";

const ROLES = ["worker", "purchaser", "admin"];
export default function AdminPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [busy, setBusy] = useState(false);
  const c = tgColors();
  const load = async () => { try { setUsers(await api("/api/users")); } catch (e: any) { setUsers([]); } };
  useEffect(() => { load(); }, []);
  const act = async (u: any, role: string) => { setBusy(true); try { await api("/api/users/" + u.id + "/activate", "", { roles: [role] }); toast(u.first_name + " активирован"); load(); } catch (e: any) { toast(e.message, false); } setBusy(false); };
  const block = async (u: any) => { setBusy(true); try { await api("/api/users/" + u.id + "/block", "", {}); toast("Заблокирован"); load(); } catch (e: any) { toast(e.message, false); } setBusy(false); };
  const pend = users.filter((x) => x.status === "pending");
  const act2 = users.filter((x) => x.status === "active");
  const card = (u: any) => (
    <div key={u.id} className="hrx-panel" style={{ background: c.card, color: c.text }}>
      <div className="hrx-cell"><b>{u.first_name} {u.last_name || ""}</b><small> · @{u.username || "?"} · {u.position || "без должности"}</small></div>
      <div style={{ fontSize: 13, opacity: .6 }}>Роли: {(u.roles || []).join(", ") || "нет"} · {u.status}</div>
      {u.status === "pending" && (<div><div className="hrx-sec">Выдать доступ как</div><div className="hrx-row">
        {ROLES.map((r) => (<button key={r} className="hrx-btn ghost" disabled={busy} onClick={() => act(u, r)}>{r}</button>))}
      </div></div>)}
      {u.status === "active" && <button className="hrx-btn ghost" disabled={busy} onClick={() => block(u)}>Заблокировать</button>}
    </div>);
  return (
    <div>
      <h2 style={{ margin: "8px 16px" }}>Люди</h2>
      {pend.length > 0 && (<div><div className="hrx-sec">Ждут ({pend.length})</div>{pend.map(card)}</div>)}
      <div className="hrx-sec">Активные ({act2.length})</div>
      {act2.map(card)}
      {users.length === 0 && <div className="hrx-msg">Нет доступа (нужен admin) или пока никого</div>}
    </div>
  );
}
