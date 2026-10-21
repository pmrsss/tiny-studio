// Les visuels des articles : la photo du produit (champ « image »), par son adresse ; à défaut,
// une vignette neutre, l'icône du meuble.
const dessins = {};  // les dessins des premiers articles, remplacés par les packshots le 19 octobre 2026, sont dans l'historique Git

// Les cinq meubles, vides au départ : en ligne, le studio s'ouvre vide (décision de Pauline,
// 19 octobre 2026). Chaque meuble donne sa teinte à son panneau.

const meubles = {
  dressing: {
    nom: "Le dressing",
    teinte: "#F3C3CC",
    vide: "Ton prochain coup de cœur mode ira ici.",
    articles: []
  },
  bibliotheque: {
    nom: "La bibliothèque",
    teinte: "#D9A877",
    vide: "Le prochain livre qui te fait envie ira ici.",
    articles: []
  },
  deco: {
    nom: "La commode déco",
    teinte: "#A9B9F0",
    vide: "Ta prochaine trouvaille déco ira ici.",
    articles: []
  },
  coffre: {
    nom: "Le coffre fourre-tout",
    teinte: "#C98A52",
    vide: "Tout ce qui ne va dans aucun meuble ira ici.",
    articles: []
  },
  coiffeuse: {
    nom: "La coiffeuse",
    teinte: "#EED3AE",
    vide: "Ton prochain soin ou ton prochain rouge à lèvres ira ici.",
    articles: []
  }
};


// Les articles enregistrés dans le navigateur (issue n° 3, 19 octobre 2026) : à la première visite,
// les articles de départ ci-dessus ; ensuite, ce que l'on a rangé, retiré ou déplacé. Les photos
// restent enregistrées par leur adresse, comme prévu dans le choix technique du 15 octobre 2026.
const CLE_ARTICLES = "tiny-studio-articles";
let stockageOk = true;

function lireArticles() {
  try {
    localStorage.setItem("tiny-studio-essai", "1");
    localStorage.removeItem("tiny-studio-essai");
    const enregistres = JSON.parse(localStorage.getItem(CLE_ARTICLES));
    if (!enregistres) return;
    Object.keys(meubles).forEach(function (cle) {
      if (Array.isArray(enregistres[cle])) meubles[cle].articles = enregistres[cle];
    });
  } catch (e) {
    stockageOk = false;
  }
}

function enregistrerArticles() {
  const contenu = {};
  Object.keys(meubles).forEach(function (cle) { contenu[cle] = meubles[cle].articles; });
  try {
    localStorage.setItem(CLE_ARTICLES, JSON.stringify(contenu));
    stockageOk = true;
  } catch (e) {
    stockageOk = false;
  }
  signalerStockage();
}

// Si le navigateur refuse d'enregistrer (navigation privée, stockage plein), un message discret le
// dit sous l'accroche ; l'app reste utilisable le temps de la visite
function signalerStockage() {
  document.getElementById("alerte-stockage").hidden = stockageOk;
}

// Le meuble qui contient un article : les articles de départ ne portent pas le champ « meuble »
function meubleDe(article) {
  return Object.keys(meubles).find(function (cle) { return meubles[cle].articles.indexOf(article) !== -1; });
}

lireArticles();
signalerStockage();

// Le tag « Acheté » : il se coche et se décoche sur chaque fiche, et le navigateur s'en souvient
const CLE_ACHATS = "tiny-studio-achats";

function lireAchats() {
  try { return JSON.parse(localStorage.getItem(CLE_ACHATS)) || {}; } catch (e) { return {}; }
}

function enregistrerAchats(achats) {
  try { localStorage.setItem(CLE_ACHATS, JSON.stringify(achats)); } catch (e) { stockageOk = false; }
  signalerStockage();
}

let achats = lireAchats();

function estAchete(article) {
  return article.id in achats ? achats[article.id] : Boolean(article.achete);
}

function libelleNombre(n) {
  if (n === 0) return "Aucun article";
  return n === 1 ? "1 article" : n + " articles";
}

// Les pastilles de nombre, sur les meubles et sur les boutons
function afficherCompteurs() {
  // Le studio vide (issue n° 4) : l'accueil dit quoi faire et désigne le bouton « + », seul appel à
  // l'action ; les pastilles des meubles restent à « 0 » (20 octobre 2026)
  const studioVide = Object.keys(meubles).every(function (cle) { return meubles[cle].articles.length === 0; });
  document.documentElement.classList.toggle("studio-vide", studioVide);
  // Les mêmes mots que la porte d'entrée (repérer, coller son lien, organiser), et le bon geste :
  // « touche » sur un écran tactile, « clique » à la souris (21 octobre 2026)
  // Sur ordinateur, le studio vide dit seulement où cliquer (choix de Pauline, 21 octobre 2026)
  const tactile = window.matchMedia("(pointer: coarse)").matches;
  const geste = tactile ? "touche" : "clique sur";
  document.getElementById("accueil-texte").textContent = studioVide
    ? (tactile ? "Ton studio attend tes premiers articles. Repère un article en ligne, puis touche le bouton + et colle son lien."
               : "Ton studio attend tes premiers articles. Clique sur le bouton + pour en ajouter un.")
    : geste[0].toUpperCase() + geste.slice(1) + " un meuble pour voir les articles que tu y as rangés.";
  // Sur téléphone, sans la bulle, le même mot s'affiche sous la pièce quand le studio est vide (issue n° 7)
  const indice = document.getElementById("indice-vide");
  if (indice) {
    indice.hidden = false;
    indice.textContent = studioVide ? document.getElementById("accueil-texte").textContent : "";
  }
  // Le nombre d'articles en toutes lettres, dans la liste des meubles de la bulle (ordinateur) ;
  // « Vide » plutôt qu'« Aucun article » (choix de Pauline, 19 octobre 2026)
  document.querySelectorAll("[data-compte-texte]").forEach(function (element) {
    const n = meubles[element.dataset.compteTexte].articles.length;
    element.textContent = n === 0 ? "Vide" : libelleNombre(n);
  });
  document.querySelectorAll("[data-compte]").forEach(function (element) {
    const n = meubles[element.dataset.compte].articles.length;
    element.textContent = n;
    element.classList.toggle("zero", n === 0);
  });
  document.querySelectorAll(".meuble").forEach(function (element) {
    const meuble = meubles[element.dataset.meuble];
    const promo = meuble.articles.some(function (a) { return a.remise; });
    element.setAttribute("aria-label", "Ouvrir " + meuble.nom.toLowerCase() + ", " + libelleNombre(meuble.articles.length).toLowerCase()
      + (promo ? ", dont un article en promotion" : ""));
    element.classList.toggle("est-vide", meuble.articles.length === 0);
  });
  // La pièce dorée « % » : sur l'épingle du meuble et sur sa case dans la barre, s'il contient un article remisé
  document.querySelectorAll("[data-meuble]").forEach(function (element) {
    element.classList.toggle("en-promo", meubles[element.dataset.meuble].articles.some(function (a) { return a.remise; }));
  });
}

