// Дизайн под Гидробот: темный фон, лаймовый акцент, фиолет вторым.
// Логотип лежит в /logo.png (public). Цвета подтягиваются из Telegram themeParams.
export const T = {
  lime: "#dff83a",
  violet: "#5e2bff",
  bg: "#101014",
  card: "#1a1a20",
  line: "#2a2a33",
  text: "#ffffff",
  muted: "#9a9aa5",
  danger: "#ff5a5a",
  ok: "#7dff9a",
  radius: 14,
};

export function tgColors() {
  const tg = (window as any).Telegram?.WebApp;
  return {
    bg: tg?.themeParams?.bg_color || T.bg,
    text: tg?.themeParams?.text_color || T.text,
  };
}
export const css = [
'*{box-sizing:border-box}',
'body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif}',
'.hrx-shell{min-height:100vh;padding-bottom:96px}',
'.hrx-top{position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:12px;padding:12px 16px;background:rgba(16,16,20,.92);border-bottom:1px solid #2a2a33}',
'.hrx-top img{width:40px;height:40px;border-radius:10px;background:#fff;object-fit:contain}',
'.hrx-top b{font-size:17px}',
'.hrx-top small{display:block;color:#9a9aa5;font-size:12px;font-weight:400}',
'.hrx-wrap{max-width:640px;margin:0 auto;padding:16px}',
'.hrx-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}',
'.hrx-card{background:#1a1a20;border:1px solid #2a2a33;border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:6px;align-items:flex-start;text-align:left;color:#fff;cursor:pointer;min-height:120px}',
'.hrx-card:active{transform:scale(.98)}',
'.hrx-card .emo{font-size:28px}',
'.hrx-card b{font-size:16px}',
'.hrx-card small{color:#9a9aa5;font-size:13px}',
'.hrx-card.lime{background:#dff83a;border-color:#dff83a;color:#111}',
'.hrx-card.lime small{color:#333}',
'.hrx-panel{background:#1a1a20;border:1px solid #2a2a33;border-radius:14px;padding:14px;margin:12px 0}',
'.hrx-inp{width:100%;font-size:17px;padding:13px 14px;margin:5px 0;border-radius:12px;border:1px solid #2a2a33;background:#0c0c10;color:#fff}',
'.hrx-btn{font-size:18px;font-weight:700;padding:15px;width:100%;border-radius:14px;border:none;background:#dff83a;color:#111;cursor:pointer;margin-top:8px}',
'.hrx-btn:active{transform:scale(.98)}',
'.hrx-btn.ghost{background:transparent;border:1px solid #2a2a33;color:#fff}',
'.hrx-btn.violet{background:#5e2bff;color:#fff}',
'.hrx-row{display:flex;gap:8px}',
'.hrx-table{width:100%;border-collapse:collapse;font-size:14px;margin-top:10px}',
'.hrx-table th{text-align:left;color:#9a9aa5;font-weight:600;padding:8px;border-bottom:1px solid #2a2a33}',
'.hrx-table td{padding:10px 8px;border-bottom:1px solid #2a2a33}',
'.hrx-low{background:rgba(255,90,90,.12)}',
'.hrx-ok{color:#7dff9a}',
'.hrx-bad{color:#ff5a5a}',
'.hrx-tabs{position:fixed;bottom:0;left:0;right:0;z-index:10;display:flex;background:rgba(16,16,20,.96);border-top:1px solid #2a2a33;padding:6px 4px}',
'.hrx-tabs button{flex:1;background:none;border:none;color:#9a9aa5;font-size:11px;display:flex;flex-direction:column;align-items:center;gap:2px;padding:8px 2px;cursor:pointer}',
'.hrx-tabs button.on{color:#dff83a}',
'.hrx-tabs .e{font-size:22px}',
'.hrx-msg{padding:10px 12px;border-radius:10px;background:#0c0c10;border:1px solid #2a2a33;margin:8px 0;font-size:14px}',
'.hrx-progress{height:8px;border-radius:4px;background:#0c0c10;overflow:hidden}',
'.hrx-progress i{display:block;height:100%;background:#dff83a}',
].join('\n');
