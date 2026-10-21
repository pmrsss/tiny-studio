# Atelier

Les outils qui fabriquent la maquette de Tiny Studio. Ce dossier ne se publie pas.

- `genere_piece.py` pose le socle, le sol et l'épaisseur des murs, puis insère la pièce dans `index.html`, entre les marqueurs `<!-- PIECE -->` et `<!-- /PIECE -->`.
- `piece_par_defaut.py` dessine la pièce elle-même, dans sa version par défaut : les murs, les cinq meubles de la wishlist, le fauteuil, la table d'appoint et la déco. Seuls les choix retenus y sont ; les variantes essayées restent dans l'historique Git.

- `immeuble.py` dessine l'immeuble de la porte d'entrée, sur téléphone : le studio fermé, vu de dehors, au même repère que la pièce. Il l'insère dans `index.html`, entre les marqueurs `<!-- IMMEUBLE -->` et `<!-- /IMMEUBLE -->` (issue n° 7).

Pour retoucher la pièce ou l'immeuble, on modifie ces scripts puis on relance, depuis `maquette/` :

```
python3 atelier/genere_piece.py index.html
python3 atelier/immeuble.py index.html
```