// Le panneau : il montre ce qui est rangé dans le meuble choisi
const panneau = document.getElementById("panneau");
const liste = document.getElementById("articles");
const vide = document.getElementById("vide");
let meubleOuvert = null;  // le meuble dont le panneau est ouvert, proposé pour ranger un nouvel article

// Les règles de mise en forme des photos (décision de Pauline, 19 octobre 2026) :
// 1. la case prend la couleur du fond de la photo ;
// 2. le produit est recadré à son contour, puis centré ; les ombres portées ne comptent pas dans
//    le contour, sinon le produit paraît décalé du côté opposé à son ombre ;
// 3. il occupe 80 % de la case dans sa plus grande dimension, la même marge pour tous ;
// 4. si le fond n'est pas uni, ou si le site interdit de lire la photo, elle remplit toute la case ;
// 5. si le produit touche deux bords de la photo ou plus, la photo est déjà cadrée serré : elle est
//    montrée entière, centrée, sans recadrage (20 octobre 2026) ;
// 6. les articles de la bibliothèque (livres, BD, carnets, agendas, papeterie) sont montrés comme un
//    livre posé : la couverture entière, centrée, sur fond blanc, sans analyse (20 octobre 2026).
// L'analyse se fait une fois, et ses résultats (« fond », « cadre » ou « plein ») s'enregistrent avec
// l'article, avec le numéro de la règle (« analyse ») : quand la règle change, la photo est relue.
const VERSION_ANALYSE = 3;  // 2 : les ombres ne comptent plus dans le contour (19 octobre 2026) ;
                            // 3 : une photo déjà cadrée serré n'est plus recadrée (20 octobre 2026)
function analyserPhoto(adresse, rappel) {
  const sonde = new Image();
  sonde.crossOrigin = "anonymous";
  sonde.addEventListener("load", function () {
    try {
      // La photo réduite à 160 pixels au plus suffit pour trouver le fond et le contour
      const echelle = Math.min(1, 160 / Math.max(sonde.naturalWidth, sonde.naturalHeight));
      const w = Math.max(8, Math.round(sonde.naturalWidth * echelle));
      const h = Math.max(8, Math.round(sonde.naturalHeight * echelle));
      const toile = document.createElement("canvas");
      toile.width = w;
      toile.height = h;
      const ctx = toile.getContext("2d");
      ctx.drawImage(sonde, 0, 0, w, h);
      const pixels = ctx.getImageData(0, 0, w, h).data;
      const pixel = function (x, y) { const i = (y * w + x) * 4; return [pixels[i], pixels[i + 1], pixels[i + 2]]; };
      // Le fond, c'est la couleur que partagent au moins cinq des huit points du bord : le produit
      // peut toucher un bord, et un fond de studio a souvent un léger dégradé
      const xs = [1, Math.round(w / 2), w - 2], ys = [1, Math.round(h / 2), h - 2];
      const points = [[xs[0], ys[0]], [xs[2], ys[0]], [xs[0], ys[2]], [xs[2], ys[2]], [xs[1], ys[0]], [xs[1], ys[2]], [xs[0], ys[1]], [xs[2], ys[1]]].map(function (p) { return pixel(p[0], p[1]); });
      const ecart = function (p, q) { return Math.max(Math.abs(p[0] - q[0]), Math.abs(p[1] - q[1]), Math.abs(p[2] - q[2])); };
      const groupes = points.map(function (p) { return points.filter(function (q) { return ecart(p, q) <= 16; }); });
      const groupe = groupes.reduce(function (a, g) { return g.length > a.length ? g : a; });
      if (groupe.length < 5) { rappel(null); return; }
      const fond = [0, 1, 2].map(function (i) {
        return Math.round(groupe.reduce(function (s, p) { return s + p[i]; }, 0) / groupe.length);
      });
      // Le contour du produit : tout ce qui s'écarte nettement du fond, sauf les ombres. Une ombre est
      // grise (ses trois couleurs restent proches), plus sombre que le fond, mais de peu
      const lum = function (p) { return (p[0] + p[1] + p[2]) / 3; };
      const ombre = function (p) {
        const assombri = lum(fond) - lum(p);
        return assombri > 0 && assombri < 70 && Math.max(p[0], p[1], p[2]) - Math.min(p[0], p[1], p[2]) < 20;
      };
      let x0 = w, y0 = h, x1 = -1, y1 = -1;
      for (let y = 0; y < h; y++) {
        for (let x = 0; x < w; x++) {
          const p = pixel(x, y);
          if (ecart(p, fond) > 28 && !ombre(p)) {
            if (x < x0) x0 = x;
            if (x > x1) x1 = x;
            if (y < y0) y0 = y;
            if (y > y1) y1 = y;
          }
        }
      }
      // Le produit touche deux bords ou plus : la photo est déjà cadrée serré, et un produit clair sur
      // un fond clair ne se distingue que par ses motifs ; on la garde entière
      const marge = 0.03;  // à 3 % près du bord
      const bords = (x0 <= w * marge) + (y0 <= h * marge) + (x1 >= w * (1 - marge) - 1) + (y1 >= h * (1 - marge) - 1);
      const cadre = x1 < 0 || bords >= 2 ? [0, 0, 1, 1] : [x0 / w, y0 / h, (x1 + 1) / w, (y1 + 1) / h].map(function (v) { return Math.round(v * 1000) / 1000; });
      rappel({ fond: "#" + fond.map(function (v) { return v.toString(16).padStart(2, "0"); }).join("").toUpperCase(), cadre: cadre });
    } catch (e) {
      rappel(null);
    }
  });
  sonde.addEventListener("error", function () { rappel(null); });
  sonde.src = adresse;
}

