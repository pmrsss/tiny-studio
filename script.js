// Les visuels des articles : le packshot du produit (champ « image »), téléchargé dans images/ pour
// s'afficher partout ; à défaut, un dessin dans le style de la pièce (champ « dessin »).
const dessins = {};  // les dessins des premiers articles, remplacés par les packshots le 19 octobre 2026, sont dans l'historique Git

// Les cinq meubles et les vrais articles de Pauline (19 octobre 2026), chacune avec « lien », la
// page du produit. La coiffeuse est vide exprès, pour montrer un meuble qui n'a encore rien.
// Chaque meuble donne sa teinte à son panneau.

const meubles = {
  dressing: {
    nom: "Le dressing",
    teinte: "#F3C3CC",
    vide: "Ton prochain coup de cœur mode ira ici.",
    articles: [
      // Les premiers vrais articles de Pauline (19 octobre 2026), prix relevés ce jour-là ; aucune n'est en promotion
      { id: "zara-bomber-8490709", image: "images/zara-bomber.jpg", fond: "#F0F0F0", marque: "Zara", nom: "Veste bomber en matière synthétique, noir", prix: "25,99 €",
        lien: "https://www.zara.com/fr/fr/veste-bomber-en-matiere-synthetique-p08490709.html?v1=545485930&v2=2419737" },
      { id: "cos-bob-1361189003", image: "images/cos-chapeau.jpg", fond: "#EBE9E7", marque: "COS", nom: "Chapeau seau en laine mélangée imprimé léopard, brun", prix: "59 €",
        lien: "https://www.cos.com/fr-fr/women/accessories/hatsscarvesgloves/bucket-hats/product/sculpted-wool-bucket-hat-brown-leopard-print-1361189003" },
      { id: "ganni-sac-kat-A6997", image: "images/ganni-sac-kat.jpg", fond: "#F6F6F6", marque: "Ganni", nom: "Grand sac Kat en fausse fourrure, Foxtrot", prix: "1 095 €",
        lien: "https://www.ganni.com/fr-fr/grand-sac-kat-fausse-fourrure-A6997.html" }
    ]
  },
  bibliotheque: {
    nom: "La bibliothèque",
    teinte: "#D9A877",
    vide: "Le prochain livre qui te fait envie ira ici.",
    articles: [
      // Les vrais articles de Pauline (19 octobre 2026), prix relevés ce jour-là
      { id: "hobonichi-techo-2027-tiesheep", image: "images/hobonichi-techo.jpg", fond: "#FFFFFF", marque: "Hobonichi", nom: "Agenda Techo 2027 Weeks, couverture Bow & Tie : Sheep Sheep Sheep", prix: "34 à 35 €",
        lien: "https://www.1101.com/store/techo/en/2027/pc/detail_cover/wb27_tiesheep/" },
      { id: "fnac-yellowface-21544319", image: "images/fnac-yellowface.jpg", fond: "#FFFFFF", marque: "Rebecca F. Kuang", nom: "Yellowface, en poche", prix: "8,60 €",
        lien: "https://www.fnac.com/a21544319/Rebecca-F-Kuang-Yellowface-poche" },
      { id: "amazon-purgatoire-2266246240", image: "images/amazon-purgatoire.jpg", fond: "#FFFFFF", marque: "Karine Giebel", nom: "Purgatoire des innocents, en poche", prix: "9,60 €",
        lien: "https://www.amazon.fr/dp/2266246240" }
    ]
  },
  deco: {
    nom: "La commode déco",
    teinte: "#A9B9F0",
    vide: "Ta prochaine trouvaille déco ira ici.",
    articles: [
      // Les vrais articles de Pauline (19 octobre 2026), prix relevés ce jour-là
      { id: "diptyque-figuier-fi600", image: "images/diptyque-figuier.jpg", fond: "#F8F8F8", marque: "Diptyque", nom: "Bougie grand modèle Figuier, 600 g", prix: "190 €",
        lien: "https://diptyqueparis.com/fr-fr/products/bougie-grand-modele-figuier-fi600" },
      { id: "themasie-vase-malik-151875", image: "images/themasie-malik.jpg", fond: "#EDECEB", marque: "Themasie", nom: "Vase Malik haut en dolomite galvanisée, gris chromé, 29,5 cm", prix: "16,95 €",
        prixBarre: "18,95 €", remise: "-10 %", precision: "Précommande, envoi dès le 30 décembre",
        lien: "https://www.themasie.com/fr/acheter-vases/151875-grand-vase-en-dolomite-galvanisee-malik.html" }
    ]
  },
  coffre: {
    nom: "Le coffre fourre-tout",
    teinte: "#C98A52",
    vide: "Tout ce qui ne va dans aucun meuble ira ici.",
    articles: [
      // Les vrais articles de Pauline (19 octobre 2026), prix relevés ce jour-là
      { id: "hm-plaid-0995539095", image: "images/hm-plaid.jpg", fond: "#F9F9F9", marque: "H&M Home", nom: "Plaid en tissu polaire à motif, crème", prix: "9,99 €",
        lien: "https://www2.hm.com/fr_fr/productpage.0995539095.html" },
      { id: "ikea-stockholm-40586508", image: "images/ikea-stockholm.jpg", fond: "#FFFFFF", marque: "IKEA", nom: "Banc TV STOCKHOLM 2025 à portes coulissantes, plaqué chêne", prix: "369 €",
        lien: "https://www.ikea.com/fr/fr/p/stockholm-2025-banc-tv-portes-coulissantes-plaque-chene-40586508/" }
    ]
  },
  coiffeuse: {
    nom: "La coiffeuse",
    teinte: "#EED3AE",
    vide: "Ton prochain soin ou ton prochain rouge à lèvres ira ici.",
    articles: []
  }
};

