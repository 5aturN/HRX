// Один fetch на всех: initData, понятные ошибки, повтор при обрыве.
export async function api(path: string, initData = "", body?: unknown, retry = 1): Promise<any> {
  const tg = (window as any).Telegram?.WebApp;
  const headers: any = { "X-Telegram-Init-Data": initData || tg?.initData || "" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  try {
    const res = await fetch(path, { method: body !== undefined ? "POST" : "GET", headers, body: body !== undefined ? JSON.stringify(body) : undefined });
    if (res.status === 401) throw new Error("Откройте через Telegram");
    if (res.status === 403) throw new Error("Нет прав — попросите админа");
    if (res.status === 429) throw new Error("Много запросов, подождите минуту");
    if (!res.ok) { let t = ""; try { t = await res.text(); } catch {} throw new Error(t.slice(0, 200) || ("Ошибка " + res.status)); }
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("application/json")) return res.json();
    return res.text();
  } catch (e: any) {
    if (retry > 0 && (e.message || "").includes("Failed to fetch")) { await new Promise((r) => setTimeout(r, 800)); return api(path, initData, body, retry - 1); }
    throw e;
  }
}