// Place la photo pour que le contour du produit occupe 80 % de la case, centré
function cadrer(img, cadre) {
  function placer() {
    const W = img.naturalWidth, H = img.naturalHeight;
    if (!W || !H) return;
    // En pourcentages de la case, qui est carrée : le calcul ne dépend pas de sa taille à l'écran
    const cw = (cadre[2] - cadre[0]) * W, ch = (cadre[3] - cadre[1]) * H;
    const k = 80 / Math.max(cw, ch);
    img.classList.add("cadree");
    img.style.width = W * k + "%";
    img.style.height = H * k + "%";
    img.style.left = 50 - (cadre[0] * W + cw / 2) * k + "%";
    img.style.top = 50 - (cadre[1] * H + ch / 2) * k + "%";
  }
  if (img.complete) placer(); else img.addEventListener("load", placer);
}

function fiche(article) {
  const ligne = document.createElement("li");
  const achete = estAchete(article);
  ligne.className = "article" + (achete ? " achete" : "");

  // Le visuel : la photo du produit si on l'a, sinon le dessin d'exemple. Avec un lien, il ouvre
  // lui aussi le site du produit dans un nouvel onglet (19 octobre 2026)
  const visuel = document.createElement(article.lien ? "a" : "span");
  visuel.className = "visuel";
  if (article.lien) {
    visuel.href = article.lien;
    visuel.target = "_blank";
    visuel.rel = "noopener";
    visuel.tabIndex = -1;  // le nom porte déjà le lien au clavier
  }
  // Sans photo, ou si la photo ne se charge pas : une vignette neutre, l'icône du meuble
  const cleMeuble = article.meuble || meubleDe(article) || "coffre";
  const neutre = '<svg class="vignette-neutre"><use href="#ic-' + cleMeuble + '" /></svg>';
  if (article.image && cleMeuble === "bibliotheque") {
    // Un livre, un carnet : la couverture entière, centrée, posée sur fond blanc, avec une ombre douce
    visuel.style.background = "#FFFFFF";
    visuel.classList.add("visuel-livre");
    const img = document.createElement("img");
    img.src = article.image;
    img.alt = "";
    img.loading = "lazy";
    img.addEventListener("error", function () { visuel.style.background = ""; visuel.classList.remove("visuel-livre"); visuel.innerHTML = neutre; });
    visuel.appendChild(img);
  } else if (article.image) {
    // La case prend la couleur du fond de la photo : le produit y flotte, centré, sans toucher les bords
    visuel.style.background = article.fond || "#FFFFFF";
    visuel.classList.toggle("visuel-plein", Boolean(article.plein));
    const img = document.createElement("img");
    img.src = article.image;
    const aJour = article.analyse === VERSION_ANALYSE;
    if (article.cadre && aJour) cadrer(img, article.cadre);
    // La photo n'a pas encore été analysée, ou avec une règle plus ancienne : elle l'est, et le résultat s'enregistre
    if (!aJour) {
      analyserPhoto(article.image, function (resultat) {
        article.analyse = VERSION_ANALYSE;
        delete article.plein;
        if (resultat) {
          article.fond = resultat.fond;
          article.cadre = resultat.cadre;
          visuel.style.background = resultat.fond;
          visuel.classList.remove("visuel-plein");
          cadrer(img, resultat.cadre);
        } else {
          article.plein = true;
          visuel.classList.add("visuel-plein");
        }
        enregistrerArticles();
      });
    }
    img.alt = "";
    img.loading = "lazy";
    img.addEventListener("error", function () { visuel.style.background = ""; visuel.innerHTML = neutre; });
    visuel.appendChild(img);
  } else {
    visuel.innerHTML = dessins[article.dessin] || neutre;
  }
  visuel.setAttribute("aria-hidden", "true");
  ligne.appendChild(visuel);

  // Le texte : un lien vers le site du produit quand il existe
  const texte = document.createElement(article.lien ? "a" : "div");
  texte.className = "article-texte";
  if (article.lien) {
    texte.href = article.lien;
    texte.target = "_blank";
    texte.rel = "noopener";
  }
  texte.innerHTML = '<p class="article-marque"></p><p class="article-nom"></p><p class="article-ligne"><span class="article-prix"></span><span class="article-lien"></span></p>';
  texte.querySelector(".article-marque").textContent = article.marque;
  texte.querySelector(".article-nom").textContent = article.nom;
  texte.querySelector(".article-prix").textContent = article.prix;
  // En promotion : le prix du moment en rose, l'ancien barré, la pastille de la remise, une précision
  if (article.prixBarre) {
    const prix = texte.querySelector(".article-prix");
    prix.classList.add("prix-promo");
    prix.insertAdjacentHTML("afterend", '<span class="prix-barre"></span><span class="remise"></span>');
    texte.querySelector(".prix-barre").textContent = article.prixBarre;
    texte.querySelector(".prix-barre").setAttribute("aria-label", "au lieu de " + article.prixBarre);
    texte.querySelector(".remise").textContent = article.remise || "";
  }
  if (article.precision) {
    texte.querySelector(".article-ligne").insertAdjacentHTML("beforeend", '<span class="precision"></span>');
    texte.querySelector(".precision").textContent = article.precision;
  }
  // Le lien vers le site porte sur toute la fiche, sans mention (retirée le 19 octobre 2026) ;
  // un exemple sans lien garde la mention « Exemple fictif »
  if (article.lien) {
    texte.querySelector(".article-lien").remove();
  } else {
    texte.querySelector(".article-lien").textContent = "Exemple fictif";
    texte.querySelector(".article-lien").className = "article-exemple";
  }
  ligne.appendChild(texte);

  // Le bouton « Acheté »
  const bouton = document.createElement("button");
  bouton.type = "button";
  bouton.className = "bouton-achete";
  bouton.setAttribute("aria-pressed", achete ? "true" : "false");
  bouton.textContent = achete ? "Acheté ✓" : "Marquer comme acheté";
  bouton.addEventListener("click", function () {
    achats[article.id] = !estAchete(article);
    enregistrerAchats(achats);
    const nouvelle = fiche(article);
    ligne.replaceWith(nouvelle);
    nouvelle.querySelector(".bouton-achete").focus();
  });
  // Les actions de la fiche (issue n° 5, 20 octobre 2026) : « Marquer comme acheté » en texte, puis
  // trois boutons-icônes ronds, Modifier, Déplacer et Retirer, chacun nommé pour les lecteurs d'écran
  const actions = document.createElement("div");
  actions.className = "article-actions";
  function boutonIcone(classe, icone, action) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "bouton-icone " + classe;
    b.innerHTML = '<svg aria-hidden="true"><use href="#ic-' + icone + '" /></svg>';
    b.setAttribute("aria-label", action + " « " + article.nom + " »");
    b.title = action;
    return b;
  }
  const modification = boutonIcone("bouton-modifier", "crayon", "Modifier");
  modification.setAttribute("aria-haspopup", "dialog");
  modification.addEventListener("click", function () { ouvrirFenetre(article, null); });
  const deplacement = boutonIcone("bouton-deplacer", "deplacer", "Déplacer");
  deplacement.setAttribute("aria-expanded", "false");
  const retrait = boutonIcone("bouton-poubelle", "poubelle", "Retirer");
  retrait.addEventListener("click", function () { montrerConfirmation(true); });
  const icones = document.createElement("span");
  icones.className = "article-icones";
  icones.append(modification, deplacement, retrait);
  actions.append(bouton, icones);
  ligne.appendChild(actions);

  // Le choix du meuble d'arrivée : les autres meubles, et « Annuler »
  const choix = document.createElement("div");
  choix.className = "choix-meuble";
  choix.setAttribute("role", "group");
  choix.setAttribute("aria-label", "Déplacer « " + article.nom + " » vers");
  choix.hidden = true;
  choix.innerHTML = '<span class="choix-titre" aria-hidden="true">Vers :</span>';
  Object.keys(meubles).forEach(function (cle) {
    if (meubles[cle].articles.indexOf(article) !== -1) return;
    const vers = document.createElement("button");
    vers.type = "button";
    vers.className = "bouton-meuble";
    vers.innerHTML = '<svg aria-hidden="true"><use href="#ic-' + cle + '" /></svg><span></span>';
    vers.querySelector("span").textContent = meubles[cle].nom;
    vers.addEventListener("click", function () { deplacer(article, cle); });
    choix.appendChild(vers);
  });
  const renoncer = document.createElement("button");
  renoncer.type = "button";
  renoncer.className = "bouton-retirer";
  renoncer.textContent = "Annuler";
  choix.appendChild(renoncer);
  ligne.appendChild(choix);

  function montrerChoix(ouvert) {
    choix.hidden = !ouvert;
    deplacement.setAttribute("aria-expanded", ouvert ? "true" : "false");
    (ouvert ? choix.querySelector(".bouton-meuble") : deplacement).focus();
  }
  deplacement.addEventListener("click", function () { montrerChoix(choix.hidden); });
  renoncer.addEventListener("click", function () { montrerChoix(false); });

  // La confirmation avant de retirer (piste A, choisie par Pauline le 20 octobre 2026) : la ligne
  // d'actions laisse place à la question, « Retirer » ou « Garder » ; le focus va à « Garder »
  const confirmation = document.createElement("div");
  confirmation.className = "confirmation-retrait";
  confirmation.setAttribute("role", "group");
  confirmation.setAttribute("aria-label", "Retirer « " + article.nom + " » ?");
  confirmation.hidden = true;
  confirmation.innerHTML = '<span class="confirmation-texte">Retirer cet article ?</span>'
    + '<span class="confirmation-boutons"><button class="bouton-confirmer" type="button">Retirer</button>'
    + '<button class="bouton-garder" type="button">Garder</button></span>';
  confirmation.querySelector(".bouton-confirmer").addEventListener("click", function () { retirer(article); });
  confirmation.querySelector(".bouton-garder").addEventListener("click", function () { montrerConfirmation(false); });
  ligne.appendChild(confirmation);

  function montrerConfirmation(ouvert) {
    confirmation.hidden = !ouvert;
    actions.hidden = ouvert;
    if (ouvert) {
      choix.hidden = true;
      deplacement.setAttribute("aria-expanded", "false");
    }
    (ouvert ? confirmation.querySelector(".bouton-garder") : retrait).focus();
  }
  return ligne;
}

