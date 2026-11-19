// La fonction du lien collé (issue n° 9, contrat docs/api.md) : GET /api/produit?lien=…
// Elle télécharge la page du produit avec ses garde-fous, la passe au moteur commun (site/moteur.js,
// le même que celui du favori) et rend la fiche en JSON. Elle ne stocke rien et n'utilise aucune clé.
import "../../site/moteur.js";

const UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15";
const DELAI_MS = 8000;
const TAILLE_MAX = 2 * 1024 * 1024;
const REDIRECTIONS_MAX = 3;
const DEMANDES_PAR_MINUTE = 30;

const MESSAGES = {
  "lien-invalide": "Ce lien ne fonctionne pas : il doit commencer par https://",
  "rien-trouve": "Je n'ai pas trouvé d'informations sur cette page. Remplis l'article à la main.",
  "trop-de-demandes": "Trop de demandes d'un coup. Réessaie dans une minute.",
  "site-refuse": "Ce site ne se laisse pas lire. Remplis l'article à la main.",
  "delai-depasse": "Ce site met trop de temps à répondre. Remplis l'article à la main."
};

function reponse(corps, code) {
  return new Response(JSON.stringify(corps), {
    status: code || 200,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "x-content-type-options": "nosniff" }
  });
}

function erreur(code, nom) {
  return reponse({ erreur: nom, message: MESSAGES[nom] || "" }, code);
}

// Le nombre de demandes par adresse, compté dans la mémoire de l'instance : une approximation, chaque
// instance de Cloudflare tenant son propre compte (un compteur partagé demanderait un stockage)
const demandes = new Map();
function tropDeDemandes(ip) {
  const maintenant = Date.now();
  const recentes = (demandes.get(ip) || []).filter((t) => maintenant - t < 60000);
  recentes.push(maintenant);
  demandes.set(ip, recentes);
  if (demandes.size > 5000) demandes.clear();
  return recentes.length > DEMANDES_PAR_MINUTE;
}

// Les adresses interdites : une fonction qui lit l'adresse qu'on lui donne ne doit viser ni le réseau
// interne ni une adresse écrite en chiffres (contrat, « Sécurité »)
function adresseAutorisee(texte) {
  let url;
  try { url = new URL(texte); } catch (e) { return null; }
  if (url.protocol !== "https:" && url.protocol !== "http:") return null;
  if (url.username || url.password) return null;
  const hote = url.hostname.toLowerCase();
  if (!hote || hote === "localhost" || hote.endsWith(".localhost") || hote.endsWith(".local") || hote.endsWith(".internal")) return null;
  if (/^[\d.]+$/.test(hote) || hote.includes(":") || hote.startsWith("[")) return null;
  if (!hote.includes(".")) return null;
  if (url.port && url.port !== "80" && url.port !== "443") return null;
  return url;
}

// Lit au plus 2 Mo de la page, et s'arrête là
async function lireCorps(r) {
  const lecteur = r.body.getReader();
  const morceaux = [];
  let taille = 0;
  while (taille < TAILLE_MAX) {
    const { done, value } = await lecteur.read();
    if (done) break;
    morceaux.push(value);
    taille += value.byteLength;
  }
  try { await lecteur.cancel(); } catch (e) { /* déjà fermé */ }
  const tout = new Uint8Array(Math.min(taille, TAILLE_MAX));
  let position = 0;
  for (const m of morceaux) {
    const reste = tout.length - position;
    if (reste <= 0) break;
    tout.set(m.subarray(0, reste), position);
    position += Math.min(m.byteLength, reste);
  }
  return new TextDecoder("utf-8").decode(tout);
}

export async function onRequestGet({ request }) {
  const ip = request.headers.get("cf-connecting-ip") || "inconnue";
  if (tropDeDemandes(ip)) return erreur(429, "trop-de-demandes");

  const lien = new URL(request.url).searchParams.get("lien") || "";
  if (!lien || lien.length > 2048) return erreur(400, "lien-invalide");
  let cible = adresseAutorisee(lien.trim());
  if (!cible) return erreur(400, "lien-invalide");

  const controle = new AbortController();
  const minuterie = setTimeout(() => controle.abort(), DELAI_MS);
  let code = 0;
  try {
    let r;
    for (let saut = 0; ; saut++) {
      r = await fetch(cible.toString(), {
        redirect: "manual",
        signal: controle.signal,
        headers: { "user-agent": UA, accept: "text/html,application/xhtml+xml", "accept-language": "fr-FR,fr;q=0.9,en;q=0.5" }
      });
      if (r.status < 300 || r.status >= 400) break;
      const suite = r.headers.get("location");
      if (!suite || saut >= REDIRECTIONS_MAX) { code = 502; return erreur(502, "site-refuse"); }
      cible = adresseAutorisee(new URL(suite, cible).toString());
      if (!cible) { code = 502; return erreur(502, "site-refuse"); }
    }
    code = r.status;
    if (r.status === 429 || r.status >= 400) return erreur(502, "site-refuse");
    const type = r.headers.get("content-type") || "";
    if (!/text\/html|application\/xhtml/i.test(type)) return erreur(422, "rien-trouve");
    const html = await lireCorps(r);
    const fiche = globalThis.TinyMoteur.lireProduit(html, lien.trim());
    if (!fiche) {
      // Une page minuscule sans produit est presque toujours un écran anti-robot
      return html.length < 6000 ? erreur(502, "site-refuse") : erreur(422, "rien-trouve");
    }
    return reponse(fiche);
  } catch (e) {
    if (e && e.name === "AbortError") { code = 504; return erreur(504, "delai-depasse"); }
    code = 502;
    return erreur(502, "site-refuse");
  } finally {
    clearTimeout(minuterie);
    // Le nom du site et le code de réponse, jamais l'adresse complète ni celle du visiteur
    console.log(JSON.stringify({ site: cible ? cible.hostname : "", code }));
  }
}

export async function onRequest({ request }) {
  if (request.method === "GET" || request.method === "HEAD") return erreur(400, "lien-invalide");
  return reponse({ erreur: "methode-non-permise" }, 405);
}
