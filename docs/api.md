# API de Tiny Studio

Le contrat de l'API du remplissage automatique (issue n° 6), rédigé au format de la séance 6 du cours « Vibe-Coding : IA & Dev » : endpoints, codes HTTP, exemples JSON, autorisations, validations, sécurité et tests prioritaires. Brouillon du 20 octobre 2026, à relire avec le formateur.

## Le besoin

Ranger un article en collant seulement le lien du produit : l'app demande à une petite fonction côté serveur de lire la page, et remplit le nom, la marque, le prix et la photo, puis propose le meuble. Une page web ne peut pas lire elle-même un autre site (le navigateur l'en empêche), d'où ce passage par le serveur.

Tiny Studio n'a ni comptes ni base de données : les articles restent dans le navigateur. L'API ne stocke rien.

## Où elle vit

Une fonction Cloudflare Pages (`functions/api/produit.js` dans le dépôt), servie à la même adresse que l'app : `https://tiny-studio-b9f.pages.dev/api/produit`.

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
  "meuble": "dressing",
  "complet": true
}
```

`complet` vaut `false` si le nom, la marque, le prix ou la photo manque. L'app remplit ce qu'elle a et laisse les autres champs à compléter.

### Comment la fonction lit la page

Dans l'ordre, la première source qui répond gagne, champ par champ :
1. **Les données de produit** que les boutiques déclarent pour Google (JSON-LD, type `Product`) : `name`, `brand.name`, `offers.price` et `offers.priceCurrency`, `image`.
2. **Les balises de partage** (Open Graph) : `og:title`, `og:image`, `product:price:amount`, `og:site_name` pour la marque.
3. **Le titre de la page** pour le nom, en dernier recours.

Le prix est rendu au format de l'app (« 29,90 € ») ; une autre devise est indiquée telle quelle.

### Le meuble proposé

D'après la catégorie déclarée par la boutique, puis les mots du nom :
- vêtements, chaussures, sacs, accessoires de mode : `dressing`
- livres, BD, carnets, agendas, papeterie : `bibliotheque`
- bougies, vases, cadres, objets déco : `deco`
- beauté, parfum, maquillage, soins : `coiffeuse`
- sinon : `coffre`

L'app le propose dans « Ranger dans » ; on peut toujours le changer.

## Endpoint 2 (facultatif, à discuter) : rapatrier une photo

`GET /api/photo?adresse=<adresse de l'image, encodée>`

Renvoie l'image elle-même, depuis l'adresse de l'app. Intérêt : les règles de mise en forme des photos (couleur du fond, recadrage) ne marchent aujourd'hui que si le site de la photo permet de la lire ; en passant par l'app, elles marcheraient pour toutes.

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

## Ce que l'API ne fait pas

- Contourner les sites qui bloquent la lecture : ils passent par la saisie à la main (le favori « Ranger dans Tiny Studio » et l'app iPhone pourront les lire depuis la page ouverte).
- Stocker quoi que ce soit.
- Suivre l'évolution des prix.