function remplirPanneau(cle) {
  const meuble = meubles[cle];
  document.getElementById("panneau-icone").setAttribute("href", "#ic-" + cle);
  document.getElementById("panneau-titre").textContent = meuble.nom;
  document.getElementById("panneau-compte").textContent = libelleNombre(meuble.articles.length);

  liste.innerHTML = "";
  meuble.articles.forEach(function (article) { liste.appendChild(fiche(article)); });

  const estVide = meuble.articles.length === 0;
  liste.hidden = estVide;
  vide.hidden = !estVide;
  document.getElementById("panneau-note").hidden = estVide || meuble.articles.every(function (a) { return a.lien; });
  document.getElementById("vide-texte").textContent = meuble.vide;
}

function ouvrir(cle) {
  meubleOuvert = cle;
  remplirPanneau(cle);
  panneau.showModal();
  // Le focus va au titre du meuble, pas à la croix : sur téléphone, la croix s'affichait entourée
  // de pointillés dès l'ouverture (retour de Pauline, 19 octobre 2026). Au clavier, Tab y mène.
  document.getElementById("panneau-titre").focus();
}

// Survoler une case de la barre, ou un meuble de la liste, soulève le meuble dans la pièce (19 octobre 2026)
document.querySelectorAll(".barre-meubles [data-meuble], .liste-meubles [data-meuble]").forEach(function (bouton) {
  const meubleDansLaPiece = document.querySelector('.meuble[data-meuble="' + bouton.dataset.meuble + '"]');
  ["mouseenter", "focus"].forEach(function (type) {
    bouton.addEventListener(type, function () { meubleDansLaPiece.classList.add("survole"); });
  });
  ["mouseleave", "blur"].forEach(function (type) {
    bouton.addEventListener(type, function () { meubleDansLaPiece.classList.remove("survole"); });
  });
});

