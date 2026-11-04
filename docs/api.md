# API de Tiny Studio

Le contrat de l'API du remplissage automatique (issue n° 6), rédigé au format de la séance 6 du cours « Vibe-Coding : IA & Dev » : endpoints, codes HTTP, exemples JSON, autorisations, validations, sécurité et tests prioritaires. Brouillon du 20 octobre 2026, complété le 4 novembre 2026 après l'échange avec le formateur sur le « petit moteur » : les catégories d'objets, la base de liens et la mise au point avec l'IA. À relire avec le formateur.

## Le besoin

Ranger un article en collant seulement le lien du produit : l'application demande à une petite fonction côté serveur de lire la page, et remplit le nom, la marque, le prix et la photo, puis propose le meuble. Une page web ne peut pas lire elle-même un autre site (le navigateur l'en empêche), d'où ce passage par le serveur.

Tiny Studio n'a ni comptes ni base de données : les articles restent dans le navigateur. L'API ne stocke rien.

## Où elle vit

Une fonction Cloudflare Pages (`functions/api/produit.js` dans le dépôt), servie à la même adresse que l'application : `https://tiny-studio-b9f.pages.dev/api/produit`.

## Endpoint 1 : lire un produit

`GET /api/produit?lien=<adresse de la page, encodée>`

### Paramètres

| Nom | Où | Obligatoire | Règle |
|---|---|---|---|
| `lien` | requête | oui | une adresse `https://` (ou `http://`) complète, 2 048 caractères au plus |

### Réponses

| Code | Quand | Corps |
|---|---|---|
| 200 | La page a été lue, au moins le nom ou la photo trouvés | la fiche du produit, les champs non trouvés à `null` |
| 400 | `lien` manquant, trop long, pas une adresse web, ou adresse interdite (voir Sécurité) | `{ "erreur": "lien-invalide", "message": "…" }` |
| 405 | Une autre méthode que `GET` | `{ "erreur": "methode-non-permise" }` |
| 422 | La page a été lue, mais on n'y trouve aucune information de produit | `{ "erreur": "rien-trouve", "message": "…" }` |
| 429 | Trop de demandes depuis la même adresse | `{ "erreur": "trop-de-demandes", "message": "…" }` |
| 502 | Le site refuse d'être lu (403, page anti-robot) ou répond en erreur | `{ "erreur": "site-refuse", "message": "…" }` |
| 504 | Le site met trop de temps à répondre | `{ "erreur": "delai-depasse", "message": "…" }` |

Les messages sont écrits pour l'utilisateur, sans détail technique. Exemples :
- 400 : « Ce lien ne fonctionne pas : il doit commencer par https:// »
- 422 : « Je n'ai pas trouvé d'informations sur cette page. Remplis l'article à la main. »
- 502 : « Ce site ne se laisse pas lire. Remplis l'article à la main. »

### Exemple

Requête :

```
GET /api/produit?lien=https%3A%2F%2Fwww.ganni.com%2Ffr-fr%2Fgrand-sac-kat-fausse-fourrure-A6997.html
```

Réponse `200` :

```json
{
  "lien": "https://www.ganni.com/fr-fr/grand-sac-kat-fausse-fourrure-A6997.html",
  "nom": "Grand sac Kat en fausse fourrure",
  "marque": "Ganni",
  "prix": "1 095 €",
  "image": "https://www.ganni.com/…/A6997.jpg",
  "categorie": "sacs",
  "meuble": "dressing",
  "complet": true
}
```

`complet` vaut `false` si le nom, la marque, le prix ou la photo manque. L'application remplit ce qu'elle a et laisse les autres champs à compléter.

### Comment la fonction lit la page

Dans l'ordre, la première source qui répond gagne, champ par champ :
1. **Une règle propre au site**, seulement si la mise au point en a écrit une (voir plus bas). C'est rare : uniquement quand les sources générales se trompent sur un site qui compte.
2. **Les données de produit** que les boutiques déclarent pour Google (JSON-LD, type `Product`) : `name`, `brand.name`, `offers.price` et `offers.priceCurrency`, `image`, `category`.
3. **Les balises de partage** (Open Graph) : `og:title`, `og:image`, `product:price:amount`, `product:brand` pour la marque.
4. **Le titre de la page** pour le nom, en dernier recours.

Le prix est rendu au format de l'application (« 29,90 € ») ; une autre devise est indiquée telle quelle.

