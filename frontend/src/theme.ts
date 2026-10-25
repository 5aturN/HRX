// Стиль Apple/Telegram: светлое и тёмное из телеги, скругления, как в iOS.
export const T = {
  lime: "#dff83a",
  blue: "#007aff",
};

export function tgColors() {
  const tg = (window as any).Telegram?.WebApp;
  const p = tg?.themeParams || {};
  const dark = tg?.colorScheme === "dark";
  return {
    bg: p.bg_color || (dark ? "#0e0e11" : "#f2f2f7"),
    card: p.secondary_bg_color || (dark ? "#1c1c1e" : "#ffffff"),
    text: p.text_color || (dark ? "#ffffff" : "#000000"),
    muted: p.hint_color || (dark ? "#98989f" : "#8e8e93"),
    btn: p.button_color || "#007aff",
    btnText: p.button_text_color || "#ffffff",
  };
}

const cssArr = [
'*{box-sizing:border-box}',
'body{margin:0;font-family:-apple-system,system-ui,Segoe UI,Roboto,sans-serif;-webkit-font-smoothing:antialiased}',
'.hrx-shell{min-height:100vh;padding-bottom:110px}',
'.hrx-top{position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:10px;padding:10px 16px;backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:.5px solid rgba(128,128,128,.3)}',
'.hrx-top img{width:32px;height:32px;border-radius:8px;background:#fff;object-fit:contain}',
'.hrx-top b{font-size:15px}',
'.hrx-hero{display:flex;flex-direction:column;align-items:center;padding:28px 16px 12px;text-align:center}',
'.hrx-hero img{width:96px;height:96px;border-radius:24px;background:#fff;object-fit:contain;box-shadow:0 8px 32px rgba(0,0,0,.18)}',
'.hrx-hero h1{font-size:24px;margin:14px 0 4px}',
'.hrx-hero p{margin:0;font-size:14px;opacity:.6}',
'.hrx-me{display:flex;align-items:center;gap:12px;padding:14px;margin:14px 16px;border-radius:18px;box-shadow:0 2px 16px rgba(0,0,0,.08)}',
'.hrx-me img{width:56px;height:56px;border-radius:28px;object-fit:cover;background:#e5e5ea}',
'.hrx-me .init{width:56px;height:56px;border-radius:28px;display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:700;color:#fff;background:linear-gradient(135deg,#007aff,#5e2bff)}',
'.hrx-me b{font-size:17px}',
'.hrx-me small{display:block;font-size:13px;opacity:.6}',
'.hrx-sec{font-size:13px;text-transform:uppercase;letter-spacing:.5px;opacity:.5;margin:20px 16px 6px}',
'.hrx-list{margin:0 16px;border-radius:18px;overflow:hidden;box-shadow:0 2px 16px rgba(0,0,0,.06)}',
'.hrx-cell{display:flex;align-items:center;gap:12px;width:100%;padding:13px 16px;border:none;font-size:16px;text-align:left;cursor:pointer;border-bottom:.5px solid rgba(128,128,128,.25)}',
'.hrx-cell:last-child{border-bottom:none}',
'.hrx-cell:active{opacity:.6}',
'.hrx-cell .ic{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}',
'.hrx-cell .tx{flex:1}',
'.hrx-cell .tx small{display:block;font-size:13px;opacity:.55}',
'.hrx-cell .ch{font-size:20px;opacity:.3}',
'.hrx-thumb{width:52px;height:52px;border-radius:12px;object-fit:cover;background:#e5e5ea;flex-shrink:0}',
'.hrx-thumb.ph{background:linear-gradient(135deg,#e5e5ea,#d1d1d6);display:flex;align-items:center;justify-content:center;font-size:22px}',
'.hrx-inp{width:100%;font-size:17px;padding:12px 14px;margin:4px 0;border-radius:12px;border:none;outline:none}',
'.hrx-panel{margin:12px 16px;border-radius:18px;padding:14px;box-shadow:0 2px 16px rgba(0,0,0,.06)}',
'.hrx-btn{display:block;font-size:17px;font-weight:600;padding:14px;width:100%;border-radius:14px;border:none;cursor:pointer;margin-top:8px}',
'.hrx-btn:active{opacity:.7}',
'.hrx-btn.ghost{background:transparent;border:1px solid rgba(128,128,128,.4)}',
'.hrx-row{display:flex;gap:8px}',
'.hrx-table{width:100%;border-collapse:collapse;font-size:14px;margin-top:8px}',
'.hrx-table th{text-align:left;font-size:12px;text-transform:uppercase;opacity:.5;padding:6px 4px}',
'.hrx-table td{padding:9px 4px;border-top:.5px solid rgba(128,128,128,.25)}',
'.hrx-low{background:rgba(255,59,48,.08)}',
'.hrx-ok{color:#34c759}',
'.hrx-bad{color:#ff3b30}',
'.hrx-msg{padding:10px 14px;border-radius:12px;margin:8px 16px;font-size:14px;background:rgba(128,128,128,.12)}',
'.hrx-progress{height:6px;border-radius:3px;background:rgba(128,128,128,.2);overflow:hidden;margin-top:6px}',
'.hrx-progress i{display:block;height:100%;background:#34c759}',
'.hrx-tabs{position:fixed;bottom:0;left:0;right:0;z-index:10;display:flex;backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-top:.5px solid rgba(128,128,128,.3);padding:6px 4px calc(8px + env(safe-area-inset-bottom))}',
'.hrx-tabs button{flex:1;background:none;border:none;font-size:10px;display:flex;flex-direction:column;align-items:center;gap:3px;padding:6px 2px;cursor:pointer;opacity:.5}',
'.hrx-tabs button.on{opacity:1}',
'.hrx-tabs .e{font-size:24px}',
'.hrx-folder{margin:0 16px 8px;border-radius:14px;overflow:hidden}',
'.hrx-folder-h{display:flex;align-items:center;gap:8px;width:100%;padding:12px 14px;border:none;font-size:16px;font-weight:600;cursor:pointer}',
];
export const css: string = cssArr.join("\n");
