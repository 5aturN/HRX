// Один fetch на всех: initData в заголовке, понятные русские ошибки, повтор при обрыве.
function initHeader(): string {
  try {
    return (window as any).Telegram?.WebApp?.initData || "";
  } catch {
    return "";
  }
}

function isOffline(e: any): boolean {
  const m = String(e?.message || e || "");
  return (
    m.includes("Failed to fetch") ||
    m.includes("NetworkError") ||
    m.includes("Load failed") ||
    m.includes("Network request failed") ||
    e instanceof TypeError
  );
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export async function api(path: string, initData = "", body?: unknown, retry = 1): Promise<any> {
  const headers: Record<string, string> = {
    "X-Telegram-Init-Data": initData || initHeader(),
  };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  try {
    const res = await fetch(path, {
      method: body !== undefined ? "POST" : "GET",
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    if (res.status === 401) throw new Error("Откройте через Telegram");
    if (res.status === 403) throw new Error("Нет прав — попросите админа");
    if (res.status === 429) throw new Error("Много запросов, подождите минуту");
    if (!res.ok) {
      let t = "";
      try {
        t = await res.text();
      } catch {
        /* пусто */
      }
      throw new Error(t.slice(0, 200) || "Ошибка " + res.status);
    }
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("application/json")) return res.json();
    return res.text();
  } catch (e: any) {
    if (retry > 0 && isOffline(e)) {
      await sleep(800);
      return api(path, initData, body, retry - 1);
    }
    throw e instanceof Error ? e : new Error("Нет связи, проверьте интернет");
  }
}

// Скачивание Excel через blob: токен только в заголовке, не в URL.
export async function downloadExcel(path: string, filename = "otchet.xlsx"): Promise<void> {
  const res = await fetch(path, { headers: { "X-Telegram-Init-Data": initHeader() } });
  if (res.status === 401) throw new Error("Откройте через Telegram");
  if (res.status === 403) throw new Error("Нет прав — попросите админа");
  if (res.status === 429) throw new Error("Много запросов, подождите минуту");
  if (!res.ok) throw new Error("Не удалось скачать файл");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  try {
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
  } finally {
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }
}