// Un clic, ou Entrée et Espace au clavier, ouvre le meuble
document.querySelectorAll("[data-meuble]").forEach(function (element) {
  element.addEventListener("click", function () { ouvrir(element.dataset.meuble); });
  if (element.tagName.toLowerCase() === "g") {
    element.addEventListener("keydown", function (evenement) {
      if (evenement.key === "Enter" || evenement.key === " ") {
        evenement.preventDefault();
        ouvrir(element.dataset.meuble);
      }
    });
  }
});

// Fermer : le bouton, la touche Échap (gérée par le navigateur) ou un clic à côté du panneau
document.getElementById("fermer").addEventListener("click", function () { panneau.close(); });
panneau.addEventListener("click", function (evenement) {
  // Seul un clic sur le fond lui-même compte : un clic lancé au clavier (Entrée, Espace) arrive en
  // (0, 0) et passerait pour un clic à côté (corrigé le 19 octobre 2026)
  if (evenement.target !== panneau) return;
  const cadre = panneau.getBoundingClientRect();
  const dehors = evenement.clientX < cadre.left || evenement.clientX > cadre.right ||
                 evenement.clientY < cadre.top || evenement.clientY > cadre.bottom;
  if (dehors) panneau.close();
});

// Les onglets du menu : un clic ou les flèches du clavier changent le contenu de la bulle,
// et la queue de la bulle se place en face de l'onglet choisi
const onglets = Array.from(document.querySelectorAll('[role="tab"]'));
const surTelephone = window.matchMedia("(max-width: 600px)");
const bulle = document.getElementById("bulle");

function placerQueue(onglet) {
  const o = onglet.getBoundingClientRect();
  const b = bulle.getBoundingClientRect();
  bulle.style.setProperty("--queue", Math.round(o.top + o.height / 2 - b.top - 10) + "px");
  bulle.style.setProperty("--queue-x", Math.round(o.left + o.width / 2 - b.left) + "px");
}

function choisirOnglet(onglet, donnerFocus) {
  onglets.forEach(function (autre) {
    const actif = autre === onglet;
    autre.setAttribute("aria-selected", actif ? "true" : "false");
    autre.tabIndex = actif ? 0 : -1;
    document.getElementById(autre.getAttribute("aria-controls")).hidden = !actif;
  });
  if (donnerFocus) onglet.focus();
  placerQueue(onglet);
  // Sur téléphone, la boutique est une page à part, et l'icône du haut ramène au studio (issue n° 7)
  document.documentElement.classList.toggle("vue-boutique", onglet.id === "onglet-boutique");
  if (surTelephone.matches) window.scrollTo(0, 0);
}

onglets.forEach(function (onglet, rang) {
  onglet.addEventListener("click", function () {
    choisirOnglet(onglet, false);
    // Sur téléphone, l'icône touchée disparaît (on est sur sa page) : le focus passe à l'autre
    if (surTelephone.matches) onglets.find(function (o) { return o !== onglet; }).focus();
  });
  onglet.addEventListener("keydown", function (evenement) {
    const pas = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[evenement.key];
    if (pas) {
      evenement.preventDefault();
      choisirOnglet(onglets[(rang + pas + onglets.length) % onglets.length], !surTelephone.matches);
    } else if (evenement.key === "Home" || evenement.key === "End") {
      evenement.preventDefault();
      choisirOnglet(onglets[evenement.key === "Home" ? 0 : onglets.length - 1], true);
    }
  });
});

window.addEventListener("resize", function () {
  placerQueue(onglets.find(function (o) { return o.getAttribute("aria-selected") === "true"; }));
});
placerQueue(onglets[0]);

afficherCompteurs();

// Le moment de la journée, d'après l'heure de l'utilisateur : le jour de 7 h à 18 h, le soir de
// 18 h à 21 h et à l'aube, de 6 h à 7 h, la nuit le reste du temps. La fenêtre et l'ambiance de la
// pièce suivent (style.css). Pour essayer un moment : ?moment=jour, soir ou nuit dans l'adresse.
const momentForce = new URLSearchParams(location.search).get("moment");

