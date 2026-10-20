# Tiny Studio

Une pièce à vivre illustrée où l'on range les articles repérés en ligne : les livres dans la bibliothèque, les vêtements dans le dressing, la déco sur la commode, les produits de beauté dans la coiffeuse, et tout le reste dans le coffre fourre-tout.

**En ligne :** https://tiny-studio-b9f.pages.dev

## Pour qui ?
Pour moi d'abord, et pour toutes les personnes qui repèrent des articles sur plein de sites différents et finissent par les perdre.

## Le problème ou besoin
Les articles repérés s'éparpillent : favoris propres à chaque site, captures d'écran, onglets ouverts, paniers abandonnés. On ne les retrouve plus, ou on achète sur un coup de tête.

Le projet veut offrir un endroit à soi, joli et un peu ludique, où l'on range ses trouvailles comme on aménage un intérieur.

## MVP
La première version permet de :
- Parcourir son studio : une pièce illustrée avec cinq meubles cliquables, le dressing, la bibliothèque, la commode déco, la coiffeuse et le coffre fourre-tout. Un clic sur un meuble ouvre un panneau avec les articles qu'on y a rangés
- Ranger un article : l'ajouter à la main, avec son lien, son nom, sa marque, son prix et sa photo, dans le meuble choisi
- Retrouver et mettre à jour ses articles : ils restent enregistrés d'une visite à l'autre ; on peut les déplacer, les retirer et cocher « Acheté »

## Comment c'est construit
- HTML, CSS et JavaScript, sans framework
- Les articles sont enregistrés dans le navigateur (localStorage), les photos par leur adresse
- `site/` : l'app, publiée par Cloudflare Pages à chaque push sur `main`
- `atelier/` : les scripts Python qui dessinent la pièce en SVG

## Et ensuite
- Modifier un article déjà rangé (#5)
- Remplir un article à partir de son seul lien
- Un favori « Ranger dans Tiny Studio » pour le navigateur
- Plus tard : une app iPhone, avec le partage depuis Safari

## Hors périmètre pour le moment
- L'extension de navigateur
- Retrouver sa collection sur plusieurs appareils
- Le suivi automatique des prix
- La boutique : des meubles, des papiers peints, des sols et un compagnon pour personnaliser son studio

## État du projet
- [x] Idée cadrée
- [x] MVP défini
- [x] Première version construite
- [x] Testée avec une ou plusieurs personnes
- [ ] Améliorée