// Le tag « Acheté » : il se coche et se décoche sur chaque fiche, et le navigateur s'en souvient
const CLE_ACHATS = "tiny-studio-achats";

function lireAchats() {
  try { return JSON.parse(localStorage.getItem(CLE_ACHATS)) || {}; } catch (e) { return {}; }
}

function enregistrerAchats(achats) {
  try { localStorage.setItem(CLE_ACHATS, JSON.stringify(achats)); } catch (e) { /* le choix ne sera pas retenu */ }
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
  const neutre = '<svg class="vignette-neutre"><use href="#ic-' + (article.meuble || "coffre") + '" /></svg>';
  if (article.image) {
    // La case prend la couleur du fond de la photo : le produit y flotte, centré, sans toucher les bords
    visuel.style.background = article.fond || "#FFFFFF";
    const img = document.createElement("img");
    img.src = article.image;
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
  // Un article ajouté à la main peut être retiré
  if (article.ajoute) {
    const actions = document.createElement("div");
    actions.className = "article-actions";
    const retrait = document.createElement("button");
    retrait.type = "button";
    retrait.className = "bouton-retirer";
    retrait.textContent = "Retirer";
    retrait.setAttribute("aria-label", "Retirer « " + article.nom + " »");
    retrait.addEventListener("click", function () { retirer(article); });
    actions.append(bouton, retrait);
    ligne.appendChild(actions);
  } else {
    ligne.appendChild(bouton);
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
  ouvrirFormulaire(false);
  remplirPanneau(cle);
  panneau.showModal();
}

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
}

onglets.forEach(function (onglet, rang) {
  onglet.addEventListener("click", function () { choisirOnglet(onglet, false); });
  onglet.addEventListener("keydown", function (evenement) {
    const pas = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[evenement.key];
    if (pas) {
      evenement.preventDefault();
      choisirOnglet(onglets[(rang + pas + onglets.length) % onglets.length], true);
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

// Ranger un article à la main (issue n° 2, 19 octobre 2026) : un formulaire dans le panneau ; l'article
// apparaît en tête du meuble choisi, le compteur se met à jour, et un article ajouté peut être retiré.
// « Ranger dans » est réglé sur le meuble ouvert et se change avant de valider.
// Elle ne survit pas encore à un rechargement : l'enregistrement d'une visite à l'autre est la suite.
const boutonAjouter = document.getElementById("ajouter");
const formulaire = document.getElementById("formulaire-ajout");
const annonce = document.getElementById("annonce");
const CHAMPS = {
  lien: document.getElementById("champ-lien"),
  nom: document.getElementById("champ-nom"),
  marque: document.getElementById("champ-marque"),
  prix: document.getElementById("champ-prix"),
  photo: document.getElementById("champ-photo"),
  meuble: document.getElementById("champ-meuble")
};
Object.keys(meubles).forEach(function (cle) { CHAMPS.meuble.add(new Option(meubles[cle].nom, cle)); });

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

function ouvrirFormulaire(ouvert) {
  formulaire.hidden = !ouvert;
  boutonAjouter.hidden = ouvert;
  boutonAjouter.setAttribute("aria-expanded", ouvert ? "true" : "false");
  if (ouvert) {
    formulaire.reset();
    CHAMPS.meuble.value = meubleOuvert;
    ["lien", "nom", "photo"].forEach(function (cle) { montrerErreur(cle, ""); });
    CHAMPS.lien.focus();
  }
}

// Un prix tapé en chiffres seuls prend le symbole de l'euro : « 29,9 » devient « 29,90 € », « 29 » devient « 29 € »
function prixAffiche(texte) {
  const propre = texte.trim();
  if (!/^\d+([.,]\d{1,2})?$/.test(propre)) return propre;
  const [euros, centimes] = propre.replace(".", ",").split(",");
  return centimes ? euros + "," + centimes.padEnd(2, "0") + " €" : euros + " €";
}

boutonAjouter.addEventListener("click", function () { ouvrirFormulaire(true); });
document.getElementById("annuler").addEventListener("click", function () {
  ouvrirFormulaire(false);
  boutonAjouter.focus();
});

formulaire.addEventListener("submit", function (evenement) {
  evenement.preventDefault();
  const lien = CHAMPS.lien.value.trim();
  const nom = CHAMPS.nom.value.trim();
  const photo = CHAMPS.photo.value.trim();
  const erreurs = {
    lien: !lien ? "Colle le lien de la page du produit." : (!adresseWeb(lien) ? "Ce lien ne fonctionne pas : il doit commencer par https://" : ""),
    nom: !nom ? "Donne un nom à ton article." : "",
    photo: photo && !adresseWeb(photo) ? "Cette adresse ne fonctionne pas : elle doit commencer par https://" : ""
  };
  Object.keys(erreurs).forEach(function (cle) { montrerErreur(cle, erreurs[cle]); });
  const premiere = ["lien", "nom", "photo"].find(function (cle) { return erreurs[cle]; });
  if (premiere) {
    CHAMPS[premiere].focus();
    return;
  }
  // Le panneau passe au meuble choisi, pour que l'article se voie là où il est rangé
  meubleOuvert = CHAMPS.meuble.value;
  const meuble = meubles[meubleOuvert];
  const article = {
    id: "ajout-" + Date.now(), ajoute: true, meuble: meubleOuvert,
    marque: CHAMPS.marque.value.trim(), nom: nom, prix: prixAffiche(CHAMPS.prix.value), lien: lien, image: photo || ""
  };
  meuble.articles.unshift(article);
  ouvrirFormulaire(false);
  remplirPanneau(meubleOuvert);
  afficherCompteurs();
  annonce.textContent = "« " + nom + " » est rangé dans " + meuble.nom.toLowerCase() + ".";
  liste.querySelector(".article-texte").focus();
});

// Retirer un article ajouté : elle quitte le meuble, le compteur se met à jour
function retirer(article) {
  const meuble = meubles[article.meuble];
  meuble.articles.splice(meuble.articles.indexOf(article), 1);
  remplirPanneau(article.meuble);
  afficherCompteurs();
  annonce.textContent = "« " + article.nom + " » est retiré.";
  boutonAjouter.focus();
}