function momentDuJour(heure) {
  if (heure >= 7 && heure < 18) return "jour";
  if ((heure >= 18 && heure < 21) || heure === 6) return "soir";
  return "nuit";
}

function appliquerMoment() {
  const moment = ["jour", "soir", "nuit"].includes(momentForce) ? momentForce : momentDuJour(new Date().getHours());
  document.documentElement.dataset.moment = moment;
}

appliquerMoment();
setInterval(appliquerMoment, 60000);

// La fenêtre d'un article (issue n° 5, 20 octobre 2026) : le formulaire sort du panneau pour servir à
// trois portes d'entrée. « Ajouter un article » dans un meuble l'ouvre avec ce meuble déjà choisi ;
// « Modifier » sur une fiche l'ouvre rempli ; le bouton « + » l'ouvre vide, et l'on choisit le meuble.
// (Le formulaire d'ajout date de l'issue n° 2, le choix « Ranger dans » du 19 octobre 2026.)
const boutonAjouter = document.getElementById("ajouter");
const boutonPlus = document.getElementById("bouton-plus");
const fenetre = document.getElementById("fenetre");
const formulaire = document.getElementById("formulaire-ajout");
const boutonValider = document.getElementById("valider");
const annonce = document.getElementById("annonce");
const CHAMPS = {
  lien: document.getElementById("champ-lien"),
  nom: document.getElementById("champ-nom"),
  marque: document.getElementById("champ-marque"),
  prix: document.getElementById("champ-prix"),
  photo: document.getElementById("champ-photo"),
  meuble: document.getElementById("champ-meuble")
};
CHAMPS.meuble.add(new Option("Choisis un meuble", ""));
Object.keys(meubles).forEach(function (cle) { CHAMPS.meuble.add(new Option(meubles[cle].nom, cle)); });
let articleModifie = null;  // l'article en cours de modification, ou null pour un nouvel article

function adresseWeb(texte) {
  try {
    const url = new URL(texte);
    return url.protocol === "https:" || url.protocol === "http:";
  } catch (e) {
    return false;
  }
}

function montrerErreur(cle, message) {
  const champ = CHAMPS[cle];
  const erreur = document.getElementById("erreur-" + cle);
  champ.setAttribute("aria-invalid", message ? "true" : "false");
  erreur.textContent = message || "";
  erreur.hidden = !message;
}

// Un prix tapé en chiffres seuls prend le symbole de l'euro : « 29,9 » devient « 29,90 € », « 29 » devient « 29 € »
function prixAffiche(texte) {
  const propre = texte.trim();
  if (!/^\d+([.,]\d{1,2})?$/.test(propre)) return propre;
  const [euros, centimes] = propre.replace(".", ",").split(",");
  return centimes ? euros + "," + centimes.padEnd(2, "0") + " €" : euros + " €";
}

// Ouvre la fenêtre : vide pour un nouvel article (le meuble éventuellement déjà choisi), ou remplie
// avec les informations de l'article à modifier
function ouvrirFenetre(article, cleMeuble) {
  articleModifie = article || null;
  formulaire.reset();
  ["lien", "nom", "photo", "meuble"].forEach(function (cle) { montrerErreur(cle, ""); });
  document.getElementById("ajout-titre").textContent = article ? "Modifier l'article" : "Nouvel article";
  boutonValider.textContent = article ? "Enregistrer" : "Ranger l'article";
  if (article) {
    CHAMPS.lien.value = article.lien || "";
    CHAMPS.nom.value = article.nom || "";
    CHAMPS.marque.value = article.marque || "";
    CHAMPS.prix.value = article.prix || "";
    CHAMPS.photo.value = article.image || "";
    CHAMPS.meuble.value = meubleDe(article);
  } else {
    CHAMPS.meuble.value = cleMeuble || "";
  }
  fenetre.showModal();
  CHAMPS.lien.focus();
}

boutonAjouter.addEventListener("click", function () { ouvrirFenetre(null, meubleOuvert); });
boutonPlus.addEventListener("click", function () { ouvrirFenetre(null, ""); });
document.getElementById("annuler").addEventListener("click", function () { fenetre.close(); });
// Un clic sur le fond, à côté de la fenêtre, la ferme aussi
fenetre.addEventListener("click", function (evenement) {
  if (evenement.target !== fenetre) return;
  const cadre = fenetre.getBoundingClientRect();
  if (evenement.clientX < cadre.left || evenement.clientX > cadre.right ||
      evenement.clientY < cadre.top || evenement.clientY > cadre.bottom) fenetre.close();
});