**La marque, pas le site.** Sur une marketplace ou un grand magasin en ligne (Vinted, ASOS, Zalando, La Redoute, Veepee, Place des Tendances, Galeries Lafayette, Amazon…), le nom du site n'est pas la marque du produit : une paire de Nike achetée sur ASOS doit être rangée sous « Nike ». D'où trois règles :
- **La marque vient du produit lui-même** : `brand.name` du JSON-LD, puis `product:brand`, puis le champ « Marque » de l'annonce quand la plateforme en affiche un (Vinted).
- **Le nom du site (`og:site_name`) ne sert de marque que sur le site d'une marque** (Ganni, Sézane…). La fonction tient une liste des plateformes multimarques, où il n'est jamais utilisé.
- **Une marque égale au nom de la plateforme est écartée** : la marque reste vide, `complet` passe à `false` et l'utilisateur la complète. Exception : les produits de la marque propre d'une plateforme (« ASOS DESIGN ») gardent leur marque.

Sur certaines plateformes, la marque n'apparaît qu'au début du nom (« Nike - Baskets Air Max ») : c'est le cas typique d'une règle propre à un site, écrite si la base de liens le montre. La liste des plateformes s'allonge avec la base de liens.

**Le bon produit, pas ses voisins.** Une page de produit en montre souvent d'autres : « vous aimerez aussi », « complétez le look ». Quand la page déclare plusieurs produits, la fonction garde celui dont l'adresse correspond au lien, sinon le premier. La base de liens vérifie ce point.

### Les catégories d'objets et le meuble proposé

La fonction range d'abord le produit dans une catégorie, puis la catégorie donne le meuble. Elle cherche la catégorie dans cet ordre : la catégorie déclarée par la boutique (`category` du JSON-LD, ou le fil d'Ariane de la page), puis les mots du nom du produit. Les mots se comparent sans accents ni majuscules.

Validées par Pauline le 4 novembre 2026 :

| Catégorie | Meuble | Exemples de mots |
|---|---|---|
| `vetements` | `dressing` | robe, jupe, pull, gilet, chemise, t-shirt, jean, pantalon, manteau, veste |
| `chaussures` | `dressing` | chaussures, bottes, bottines, baskets, sandales, escarpins, mocassins |
| `sacs` | `dressing` | sac, cabas, pochette, besace, sac à dos |
| `accessoires` | `dressing` | bijoux, collier, boucles d'oreilles, bague, montre, ceinture, écharpe, bonnet, lunettes de soleil, lunettes de vue |
| `livres` | `bibliotheque` | livre, roman, BD, manga, album, beau livre |
| `papeterie` | `bibliotheque` | carnet, agenda, cahier, stylo, papeterie |
| `deco` | `deco` | bougie, vase, cadre, affiche, coussin, plaid, miroir, lampe |
| `maquillage` | `coiffeuse` | rouge à lèvres, mascara, fond de teint, fard, palette, vernis |
| `soins-parfums` | `coiffeuse` | crème, sérum, soin, parfum, eau de toilette, shampooing |
| `autre` | `coffre` | l'ameublement (chaise, table, étagère, canapé, lit), le matériel de sport (tapis de yoga, haltères, raquette, vélo), et tout le reste |

La lampe et le miroir sont de la déco, mais un meuble va dans le coffre. Les tenues de sport (legging, brassière, baskets de running) restent au dressing, seul le matériel va dans le coffre. Les listes de mots vivent dans le code et s'affinent avec la base de liens. L'application propose le meuble dans « Ranger dans » ; on peut toujours le changer.

## La base de liens

Une liste de vrais liens de produits, chacun avec ce que la fonction doit y trouver. Elle sert à mesurer le moteur et à l'affiner. C'est un fichier du dépôt, `tests/liens.json`, jamais envoyé à l'application : l'API continue de ne rien stocker.

- **Qui la remplit :** Pauline, avec 30 à 50 liens pris sur les sites où elle achète vraiment.
- **Ce qu'elle couvre :** au moins trois liens par catégorie, plusieurs sites par catégorie, des sites de marque comme des plateformes multimarques (au moins cinq liens de marketplaces, dont Vinted et ASOS, pour des marques différentes), et quelques sites qui bloquent la lecture, pour vérifier le message d'erreur.
- **Ce qu'on note pour chaque lien :** le nom, la marque, la présence d'un prix, la catégorie et le meuble attendus, relevés à la main sur la page.

Exemple d'entrée :

```json
{
  "lien": "https://www.ganni.com/fr-fr/grand-sac-kat-fausse-fourrure-A6997.html",
  "attendu": {
    "nom": "Grand sac Kat en fausse fourrure",
    "marque": "Ganni",
    "prix": true,
    "photo": true,
    "categorie": "sacs",
    "meuble": "dressing"
  }
}
```

Le prix se vérifie présent ou absent, pas au centime près, puisqu'il change. Un lien mort se remplace par un autre du même site.

## La mise au point

L'IA n'intervient qu'ici, pendant le développement : Claude, l'assistant de code, sert à affiner le moteur. **Dans l'application, la fonction n'utilise aucune IA.** Elle suit des règles écrites, ce qui la garde gratuite, rapide et sans clé.

