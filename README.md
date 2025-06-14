### Script python pour comparer les baromètres de la FUB 2019/2021 et 2021/2025

Installation des dépendances en utilisant `uv` (https://docs.astral.sh/uv/#installation)

```
git clone https://github.com/CyclisteBx/comparaison_barometre_FUB.git
uv sync
```

Données volumineuses à télécharger et à placer dans le dossier data/
- Contours des communes issues de OpenStreetMap (https://www.data.gouv.fr/fr/datasets/decoupage-administratif-communal-francais-issu-d-openstreetmap/): https://www.data.gouv.fr/fr/datasets/decoupage-administratif-communal-francais-issu-d-openstreetmap/#/resources/17062524-991f-4e13-9bf0-b410cc2216fd
- mettre à jour les données de 2025:
```
curl 'https://www.barometre-velo.fr/stats/progress.geojson' > data/barometre2025.json
```



Scripts:
- barometre_dep_2021.py: calcule les evolutions et génère les cartes sauvegardées dans le dossier png, créé un tweet par département
- barometre_dep_2025.py: calcule les evolutions et génère les cartes sauvegardées dans le dossier png, créé un tweet par département. Prends en compte le nouveau critère de qualification (pop <5000 & reponse > 30) pour 2025.

Sorties:
- dossier png/: une image par département + une image de la France Métropolitaine
- dossier output/:
  * commune_qualif.csv: fichier recapitulatif des évolutions absolues et relative par département
  * tweets.txt: fichier recapitulatif des tweets par département