formulaire.addEventListener("submit", function (evenement) {
  evenement.preventDefault();
  const lien = CHAMPS.lien.value.trim();
  const nom = CHAMPS.nom.value.trim();
  const photo = CHAMPS.photo.value.trim();
  const cle = CHAMPS.meuble.value;
  // Une photo des articles de départ a une adresse locale, dans le dossier des photos : elle reste valable telle quelle
  const photoInchangee = articleModifie && photo === articleModifie.image;
  const erreurs = {
    lien: !lien ? "Colle le lien de la page du produit." : (!adresseWeb(lien) ? "Ce lien ne fonctionne pas : il doit commencer par https://" : ""),
    nom: !nom ? "Donne un nom à ton article." : "",
    meuble: !cle ? "Choisis le meuble où le ranger." : "",
    photo: photo && !photoInchangee && !adresseWeb(photo) ? "Cette adresse ne fonctionne pas : elle doit commencer par https://" : ""
  };
  Object.keys(erreurs).forEach(function (champ) { montrerErreur(champ, erreurs[champ]); });
  const premiere = ["lien", "nom", "meuble", "photo"].find(function (champ) { return erreurs[champ]; });
  if (premiere) {
    CHAMPS[premiere].focus();
    return;
  }
  const infos = { lien: lien, nom: nom, marque: CHAMPS.marque.value.trim(), prix: prixAffiche(CHAMPS.prix.value), image: photo };

  if (articleModifie) {
    // Modifier : la fiche est mise à jour à sa place ; si le meuble change, l'article s'y déplace
    const article = articleModifie;
    const depart = meubleDe(article);
    if (article.image !== photo) {
      // Une nouvelle photo est relue selon les règles de mise en forme
      delete article.fond; delete article.cadre; delete article.plein; delete article.analyse;
    }
    Object.assign(article, infos);
    if (cle !== depart) {
      meubles[depart].articles.splice(meubles[depart].articles.indexOf(article), 1);
      article.meuble = cle;
      meubles[cle].articles.unshift(article);
    }
    enregistrerArticles();
    fenetre.close();
    remplirPanneau(meubleOuvert);
    afficherCompteurs();
    if (cle !== depart) {
      annonce.textContent = "« " + nom + " » est modifié et déplacé dans " + meubles[cle].nom.toLowerCase() + ".";
      (liste.querySelector(".article-texte") || boutonAjouter).focus();
    } else {
      annonce.textContent = "« " + nom + " » est modifié.";
      const rang = meubles[cle].articles.indexOf(article);
      liste.querySelectorAll(".bouton-modifier")[rang].focus();
    }
    return;
  }

  // Ranger un nouvel article : il se range en tête du meuble choisi, et le panneau de ce meuble s'ouvre
  const article = Object.assign({ id: "ajout-" + Date.now(), ajoute: true, meuble: cle }, infos);
  meubles[cle].articles.unshift(article);
  enregistrerArticles();
  fenetre.close();
  meubleOuvert = cle;
  remplirPanneau(cle);
  afficherCompteurs();
  if (!panneau.open) panneau.showModal();
  annonce.textContent = "« " + nom + " » est rangé dans " + meubles[cle].nom.toLowerCase() + ".";
  liste.querySelector(".article-texte").focus();
});

// Sortir un article de son meuble : le panneau se redessine, et le focus va à l'article qui prend
// sa place, ou au bouton d'ajout s'il n'y en a plus
function sortir(article) {
  const cle = meubleDe(article);
  const rang = meubles[cle].articles.indexOf(article);
  meubles[cle].articles.splice(rang, 1);
  remplirPanneau(cle);
  afficherCompteurs();
  const suivants = liste.querySelectorAll(".article-texte");
  (suivants[Math.min(rang, suivants.length - 1)] || boutonAjouter).focus();
}

// Retirer un article, ajouté ou de départ : il quitte le meuble, et ne revient pas au rechargement
function retirer(article) {
  delete achats[article.id];
  enregistrerAchats(achats);
  sortir(article);
  enregistrerArticles();
  annonce.textContent = "« " + article.nom + " » est retiré.";
}

// Déplacer un article : il quitte le meuble ouvert et se range en tête du meuble choisi
function deplacer(article, cle) {
  sortir(article);
  article.meuble = cle;
  meubles[cle].articles.unshift(article);
  afficherCompteurs();
  enregistrerArticles();
  annonce.textContent = "« " + article.nom + " » est déplacé dans " + meubles[cle].nom.toLowerCase() + ".";
}


// ---------- La navigation sur téléphone (issue n° 7, 21 octobre 2026) ----------
// Mise au point avec Pauline dans planches/navigation.html.

// Le store de la boutique : une toile rayée en pente, tendue sous une barre de bois, qui finit en
// festons, un par rayure ; un pli d'ombre sous la barre, un reflet au milieu
function dessinerStore() {
  const L = 340, N = 10, haut = 12, bas = 52, retrait = 16, creux = 14;
  const couleurs = ["var(--rose)", "#FFF6EA"];
  let rayures = "", festons = "", ombres = "";
  for (let i = 0; i < N; i++) {
    const h0 = retrait + i * (L - 2 * retrait) / N, h1 = retrait + (i + 1) * (L - 2 * retrait) / N;
    const b0 = i * L / N, b1 = (i + 1) * L / N, c = couleurs[i % 2];
    rayures += '<polygon points="' + h0 + "," + haut + " " + h1 + "," + haut + " " + b1 + "," + bas + " " + b0 + "," + bas + '" fill="' + c + '" />';
    const feston = "M" + b0 + " " + bas + " L" + b1 + " " + bas + " Q" + (b0 + b1) / 2 + " " + (bas + 2 * creux) + " " + b0 + " " + bas + " Z";
    ombres += '<path d="' + feston + '" transform="translate(0 4)" fill="rgba(74, 51, 40, 0.18)" />';
    festons += '<path d="' + feston + '" fill="' + c + '" stroke="var(--brun)" stroke-width="2.5" stroke-linejoin="round" />';
  }
  const toile = retrait + "," + haut + " " + (L - retrait) + "," + haut + " " + L + "," + bas + " 0," + bas;
  document.getElementById("store").innerHTML = '<svg viewBox="-4 0 348 ' + (bas + creux + 10) + '">'
    + '<defs><linearGradient id="pli" x1="0" y1="' + haut + '" x2="0" y2="' + bas + '" gradientUnits="userSpaceOnUse">'
    + '<stop offset="0" stop-color="#4A3328" stop-opacity="0.32" /><stop offset="0.3" stop-color="#4A3328" stop-opacity="0" />'
    + '<stop offset="0.62" stop-color="#FFFFFF" stop-opacity="0.22" /><stop offset="0.8" stop-color="#FFFFFF" stop-opacity="0" />'
    + '<stop offset="1" stop-color="#4A3328" stop-opacity="0.12" /></linearGradient></defs>'
    + ombres + festons + rayures
    + '<polygon points="' + toile + '" fill="url(#pli)" />'
    + '<polygon points="' + toile + '" fill="none" stroke="var(--brun)" stroke-width="2.5" stroke-linejoin="round" />'
    + '<rect x="6" y="5" width="328" height="10" rx="5" fill="#7A5134" stroke="var(--brun)" stroke-width="2.5" />'
    + '<rect x="14" y="7.5" width="300" height="2.5" rx="1.25" fill="#FFFFFF" opacity="0.25" />'
    + '<circle cx="6" cy="10" r="6" fill="#7A5134" stroke="var(--brun)" stroke-width="2.5" />'
    + '<circle cx="334" cy="10" r="6" fill="#7A5134" stroke="var(--brun)" stroke-width="2.5" /></svg>';
}
dessinerStore();

