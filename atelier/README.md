# Atelier

Les outils qui fabriquent la maquette de Tiny Studio. Ce dossier ne se publie pas.

- `genere_piece.py` pose le socle, le sol et l'épaisseur des murs, puis insère la pièce dans `index.html`, entre les marqueurs `<!-- PIECE -->` et `<!-- /PIECE -->`.
- `zen_illustre.py` dessine la pièce elle-même : les murs, les cinq meubles de la wishlist, le fauteuil, la table d'appoint et la déco. Seuls les choix retenus y sont ; les variantes essayées restent dans l'historique Git.

Pour retoucher la pièce, on modifie ces scripts puis on relance, depuis `maquette/` :

```
python3 atelier/genere_piece.py index.html
```
