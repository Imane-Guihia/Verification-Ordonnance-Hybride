# Sujet 3 — Vérification d'ordonnance par graphe et règles

Mini-projet IA hybride — ISIS Castres, 5e année DSIA. Binôme : Imane Guihia et Mohamed Aziz Braham.

Version fusionnée des deux prototypes du binôme (voir « Contributions »).

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

## Résultats principaux (40 ordonnances, 54 paires à risque attendues)

| Système | Précision | Rappel | F1 | Alertes / ordonnance |
|---|---|---|---|---|
| **Hybride (graphe + règles), mode concis** | 0,96 | 0,89 | **0,92** | 1,25 |
| Hybride sans filtre anti-fatigue | 0,42 | 0,94 | 0,58 | 3,02 |
| Graphe seul (règles génériques G1-G3) | 0,91 | 0,19 | 0,31 | 0,28 |
| Référence non hybride : liste de paires | 1,00 | 0,39 | 0,56 | 0,53 |

- Généralisation (5 ordonnances, médicaments absents de la table) : hybride 5/5, table seule 0/5, liste de paires 0/5.
- Cohérence : 0 résultat incohérent sur 200 permutations de l'ordre des médicaments.
- Avant la fusion, l'évaluation croisée donnait : version d'Imane F1 0,83 sur son jeu et 0,76 sur celui d'Aziz ; version d'Aziz F1 0,94 sur son jeu et 0,38 sur celui d'Imane. Les règles R19-R24 ayant été ajoutées après avoir vu les ordonnances d'Aziz, le score sur ses ordonnances (F1 0,98) est optimiste.

## Structure

```
projet/
├── README.md
├── requirements.txt
├── src/
│   ├── graphe.py            chargement de Hetionet, sous-graphe, accès par médicament
│   ├── connaissances.py     synonymes, table ATC, effets graves, marge thérapeutique étroite
│   ├── regles.py            24 règles expertes + 3 règles du graphe, moteur d'alertes
│   ├── evaluation.py        métriques, référence, ablation, erreurs, robustesse, généralisation, cohérence
│   ├── problog_regles.py    bonus : règles pondérées en ProbLog
│   ├── reference_llm.py     2e référence optionnelle : LLM local sans graphe (Ollama)
│   └── verifier.py          vérification en ligne de commande
├── notebooks/
│   ├── 01_exploration_hetionet.ipynb
│   ├── 02_regles_et_alertes.ipynb
│   ├── 03_evaluation.ipynb
│   └── 04_bonus_problog.ipynb
├── donnees/
│   ├── ordonnances.json                 40 ordonnances de test (O01-O20 Imane, P01-P20 Aziz)
│   ├── verite_terrain.csv               54 alertes attendues, niveau et source
│   ├── ordonnances_generalisation.json  5 ordonnances de généralisation
│   ├── verite_generalisation.csv
│   ├── liste_paires_reference.csv       26 paires pour la référence non hybride
│   └── sources.md                       sources et points à vérifier
├── soutenance/              présentation et trame orale de la version d'Aziz (chiffres à mettre à jour)
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

- Vérité terrain construite par le binôme : 16 paires sur 54 sont marquées « à vérifier » sur la version en vigueur du Thésaurus ANSM.
- Règles et jeu de test écrits par les mêmes personnes : les scores sur chaque jeu sont optimistes (voir l'évaluation croisée).
- Le filtre « marge étroite » de la règle G1 a été ajouté après l'analyse d'erreurs sur le jeu de test : risque de sur-ajustement, à confirmer sur d'autres ordonnances.
- Le graphe ne connaît ni les doses (aspirine antiagrégante classée AINS) ni la force des inhibiteurs enzymatiques.
- Une absence d'alerte n'est pas une garantie d'absence de risque.

## Contributions

| Élément | Origine |
|---|---|
| Architecture, table ATC, synonymes, règles R01-R18 et G1-G3, filtres, notebooks, ProbLog, ordonnances O01-O20 | version d'Imane |
| Règles R19-R24 (ISRS/IRSN + AINS ou AVK, antiagrégant + AINS, digoxine + macrolides, potassium + épargneurs ou IEC/ARA2), ordonnances P01-P20, test de cohérence par permutations, présentation et trame orale | version d'Aziz ([ordo_check](https://github.com/mohamedazizbraham/ordo_check)) |
| Évaluation croisée, fusion des jeux de test, niveaux ANSM des paires d'Aziz | fusion |

## Usage d'assistants de code

La version d'Imane et la fusion ont été produites avec l'aide de Claude (Anthropic), la version d'Aziz avec l'aide de Codex (OpenAI) ; le binôme a relu, exécuté et vérifié le code. Les niveaux d'interaction doivent être vérifiés par le groupe sur la version en vigueur du Thésaurus ANSM (voir `donnees/sources.md`).