// La porte d'entrée : à la première ouverture sur téléphone, puis quand on touche le nom de l'app
const CLE_PORTE = "tiny-studio-porte-vue";
const porte = document.getElementById("porte");
const racine = document.documentElement;

function porteDejaVue() {
  try { return localStorage.getItem(CLE_PORTE) === "1"; } catch (erreur) { return false; }
}

function retenirPorte() {
  try { localStorage.setItem(CLE_PORTE, "1"); } catch (erreur) { /* le navigateur refuse : elle reviendra */ }
}

// La pièce de la porte : une copie de la pièce du studio, et par-dessus elle, au même repère,
// l'immeuble vu de dehors. Les meubles y attendent, cachés, la fin du glissement
function preparerPorte() {
  const cadre = document.getElementById("porte-piece");
  cadre.textContent = "";
  const piece = document.querySelector(".cadre-piece svg.studio").cloneNode(true);
  piece.removeAttribute("role");
  piece.removeAttribute("aria-label");
  piece.querySelectorAll("[tabindex], [role]").forEach(function (element) {
    element.removeAttribute("tabindex");
    element.removeAttribute("role");
  });
  const immeuble = document.getElementById("immeuble").content.querySelector(".ext").cloneNode(true);
  piece.appendChild(immeuble);
  piece.setAttribute("viewBox", immeuble.getAttribute("data-viewbox"));
  // Le décor arrive d'un bloc, les meubles l'un après l'autre, de près
  let rang = 0;
  piece.querySelectorAll(".objets > *").forEach(function (objet) {
    objet.style.transitionDelay = objet.classList.contains("meuble") ? (0.04 + 0.03 * rang++) + "s" : "0s";
  });
  cadre.appendChild(piece);
  porte.classList.remove("sortie", "ouverte", "devoile", "meubles");
}

function ouvrirPorte() {
  if (!surTelephone.matches) return;
  choisirOnglet(onglets[0], false);
  preparerPorte();
  racine.classList.add("porte-ouverte", "avant-entree", "piece-cachee", "entree");
  porte.hidden = false;
  window.scrollTo(0, 0);
  document.getElementById("porte-entrer").focus();
}

function fermerPorte() {
  porte.hidden = true;
  document.getElementById("porte-piece").textContent = "";
  racine.classList.remove("porte-ouverte", "avant-entree", "piece-cachee");
  setTimeout(function () { racine.classList.remove("entree"); }, 1200);
}

function entrer() {
  retenirPorte();
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    fermerPorte();
    return;
  }
  const piece = porte.querySelector(".porte-piece svg");
  const a = piece.getBoundingClientRect();
  const b = document.querySelector(".cadre-piece svg.studio").getBoundingClientRect();
  // La porte s'ouvre et les textes s'effacent, puis la façade s'en va
  porte.classList.add("sortie", "ouverte");
  racine.classList.remove("porte-ouverte");
  setTimeout(function () { porte.classList.add("devoile"); }, 80);
  setTimeout(function () {
    // La pièce glisse jusqu'à sa place : le viewBox de la porte est plus grand que celui de la pièce
    // (60 26 660 676), on cale le coin de la pièce, et sa largeur, sur la pièce du studio
    const vb = piece.getAttribute("viewBox").split(" ").map(Number);
    const ka = a.width / vb[2], s = (b.width / 660) / ka;
    const tx = b.left - a.left - s * (60 - vb[0]) * ka, ty = b.top - a.top - s * (26 - vb[1]) * ka;
    piece.style.transformOrigin = "0 0";
    piece.style.transform = "translate(" + tx + "px, " + ty + "px) scale(" + s + ")";
    racine.classList.remove("avant-entree");
  }, 260);
  // Les meubles arrivent pendant la fin du glissement
  setTimeout(function () { porte.classList.add("meubles"); }, 560);
  // La pièce de la porte est posée exactement sur celle du studio, meubles compris : on échange
  setTimeout(function () {
    fermerPorte();
    document.getElementById("bouton-plus").focus({ preventScroll: true });
  }, 1100);
}

document.getElementById("porte-entrer").addEventListener("click", entrer);

// Le nom de l'app ramène à la porte d'entrée, sur téléphone
const nomApp = document.querySelector(".marque");
function brancherNomApp() {
  if (surTelephone.matches) {
    nomApp.setAttribute("role", "button");
    nomApp.tabIndex = 0;
    nomApp.setAttribute("aria-label", "Revoir l'accueil de Tiny Studio");
  } else {
    nomApp.removeAttribute("role");
    nomApp.removeAttribute("tabindex");
    nomApp.removeAttribute("aria-label");
  }
}
nomApp.addEventListener("click", ouvrirPorte);
nomApp.addEventListener("keydown", function (evenement) {
  if (surTelephone.matches && (evenement.key === "Enter" || evenement.key === " ")) {
    evenement.preventDefault();
    ouvrirPorte();
  }
});
surTelephone.addEventListener("change", brancherNomApp);
brancherNomApp();

if (surTelephone.matches && !porteDejaVue()) ouvrirPorte();
