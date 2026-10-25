// Главная: привет, баланс-карточка, срочные пороги, лента, разделы.
import { useEffect, useState } from "react";
import { api } from "../api/client";
import { tgColors } from "../theme";

function Sec({ title, more, onMore }: { title: string; more?: string; onMore?: () => void }) {
  return (
    <div className="hrx-sec">
      <span>{title}</span>
      {more && <a onClick={onMore}>{more}</a>}
    </div>
  );
}

function Glyph({ bg, ch }: { bg: string; ch: string }) {
  return (
    <span className="ic" style={{ background: bg }}>
      {ch}
    </span>
  );
}

export default function HomePage({ go }: { go: (t: any) => void }) {
  const [me, setMe] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [recent, setRecent] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const [m, s, r] = await Promise.all([
          api("/api/me").catch(() => null),
          api("/api/stats").catch(() => null),
          api("/api/recent").catch(() => []),
        ]);
        if (!alive) return;
        setMe(m);
        setStats(s);
        setRecent(Array.isArray(r) ? r : []);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, []);
  const c = tgColors();
  const nm = me ? me.first_name || me.username || "Гость" : "...";
  const role = me?.position || (me?.roles || []).join(", ") || "кабинет";
  const low = Array.isArray(stats?.low) ? stats.low : [];
  if (loading) {
    return (
      <div>
        <div className="hrx-skel sk-card" />
        <div className="hrx-skel sk-line" />
        <div className="hrx-skel sk-row" />
        <div className="hrx-skel sk-row" />
      </div>
    );
  }
  return (
    <div>
      <div className="hrx-bal">
        <small>Привет, {nm} · всего на складе</small>
        <div className="n">{stats ? stats.total_qty + " шт" : "—"}</div>
        <small>
          позиций: {stats?.total_items ?? "—"} · ниже порога: {stats?.low_count ?? "—"}
        </small>
        <div className="row">
          <button className="qbtn" onClick={() => go("receipt")}>
            <b>+</b>Принять
          </button>
          <button className="qbtn" onClick={() => go("assemble")}>
            <b>⚙</b>Собрать
          </button>
          <button className="qbtn" onClick={() => go("warehouse")}>
            <b>⌕</b>Найти
          </button>
        </div>
      </div>
      <div className="hrx-me" style={{ background: c.card, color: c.text }} onClick={() => go("profile")}>
        {me && me.has_avatar ? (
          <img src={"/api/users/" + me.id + "/avatar"} alt="" />
        ) : (
          <div className="init">{(nm[0] || "?").toUpperCase()}</div>
        )}
        <div>
          <b>{nm}</b>
          <small>{role}</small>
        </div>
        <span style={{ marginLeft: "auto", opacity: 0.3, fontSize: 20 }}>›</span>
      </div>
      {low.length > 0 && (
        <div>
          <Sec title="Срочно заказать" more="Все" onMore={() => go("warehouse")} />
          <div className="hrx-list" style={{ background: c.card, color: c.text }}>
            {low.slice(0, 4).map((x: any) => (
              <div key={x.sku} className="hrx-cell hrx-urgent" onClick={() => go("warehouse")}>
                <span className="tx">
                  {x.name}
                  <small>
                    {x.sku} · осталось {x.qty} шт
                  </small>
                </span>
                <span className="hrx-badge">{x.qty}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {recent.length > 0 && (
        <div>
          <Sec title="Последние движения" more="Все" onMore={() => go("reports")} />
          <div className="hrx-list" style={{ background: c.card, color: c.text }}>
            {recent.slice(0, 4).map((x: any, i: number) => (
              <div key={i} className="hrx-cell">
                <span className="hrx-dot" style={{ background: x.qty < 0 ? "#ff453a" : "#30d158" }} />
                <span className="tx">
                  {x.name}
                  <small>
                    {x.mtype_ru} · {x.qty} шт
                  </small>
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
      <div className="hrx-sec">Склад</div>
      <div className="hrx-list" style={{ background: c.card, color: c.text }}>
        <button className="hrx-cell" style={{ borderBottom: ".5px solid rgba(128,128,128,.2)" }} onClick={() => go("warehouse")}>
          <Glyph bg="#007aff" ch="▦" />
          <span className="tx">
            Склад<small>Папки, поиск, фото</small>
          </span>
          <span className="ch">›</span>
        </button>
        <button className="hrx-cell" style={{ borderBottom: ".5px solid rgba(128,128,128,.2)" }} onClick={() => go("favs")}>
          <Glyph bg="#ff9500" ch="★" />
          <span className="tx">
            Избранное<small>Моё быстрое</small>
          </span>
          <span className="ch">›</span>
        </button>
        <button className="hrx-cell" style={{ borderBottom: ".5px solid rgba(128,128,128,.2)" }} onClick={() => go("orders")}>
          <Glyph bg="#af52de" ch="☰" />
          <span className="tx">
            Заказы<small>Прогресс сборки</small>
          </span>
          <span className="ch">›</span>
        </button>
        <button className="hrx-cell" onClick={() => go("catalog")}>
          <Glyph bg="#34c759" ch="⛭" />
          <span className="tx">
            Стандарты<small>Крепёж и химия</small>
          </span>
          <span className="ch">›</span>
        </button>
      </div>
      <div className="hrx-sec">Ещё</div>
      <div className="hrx-list" style={{ background: c.card, color: c.text }}>
        <button className="hrx-cell" style={{ borderBottom: ".5px solid rgba(128,128,128,.2)" }} onClick={() => go("moves")}>
          <Glyph bg="#ff3b30" ch="↩" />
          <span className="tx">
            Брак и возврат<small>Списание и выдача</small>
          </span>
          <span className="ch">›</span>
        </button>
        <button className="hrx-cell" style={{ borderBottom: ".5px solid rgba(128,128,128,.2)" }} onClick={() => go("reports")}>
          <Glyph bg="#5ac8fa" ch="▤" />
          <span className="tx">
            Отчёты<small>Excel и движения</small>
          </span>
          <span className="ch">›</span>
        </button>
        <button className="hrx-cell" onClick={() => go("profile")}>
          <Glyph bg="#8e8e93" ch="◉" />
          <span className="tx">
            Кабинет<small>Профиль и доступы</small>
          </span>
          <span className="ch">›</span>
        </button>
      </div>
    </div>
  );
}
