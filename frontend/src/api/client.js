// Задел: fetch с initData в заголовке; сканер — @yudiel/react-qr-scanner (не ставим в MVP).
export async function api(path, initData = "", body) {
    const tg = window.Telegram?.WebApp;
    const res = await fetch(path, {
        method: body ? "POST" : "GET",
        headers: { "Content-Type": "application/json", "X-Telegram-Init-Data": initData || tg?.initData || "" },
        body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok)
        throw new Error(await res.text());
    return res.json();
}
// Точка расширения сканера: <ScanButton onScan={(payload) => ...} />
