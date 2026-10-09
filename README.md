# Sujet 3 — Vérification d'ordonnance par graphe et règles

Mini-projet IA hybride — ISIS Castres, 5e année DSIA.

Pour une ordonnance (liste de médicaments), le système signale les associations à risque, les classe par gravité (échelle du Thésaurus ANSM) et explique chaque alerte : règle déclenchée, source, et chemin dans le graphe Hetionet ou ligne de la table ATC.

```
$ python src/verifier.py warfarine ibuprofène oméprazole
[Association déconseillée] warfarine + ibuprofène
   • R01 (Association déconseillée) — majoration du risque hémorragique
       Warfarin ←[PCiC]— « Vitamin K Inhibitors » ⇒ antivitamines K
       Ibuprofen ←[PCiC]— « Nonsteroidal Anti-inflammatory Compounds » ⇒ anti-inflammatoires non stéroïdiens
       Source : ANSM, Thésaurus des interactions médicamenteuses : AVK + AINS
...
```

## Résultats principaux (20 ordonnances, 26 paires à risque attendues)

| Système | Précision | Rappel | F1 | Alertes / ordonnance |
|---|---|---|---|---|
| **Hybride (graphe + règles), mode concis** | 0,91 | 0,77 | **0,83** | 1,10 |
| Hybride sans filtre anti-fatigue | 0,35 | 0,92 | 0,51 | 3,45 |
| Graphe seul (règles génériques G1-G3) | 0,83 | 0,19 | 0,31 | 0,30 |
| Référence non hybride : liste de paires | 1,00 | 0,42 | 0,60 | 0,55 |

Sur 5 ordonnances de généralisation (médicaments absents de la table du groupe) : hybride 5/5, table seule 0/5, liste de paires 0/5.

## Structure

```
projet/
├── README.md
├── requirements.txt
├── src/
│   ├── graphe.py            chargement de Hetionet, sous-graphe, accès par médicament
│   ├── connaissances.py     synonymes, table ATC, effets graves, marge thérapeutique étroite
│   ├── regles.py            18 règles expertes + 3 règles du graphe, moteur d'alertes
│   ├── evaluation.py        métriques, référence, ablation, erreurs, robustesse, généralisation
│   ├── problog_regles.py    bonus : règles pondérées en ProbLog
│   ├── reference_llm.py     2e référence optionnelle : LLM local sans graphe (Ollama)
│   └── verifier.py          vérification en ligne de commande
├── notebooks/
│   ├── 01_exploration_hetionet.ipynb
│   ├── 02_regles_et_alertes.ipynb
│   ├── 03_evaluation.ipynb
│   └── 04_bonus_problog.ipynb
├── donnees/
│   ├── ordonnances.json                 20 ordonnances de test
│   ├── verite_terrain.csv               26 alertes attendues, niveau et source
│   ├── ordonnances_generalisation.json  5 ordonnances de généralisation
│   ├── verite_generalisation.csv
│   ├── liste_paires_reference.csv       24 paires pour la référence non hybride
│   └── sources.md                       sources et points à vérifier
└── data/                    fichiers Hetionet v1.0 (fournis ; retéléchargés s'ils manquent)
```

## Réexécuter

1. Python 3.10 ou plus, puis `pip install -r requirements.txt`
2. Exécuter les notebooks dans l'ordre (01 → 04). Les fichiers Hetionet sont dans `data/` ; s'ils manquent, `src/graphe.py` les télécharge.
3. En ligne de commande : `python src/verifier.py <médicament> <médicament> ...` (ajouter `--complet` pour voir les signaux faibles).

**Sur Google Colab** : ouvrir un notebook, importer `sujet3_projet.zip` dans le panneau Fichiers, puis exécuter dans une cellule `!unzip -q sujet3_projet.zip` (et `!pip install problog` pour le notebook 4). Les notebooks trouvent seuls le dossier `projet/src/`.

**Référence LLM (optionnelle)** : installer Ollama, `ollama pull llama3.2:3b`, lancer `ollama serve`, puis réexécuter la dernière cellule du notebook 3.

## Données et sources

Hetionet v1.0 (CC0), Thésaurus ANSM des interactions médicamenteuses, index ATC de l'OMS, RCP. Détail et points à vérifier : `donnees/sources.md`.

## Limites connues

- Vérité terrain construite par le groupe à partir du Thésaurus : 5 niveaux sont à vérifier sur la version en vigueur.
- Le filtre « marge étroite » de la règle G1 a été ajouté après l'analyse d'erreurs sur le jeu de test : risque de sur-ajustement, à confirmer sur d'autres ordonnances.
- Le graphe ne connaît ni les doses (aspirine antiagrégante classée AINS) ni la force des inhibiteurs enzymatiques.
- Une absence d'alerte n'est pas une garantie d'absence de risque.

## Usage d'assistants de code

Le code, les notebooks et une première version du jeu de test ont été produits avec l'aide de Claude (Anthropic), puis relus, exécutés et vérifiés par le groupe. Les niveaux d'interaction doivent être vérifiés par le groupe sur la version en vigueur du Thésaurus ANSM (voir `donnees/sources.md`).