1. **Passer la base :** un script, `tests/passer-la-base.js`, envoie chaque lien à la fonction déployée sur une branche de test, compare la réponse à l'attendu et donne un taux de réussite par champ.
2. **Lire les échecs :** pour chaque lien raté, Claude lit la page, repère où se trouvent le nom, le prix, la photo ou la catégorie, et comprend pourquoi la fonction les a manqués.
3. **Corriger la règle :** de préférence une règle générale (un nouveau mot de catégorie, une autre balise), une règle propre à un site seulement si plusieurs de ses liens échouent.
4. **Repasser toute la base**, pour vérifier que la correction n'a rien cassé ailleurs.

La base passe par la fonction elle-même, et pas par le navigateur de Claude : un site qui se laisse lire dans un navigateur peut refuser la fonction, et c'est ce que l'application vivra.

Seuils proposés, à discuter : sur les sites qui se laissent lire, le nom et la photo justes pour 8 liens sur 10, le meuble juste pour 9 liens sur 10, et aucun nom de plateforme rendu comme marque.

## Endpoint 2 (facultatif, à discuter) : rapatrier une photo

`GET /api/photo?adresse=<adresse de l'image, encodée>`

Renvoie l'image elle-même, depuis l'adresse de l'application. Intérêt : les règles de mise en forme des photos (couleur du fond, recadrage) ne marchent aujourd'hui que si le site de la photo permet de la lire ; en passant par l'application, elles marcheraient pour toutes.

| Code | Quand |
|---|---|
| 200 | L'image, avec son type (`image/jpeg`, `image/png`, `image/webp`) |
| 400 | Adresse invalide ou interdite |
| 413 | Image de plus de 5 Mo |
| 415 | Ce n'est pas une image |
| 502 / 504 | Site qui refuse, délai dépassé |

## Autorisations

Pas de comptes dans Tiny Studio : l'API est ouverte à tous, en lecture seule. Elle ne crée, ne modifie et ne supprime rien. Les garde-fous de la section suivante remplacent les autorisations.

## Sécurité

Une fonction qui va lire l'adresse qu'on lui donne peut être détournée (on parle de SSRF) : pour viser des adresses internes, ou pour se servir d'elle comme relais vers d'autres sites. Les garde-fous :
- **Adresses** : `https://` et `http://` seulement ; refus de `localhost`, des adresses IP privées ou réservées (10.x, 172.16-31.x, 192.168.x, 127.x, 169.254.x, ::1…) et des adresses IP écrites en chiffres.
- **Redirections** : trois au plus, chacune revérifiée avec les mêmes règles.
- **Délai** : 8 secondes au plus pour la page, sinon 504.
- **Taille** : on ne lit que les 2 premiers Mo de la page (5 Mo pour une photo).
- **Type** : la page doit être du HTML (`text/html`), la photo une image.
- **Nombre de demandes** : 30 par minute et par adresse au plus, sinon 429.
- **Journalisation** : on note le nom du site et le code de réponse, jamais l'adresse complète ni l'adresse IP du visiteur.
- **Erreurs** : des messages simples, sans détail technique ni trace d'erreur.
- **Aucun secret** : la fonction n'utilise ni clé ni mot de passe.

## Tests prioritaires

1. Sans `lien` : 400.
2. `lien=http://localhost/` ou une adresse IP privée : 400.
3. Une page de produit qui déclare ses données (JSON-LD) : 200, avec le nom, la marque, le prix et la photo.
4. Une page avec seulement des balises de partage (Open Graph) : 200, `complet` à `false` s'il manque le prix.
5. Un site qui répond 403 (H&M, COS ou Fnac au 19 octobre 2026) : 502 et le message « Ce site ne se laisse pas lire ».
6. Une page sans aucune information de produit : 422.
7. Un site qui ne répond pas : 504 après 8 secondes.
8. La 31e demande en une minute depuis la même adresse : 429.
9. Une page qui montre aussi des produits suggérés : la fiche rendue est celle du produit du lien.
10. Un produit d'une marque vendu sur une marketplace (des baskets Nike sur ASOS, un sac d'occasion sur Vinted) : la marque rendue est celle du produit, jamais le nom de la plateforme.
11. Toute la base de liens : les seuils de la mise au point sont atteints.

## Ce que l'API ne fait pas

- Contourner les sites qui bloquent la lecture : ils passent par la saisie à la main (le favori « Ranger dans Tiny Studio » et l'application iPhone pourront les lire depuis la page ouverte).
- Utiliser une IA pour lire les pages : l'IA sert seulement à la mise au point.
- Stocker quoi que ce soit.
- Suivre l'évolution des prix.
