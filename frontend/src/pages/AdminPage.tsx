// Люди: заявки, активация, роли.
import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function AdminPage() {
  const [users, setUsers] = useState<any[]>([]);
  const load = async () => { try { setUsers(await api("/api/users")); } catch { setUsers([]); } };
  useEffect(() => { load(); }, []);
  const act = async (u: any) => { await api("/api/users/" + u.id + "/activate", "", { roles: ["worker"] }); load(); };
  const block = async (u: any) => { await api("/api/users/" + u.id + "/block", "", {}); load(); };
  return (
    <div>
      <h2>Люди</h2>
      {users.map((u: any) => (<div key={u.id} className="hrx-panel"><b>{u.first_name} {u.last_name || ""}</b> <small>(@{u.username || "?"}) — {u.status}, роли: {(u.roles || []).join(", ")}</small>
        {u.status === "pending" && <button className="hrx-btn" onClick={() => act(u)}>Активировать</button>}
        {u.status === "active" && <button className="hrx-btn ghost" onClick={() => block(u)}>Заблокировать</button>}
      </div>))}
      {users.length === 0 && <div className="hrx-msg">Нет доступа (нужен admin)</div>}
    </div>
  );
}
