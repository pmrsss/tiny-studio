// Le moteur de Tiny Studio (issues n° 9 et 10, contrat docs/api.md, « Deux portes, un seul moteur »).
// Il prend le HTML d'une page de produit et son adresse, et rend la fiche du produit : nom, marque,
// prix, photo, catégorie et meuble. Le même fichier sert à la fonction de Cloudflare (lien collé),
// au favori (page ouverte dans le navigateur) et aux essais sur la base de liens. Il ne lit que du
// texte : pas de DOM, pas de réseau, pas d'IA.
(function (racine) {
  "use strict";

  // Les catégories d'objets et leur meuble (contrat, validées par Pauline le 4 novembre 2026, complétées
  // le 19). Les mots se comparent sans accents ni majuscules, au singulier comme au pluriel, en français
  // et en anglais. Quand plusieurs mots d'un même texte répondent, le plus long l'emporte : « lampe de
  // table » est de la déco, « tapis de yoga » va au coffre ; à longueur égale, l'ordre de la liste décide.
  const CATEGORIES = [
    { cle: "papeterie", meuble: "bibliotheque", mots: ["papeterie", "carnet", "agenda", "cahier", "stylo", "feutre", "crayon", "bloc-notes", "blocs-notes", "planner", "notebook", "weeks", "pen"] },
    { cle: "livres", meuble: "bibliotheque", mots: ["livre", "roman", "bd", "bande dessinee", "manga", "beau livre", "litterature", "poesie", "essai", "book", "novel", "paperback"] },
    { cle: "autre", meuble: "coffre", mots: ["chaise", "table", "etagere", "canape", "fauteuil", "tabouret", "meuble", "parure de lit", "housse de couette", "drap", "linge de lit", "linge de maison", "serviette de bain", "literie", "ensemble de literie", "tapis de yoga", "yoga mat", "haltere", "raquette", "velo", "ballon"] },
    { cle: "chaussures", meuble: "dressing", mots: ["chaussure", "botte", "bottine", "basket", "sneaker", "sandale", "escarpin", "mocassin", "sabot", "clog", "boot", "mule", "ballerine", "derby", "chausson", "slipper", "espadrille"] },
    { cle: "sacs", meuble: "dressing", mots: ["sac", "cabas", "pochette", "besace", "sac a dos", "sac porte epaule", "bag", "tote", "tote bag", "handbag", "backpack", "clutch"] },
    { cle: "accessoires", meuble: "dressing", mots: ["bijou", "collier", "boucle d'oreille", "boucles d'oreilles", "bague", "bracelet", "montre", "ceinture", "echarpe", "foulard", "bonnet", "chapeau", "casquette", "lunette", "lunettes de soleil", "lunettes de vue", "ring", "necklace", "earring", "jewelry", "jewellery", "scarf", "sunglasses", "glasses", "belt"] },
    { cle: "maquillage", meuble: "coiffeuse", mots: ["maquillage", "rouge a levres", "baume a levres", "baume teinte", "blush", "mascara", "fond de teint", "fard", "palette", "vernis", "gloss", "eyeliner", "anticernes", "enlumineur", "lipstick", "makeup", "concealer", "highlighter"] },
    { cle: "soins-parfums", meuble: "coiffeuse", mots: ["soin", "creme", "serum", "parfum", "eau de parfum", "eau de toilette", "shampooing", "masque", "nettoyant", "huile", "lotion", "gel douche", "baume", "perfume", "fragrance", "skincare", "moisturizer"] },
    { cle: "deco", meuble: "deco", mots: ["deco", "decoration", "bougie", "vase", "cadre", "affiche", "poster", "coussin", "plaid", "miroir", "lampe", "lampe de table", "lampadaire", "luminaire", "suspension", "vaisselle", "bol", "plat", "plats de service", "assiette", "tasse", "mug", "candle", "mirror", "lamp", "print", "cushion", "throw"] },
    { cle: "vetements", meuble: "dressing", mots: ["vetement", "robe", "jupe", "pull", "gilet", "chemise", "t-shirt", "tshirt", "top", "jean", "pantalon", "manteau", "veste", "blouson", "legging", "brassiere", "soutien-gorge", "chaussette", "short", "sweat", "hoodie", "cardigan", "blouse", "combinaison", "maillot", "lingerie", "dress", "skirt", "sweater", "shirt", "trousers", "pants", "jacket", "coat", "sock", "bra"] }
  ];

  // Les sites multimarques : leur nom n'est jamais la marque d'un produit (contrat, « La marque, pas le site »)
  const PLATEFORMES = ["vinted", "asos", "zalando", "laredoute", "veepee", "placedestendances", "galerieslafayette",
    "amazon", "joybuy", "printemps", "courir", "thecoolrepublic", "sephora", "fnac", "cultura", "bonmarche",
    "lebonbon", "etsy", "leboncoin", "smallable", "24s", "mytheresa", "farfetch", "ssense", "net-a-porter"];

  // Les règles propres à un site, seulement quand la base de liens montre que les règles générales s'y
  // trompent. Chacune reçoit le HTML et la fiche déjà lue, et la corrige
  const REGLES_SITES = {
    // Aesop déclare « AES » comme marque (essai du favori, 19 novembre 2026)
    "aesop.fr": function (html, fiche) { fiche.marque = "Aesop"; },
    "aesop.com": function (html, fiche) { fiche.marque = "Aesop"; },
    // The Masie déclare « Thm FR » comme marque (relevé du 19 novembre 2026)
    "themasie.com": function (html, fiche) { fiche.marque = "The Masie"; },
    // Amazon ne déclare ni données de produit ni balises de partage (relevés du 4 et du 19 novembre)
    "amazon.fr": function (html, fiche) {
      const titre = texteDe(capturer(html, /<span[^>]*id="productTitle"[^>]*>([\s\S]*?)<\/span>/i));
      if (titre) fiche.nom = titre;
      const ligne = texteDe(capturer(html, /<(?:div|span|a)[^>]*id="bylineInfo"[^>]*>([\s\S]*?)<\/(?:div|span|a)>/i));
      if (ligne) {
        const auteurs = ligne.match(/([^,(]+?)\s*\((?:Auteur|Author)/i);
        const marque = auteurs ? auteurs[1] : ligne.replace(/^(Visiter la boutique|Marque\s*:|Visit the|Brand:)\s*/i, "").replace(/\s*(Store|Boutique)$/i, "");
        if (marque && marque.length < 60) fiche.marque = marque.replace(/^(de|par|by)\s+/i, "").trim();
      }
      if (!fiche.prix) {
        const prix = texteDe(capturer(html, /id="corePrice[\s\S]{0,4000}?class="a-offscreen">([^<]+)</i));
        if (prix) fiche.prix = formaterPrix(prix.replace(/[^\d,.]/g, "").replace(/\.(?=\d{3})/g, "").replace(",", "."), /\$/.test(prix) ? "USD" : "EUR");
      }
      if (!fiche.image) {
        const image = capturer(html, /"hiRes":"(https:[^"]+)"/) || capturer(html, /id="landingImage"[^>]*data-old-hires="(https:[^"]+)"/i);
        if (image) fiche.image = image;
      }
    },
    // Vinted : la marque et le prix de l'annonce sont dans les données de la page (relevé du 19 novembre)
    "vinted.fr": function (html, fiche) {
      const marque = capturer(html, /\\?"brand_dto\\?":\{[^}]*?\\?"title\\?":\\?"([^"\\]+)/);
      if (marque) fiche.marque = decoder(marque);
      const prix = html.match(/\\?"price\\?":\{\\?"amount\\?":\\?"([\d.]+)\\?",\\?"currency_code\\?":\\?"([A-Z]{3})/);
      if (prix && !fiche.prix) fiche.prix = formaterPrix(prix[1], prix[2]);
    },
    // ASOS : le prix n'est pas dans ses données de produit (relevé du 19 novembre)
    "asos.com": function (html, fiche) {
      const prix = html.match(/"price":\{"current":\{"value":([\d.]+)/);
      if (prix && !fiche.prix) fiche.prix = formaterPrix(prix[1], "EUR");
    }
  };

  // ---------------------------------------------------------------------------------------------
  // Outils

  function sansAccents(texte) {
    return String(texte).normalize("NFD").replace(/[̀-ͯ]/g, "");
  }

  // Un texte comparable : sans accents ni majuscules, les apostrophes droites, le reste en espaces
  function normaliser(texte) {
    return " " + sansAccents(texte).toLowerCase().replace(/[’‘`]/g, "'").replace(/[^a-z0-9'\-]+/g, " ").replace(/\s+/g, " ").trim() + " ";
  }

  const ENTITES = { amp: "&", lt: "<", gt: ">", quot: "\"", apos: "'", nbsp: " ", ndash: "–", mdash: "-", rsquo: "’", lsquo: "‘", eacute: "é", egrave: "è", agrave: "à", ccedil: "ç" };
  function decoder(texte) {
    return String(texte).replace(/&(#x[0-9a-f]+|#\d+|[a-z]+);/gi, function (tout, code) {
      if (code[0] === "#") {
        const n = code[1] === "x" || code[1] === "X" ? parseInt(code.slice(2), 16) : parseInt(code.slice(1), 10);
        return isFinite(n) ? String.fromCodePoint(n) : tout;
      }
      return Object.prototype.hasOwnProperty.call(ENTITES, code.toLowerCase()) ? ENTITES[code.toLowerCase()] : tout;
    });
  }

  function texteDe(html) {
    if (!html) return "";
    return decoder(String(html).replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
  }

  function capturer(html, motif) {
    const m = html.match(motif);
    return m ? m[1] : "";
  }

  function liste(valeur) {
    if (valeur === undefined || valeur === null) return [];
    return Array.isArray(valeur) ? valeur : [valeur];
  }

  function chaine(valeur) {
    if (valeur === undefined || valeur === null) return "";
    if (typeof valeur === "string" || typeof valeur === "number") return decoder(String(valeur)).replace(/\s+/g, " ").trim();
    if (Array.isArray(valeur)) return chaine(valeur[0]);
    if (typeof valeur === "object") return chaine(valeur.name || valeur["@value"] || valeur.url || valeur.contentUrl || "");
    return "";
  }

  function typesDe(objet) {
    return liste(objet && objet["@type"]).map(function (t) { return String(t).replace(/^.*[/#]/, ""); });
  }

  function hoteDe(adresse) {
    try { return new URL(adresse).hostname.toLowerCase().replace(/^www\d?\./, ""); } catch (e) { return ""; }
  }

  // « zalando.fr », « asos.com » : le nom du site, sans son extension
  function nomDuSite(hote) {
    const morceaux = hote.split(".");
    return morceaux.length > 1 ? morceaux[morceaux.length - 2] : hote;
  }

  function absolue(adresse, base) {
    if (!adresse) return "";
    try {
      const url = new URL(decoder(String(adresse)).trim(), base);
      if (url.protocol === "http:") url.protocol = "https:";
      return url.protocol === "https:" ? url.toString() : "";
    } catch (e) {
      return "";
    }
  }

  // ---------------------------------------------------------------------------------------------
  // Lire la page

  // Les blocs de données de produit (JSON-LD) : chaque bloc illisible est ignoré
  function lireDonnees(html) {
    const blocs = [];
    const motif = /<script[^>]*type\s*=\s*["']?application\/ld\+json["']?[^>]*>([\s\S]*?)<\/script>/gi;
    let m;
    while ((m = motif.exec(html))) {
      const texte = m[1].trim().replace(/^<!\[CDATA\[|\]\]>$/g, "");
      try { blocs.push(JSON.parse(texte)); } catch (e) {
        try { blocs.push(JSON.parse(texte.replace(/[\u0000-\u001f]+/g, " "))); } catch (e2) { /* bloc ignoré */ }
      }
    }
    return blocs;
  }

  // Les produits déclarés, sans descendre dans les listes de produits voisins (« vous aimerez aussi »)
  function rassembler(objet, produits, ariane, profondeur) {
    if (!objet || typeof objet !== "object" || profondeur > 6) return;
    if (Array.isArray(objet)) { objet.forEach(function (o) { rassembler(o, produits, ariane, profondeur + 1); }); return; }
    const types = typesDe(objet);
    if (types.indexOf("Product") !== -1 || types.indexOf("ProductGroup") !== -1 || types.indexOf("Book") !== -1 || types.indexOf("IndividualProduct") !== -1) produits.push(objet);
    if (types.indexOf("BreadcrumbList") !== -1) ariane.push(objet);
    ["@graph", "mainEntity", "mainEntityOfPage", "workExample"].forEach(function (cle) {
      if (objet[cle] && typeof objet[cle] === "object") rassembler(objet[cle], produits, ariane, profondeur + 1);
    });
    if (objet.breadcrumb && typeof objet.breadcrumb === "object") rassembler(objet.breadcrumb, produits, ariane, profondeur + 1);
  }

  function lireBalises(html) {
    const balises = {};
    const motif = /<meta\b[^>]*>/gi;
    let m;
    while ((m = motif.exec(html))) {
      const balise = m[0];
      const nom = capturer(balise, /\b(?:property|name|itemprop)\s*=\s*["']([^"']+)["']/i).toLowerCase();
      const contenu = capturer(balise, /\bcontent\s*=\s*"([^"]*)"/i) || capturer(balise, /\bcontent\s*=\s*'([^']*)'/i);
      if (nom && contenu && !(nom in balises)) balises[nom] = decoder(contenu).trim();
    }
    return balises;
  }

  // Le chemin d'une adresse, pour reconnaître le produit du lien parmi ceux de la page
  function chemin(adresse, base) {
    try { const u = new URL(adresse, base); return (u.hostname.replace(/^www\./, "") + u.pathname).replace(/\/+$/, "").toLowerCase(); } catch (e) { return ""; }
  }

  function choisirProduit(produits, lien) {
    if (!produits.length) return null;
    const cible = chemin(lien);
    const avecAdresse = produits.find(function (p) {
      return [p.url, p["@id"]].concat(liste(p.offers).map(function (o) { return o && o.url; })).some(function (a) {
        return a && typeof a === "string" && chemin(a, lien) === cible;
      });
    });
    return avecAdresse || produits[0];
  }

  // Le prix d'une offre, et l'offre de la variante du lien quand il y en a une (« ?variant=… »)
  function choisirOffre(offres, lien) {
    const toutes = [];
    liste(offres).forEach(function (o) {
      if (!o || typeof o !== "object") return;
      if (Array.isArray(o.offers)) o.offers.forEach(function (x) { toutes.push(x); });
      toutes.push(o);
    });
    let variante = "";
    try { const u = new URL(lien); variante = u.searchParams.get("variant") || u.searchParams.get("v1") || u.searchParams.get("option") || ""; } catch (e) { /* lien sans paramètres */ }
    const avecPrix = toutes.filter(function (o) { return o.price !== undefined || o.lowPrice !== undefined || (o.priceSpecification && o.priceSpecification.price !== undefined); });
    if (variante) {
      const exacte = avecPrix.find(function (o) { return (o.url && String(o.url).indexOf(variante) !== -1) || String(o.sku || "") === variante; });
      if (exacte) return exacte;
    }
    return avecPrix[0] || null;
  }

  function lirePrix(offre) {
    if (!offre) return null;
    let montant = offre.price !== undefined ? offre.price : offre.lowPrice;
    let devise = offre.priceCurrency;
    const spec = liste(offre.priceSpecification)[0];
    if (montant === undefined && spec) { montant = spec.price; devise = devise || spec.priceCurrency; }
    return montant === undefined ? null : { montant: montant, devise: devise || "" };
  }

  // « 29.9 EUR » devient « 29,90 € », « 1095 » devient « 1 095 € » ; une autre devise reste écrite telle quelle
  function formaterPrix(montant, devise) {
    const n = typeof montant === "number" ? montant : parseFloat(String(montant).replace(/\s/g, "").replace(",", "."));
    if (!isFinite(n) || n <= 0) return "";
    const entier = Math.floor(n), centimes = Math.round((n - entier) * 100);
    const euros = String(entier).replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    const chiffre = centimes ? euros + "," + String(centimes).padStart(2, "0") : euros;
    const code = String(devise || "EUR").toUpperCase();
    return code === "EUR" ? chiffre + " €" : chiffre + " " + code;
  }

  function lireImage(valeur, base) {
    for (const v of liste(valeur)) {
      const adresse = typeof v === "string" ? v : v && (v.url || v.contentUrl || v["@id"]);
      const propre = absolue(adresse, base);
      if (propre) return propre;
    }
    return "";
  }

  function lireMarque(valeur) {
    for (const v of liste(valeur)) {
      const nom = typeof v === "string" ? v : v && typeof v === "object" ? v.name : "";
      if (nom && String(nom).trim()) return chaine(nom);
    }
    return "";
  }

  // Le titre de la page, sans le nom du site qui le suit ou le précède
  // Les morceaux retirés : le nom du site (« | ZARA France », « ≡ SEPHORA ») et la marque, déjà dans son champ
  function nettoyerTitre(titre, noms) {
    let t = titre.replace(/\s+/g, " ").trim();
    t = t.replace(/^Amazon\.[a-z.]+\s*[-:|]\s*/i, "").replace(/\s*:\s*Amazon\.[a-z.]+\s*:.*$/i, "");
    const aRetirer = noms.filter(Boolean).map(function (n) { return normaliser(n).replace(/ /g, ""); });
    const retirable = function (morceau) {
      const m = normaliser(morceau).replace(/ /g, "");
      return aRetirer.some(function (n) { return m === n || (n.length > 3 && m.indexOf(n) === 0 && m.length - n.length <= 8); });
    };
    let morceaux = t.split(/\s+[|–—≡-]\s+/);
    while (morceaux.length > 1 && retirable(morceaux[morceaux.length - 1])) morceaux.pop();
    while (morceaux.length > 1 && retirable(morceaux[0])) morceaux.shift();
    return morceaux.join(" - ").trim();
  }

  // La catégorie : on cherche dans chaque texte, du plus sûr au moins sûr (la catégorie déclarée, le fil
  // d'Ariane, le nom, le titre de partage), et le premier qui répond décide
  function trouverCategorie(textes) {
    for (const texte of textes) {
      if (!texte) continue;
      const t = normaliser(texte);
      let meilleure = null, longueur = 0;
      CATEGORIES.forEach(function (categorie) {
        categorie.mots.forEach(function (mot) {
          const m = normaliser(mot).trim();
          const motif = new RegExp(" " + m.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "(s|x|es)? ");
          if (m.length > longueur && motif.test(t)) { meilleure = categorie; longueur = m.length; }
        });
      });
      if (meilleure) return meilleure;
    }
    return null;
  }

  // ---------------------------------------------------------------------------------------------
  // La fiche

  function lireProduit(html, lien) {
    html = String(html || "");
    const base = lien;
    const hote = hoteDe(lien);
    const site = nomDuSite(hote);
    const plateforme = PLATEFORMES.indexOf(site) !== -1;
    const balises = lireBalises(html);

    const produits = [], ariane = [];
    lireDonnees(html).forEach(function (bloc) { rassembler(bloc, produits, ariane, 0); });
    let produit = choisirProduit(produits, lien);

    // Une fiche générale et ses variantes : la marque est sur l'une, le prix et la photo sur l'autre
    let groupe = null, variantes = [];
    if (produit) {
      if (typesDe(produit).indexOf("ProductGroup") !== -1 || Array.isArray(produit.hasVariant)) {
        groupe = produit;
        variantes = liste(produit.hasVariant).filter(function (v) { return v && typeof v === "object"; });
      } else if (produit.isVariantOf && typeof produit.isVariantOf === "object") {
        groupe = produit.isVariantOf;
      }
      // Des variantes déclarées à part, au même nom (Shopify)
      const nomGroupe = normaliser(chaine(produit.name));
      produits.forEach(function (p) {
        if (p !== produit && normaliser(chaine(p.name)).indexOf(nomGroupe.trim()) === 1) variantes.push(p);
      });
    }
    let variante = null;
    if (variantes.length) {
      let id = "";
      try { id = new URL(lien).searchParams.get("variant") || ""; } catch (e) { /* sans paramètre */ }
      variante = variantes.find(function (v) { return id && JSON.stringify(v).indexOf(id) !== -1; }) || variantes[0];
    }
    const sources = [variante, produit, groupe].filter(Boolean);
    const premier = function (lecture) {
      for (const s of sources) { const v = lecture(s); if (v) return v; }
      return "";
    };

    const titreSite = balises["og:site_name"] || "";
    const titrePage = texteDe(capturer(html, /<title[^>]*>([\s\S]*?)<\/title>/i));
    const fiche = { lien: lien, nom: "", marque: "", prix: "", image: "", categorie: "", meuble: "", complet: false };

    // Le nom : celui du produit, sinon le titre de partage, sinon le titre de la page
    fiche.nom = chaine(produit && produit.name) || chaine(groupe && groupe.name);
    const nomDuTitre = !fiche.nom;

    // La marque : celle du produit ; l'auteur pour un livre ; le nom du site seulement sur le site d'une marque
    fiche.marque = premier(function (s) { return lireMarque(s.brand); }) || chaine(balises["product:brand"]);
    // Les données de produit écrites dans la page elle-même (microdonnées, itemprop) : Sephora (19 novembre)
    if (!fiche.marque) {
      const bloc = html.match(/itemprop=["']brand["'][\s\S]{0,800}?itemprop=["']name["'](?:[^>]*content=["']([^"']+)["']|[^>]*>([^<]+)<)/i);
      if (bloc) fiche.marque = decoder(bloc[1] || bloc[2] || "").trim();
    }
    const estLivre = produits.some(function (p) { return typesDe(p).indexOf("Book") !== -1; });
    const auteur = premier(function (s) { return lireMarque(s.author); });
    if (!fiche.marque && !plateforme && titreSite) fiche.marque = titreSite;
    if (fiche.marque) {
      const m = normaliser(fiche.marque).replace(/ /g, "");
      if (plateforme && (m === site.replace(/-/g, "") || m === normaliser(titreSite).replace(/ /g, ""))) fiche.marque = "";
    }

    // Le prix
    const offre = choisirOffre([].concat(variante ? liste(variante.offers) : [], produit ? liste(produit.offers) : [], groupe ? liste(groupe.offers) : []), lien);
    const prix = lirePrix(offre);
    if (prix) fiche.prix = formaterPrix(prix.montant, prix.devise);
    if (!fiche.prix && balises["product:price:amount"]) fiche.prix = formaterPrix(balises["product:price:amount"], balises["product:price:currency"] || balises["og:price:currency"]);
    if (!fiche.prix && balises["price"]) fiche.prix = formaterPrix(balises["price"], balises["pricecurrency"]);

    // Sans données de produit, le nom vient du titre de partage ou de la page, sans le site ni la marque
    if (nomDuTitre) {
      const noms = [titreSite, site, fiche.marque];
      fiche.nom = nettoyerTitre(balises["og:title"] || "", noms) || nettoyerTitre(titrePage, noms);
    }

    // La photo
    fiche.image = premier(function (s) { return lireImage(s.image, base); }) || absolue(balises["og:image"] || balises["og:image:secure_url"] || balises["twitter:image"], base);

    // Les corrections propres au site
    const regle = REGLES_SITES[hote] || REGLES_SITES[hote.split(".").slice(-2).join(".")];
    if (regle) regle(html, fiche);

    // La catégorie, puis le meuble
    const filAriane = ariane.map(function (a) {
      return liste(a.itemListElement).map(function (e) { return chaine(e && (e.name || (e.item && e.item.name))); }).reverse().join(" / ");
    }).join(" / ");
    const declaree = premier(function (s) { return chaine(s.category); });
    const categorie = estLivre ? CATEGORIES[1] : trouverCategorie([declaree, filAriane, fiche.nom, balises["og:title"], titrePage, balises["description"]]);
    if (categorie) { fiche.categorie = categorie.cle; fiche.meuble = categorie.meuble; }
    else { fiche.categorie = "autre"; fiche.meuble = "coffre"; }
    if (fiche.categorie === "livres" && auteur) fiche.marque = auteur;

    fiche.complet = Boolean(fiche.nom && fiche.marque && fiche.prix && fiche.image);
    // Une page sans produit (une liste, un article retiré qui renvoie ailleurs) ne donne pas de fiche
    if (!fiche.nom || (!produit && !fiche.prix && !fiche.image)) return null;
    // Ni produit déclaré ni prix, sur une page qui ne se dit pas produit : une liste dont l'image de
    // partage est le logo du site (Zara, « Vestes pour femme », 19 novembre 2026)
    if (!produit && !fiche.prix && !/product|book/i.test(balises["og:type"] || "")) return null;
    return fiche;
  }

  const api = { lireProduit: lireProduit, formaterPrix: formaterPrix, trouverCategorie: trouverCategorie, CATEGORIES: CATEGORIES, PLATEFORMES: PLATEFORMES };
  racine.TinyMoteur = api;
  if (typeof module === "object" && module.exports) module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
