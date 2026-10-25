// Админка: пользователи (активация, роли, блок) + пороги через остатки.
import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function AdminPage() {
  const [users, setUsers] = useState<any[]>([]);
  const load = async () => { try { setUsers(await api("/api/users")); } catch { setUsers([]); } };
  useEffect(() => { load(); }, []);
  const act = async (u: any) => {
    await api("/api/users/" + u.id + "/activate", "", { first_name: u.first_name, last_name: u.last_name || "", position: u.position || "", roles: ["worker"] });
    load();
  };
  return (
    <div>
      <h2>Люди</h2>
      {users.map((u: any) => (
        <div key={u.id} style={{ border: "1px solid #555", borderRadius: 8, padding: 8, margin: "8px 0" }}>
          <b>{u.first_name} {u.last_name || ""}</b> (@{u.username || "?"}) — {u.status}, роли: {(u.roles || []).join(", ")}
          {u.status === "pending" && <button style={{ fontSize: 18, padding: 12, width: "100%", marginTop: 4 }} onClick={() => act(u)}>Активировать как worker</button>}
        </div>
      ))}
      {users.length === 0 && <p>Нет доступа (нужен admin)</p>}
    </div>
  );
}
