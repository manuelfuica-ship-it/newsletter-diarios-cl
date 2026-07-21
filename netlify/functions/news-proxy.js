/* ============================================================================
   Newsletter Diarios — Proxy de feeds de noticias (RSS / Atom)
   ----------------------------------------------------------------------------
   Los feeds RSS de medios chilenos no envían cabeceras CORS correctas.
   Esta función los trae del lado servidor y devuelve al frontend.

   Uso: /.netlify/functions/news-proxy?url=<URL_ENCODED_feed>
   ============================================================================ */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Cache-Control": "public, max-age=600"
};
const UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36";

function hostBloqueado(hostname) {
  const h = (hostname || "").toLowerCase();
  if (h === "localhost" || h.endsWith(".local") || h.endsWith(".internal")) return true;
  if (/^(127\.|10\.|0\.0\.0\.0|169\.254\.|::1|fc00:|fe80:)/.test(h)) return true;
  if (/^192\.168\./.test(h)) return true;
  const m = h.match(/^172\.(\d{1,3})\./);
  if (m && +m[1] >= 16 && +m[1] <= 31) return true;
  return false;
}

exports.handler = async (event) => {
  if (event.httpMethod === "OPTIONS") return { statusCode: 204, headers: CORS, body: "" };

  const url = event.queryStringParameters && event.queryStringParameters.url;
  if (!url) return { statusCode: 400, headers: CORS, body: "Falta el parámetro 'url'." };

  let u;
  try { u = new URL(url); } catch { return { statusCode: 400, headers: CORS, body: "URL malformada." }; }
  if (u.protocol !== "https:" && u.protocol !== "http:")
    return { statusCode: 400, headers: CORS, body: "Solo se permiten URLs http(s)." };
  if (hostBloqueado(u.hostname))
    return { statusCode: 403, headers: CORS, body: "Host no permitido." };

  try {
    const ctrl = new AbortController();
    const tid = setTimeout(() => ctrl.abort(), 15000);
    const r = await fetch(u.toString(), {
      headers: { "User-Agent": UA, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*" },
      redirect: "follow",
      signal: ctrl.signal
    });
    clearTimeout(tid);
    const text = await r.text();
    if (!r.ok) return { statusCode: 502, headers: CORS, body: "El origen respondió " + r.status + "." };
    if (text.length > 6 * 1024 * 1024)
      return { statusCode: 413, headers: CORS, body: "El feed es demasiado grande." };
    const ct = r.headers.get("content-type") || "application/xml; charset=utf-8";
    return {
      statusCode: 200,
      headers: { ...CORS, "Content-Type": ct.includes("xml") || ct.includes("rss") ? ct : "application/xml; charset=utf-8" },
      body: text
    };
  } catch (e) {
    const msg = e && e.name === "AbortError" ? "Tiempo de espera agotado." : (e.message || "Error de red.");
    return { statusCode: 502, headers: CORS, body: "No se pudo obtener el feed: " + msg };
  }
};
