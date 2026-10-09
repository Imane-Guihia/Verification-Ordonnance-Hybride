# Sources

## Données

- **Hetionet v1.0** — Himmelstein DS et al., *Systematic integration of biomedical knowledge prioritizes drugs for repurposing*, eLife 2017;6:e26726. https://github.com/hetio/hetionet — contenu original sous licence CC0.
  Les arêtes utilisées proviennent de bases intégrées par Hetionet, notamment DrugCentral (PCiC, classes pharmacologiques), DrugBank et ChEMBL (CbG), SIDER 4.1 (CcSE) et PharmacotherapyDB (CtD).

## Connaissances expertes

- **ANSM — Thésaurus des interactions médicamenteuses** (référentiel national des interactions, mis à jour régulièrement), https://ansm.sante.fr — source de toutes les règles R01-R18 et de la vérité terrain. Échelle de niveaux utilisée : contre-indication, association déconseillée, précaution d'emploi, à prendre en compte.
- **WHO Collaborating Centre for Drug Statistics Methodology — ATC/DDD Index**, https://atcddd.fhi.no/atc_ddd_index/ — codes ATC de la table de classes complémentaire (`src/connaissances.py`).
- **Résumés des caractéristiques du produit (RCP)**, EMA / base de données publique des médicaments : Viagra (sildénafil, rubrique 4.3), Zocor (simvastatine), Eliquis et Xarelto (rubrique 4.3).
- **FDA Drug Safety Communication** (2016) : opioïdes + benzodiazépines, mise en garde encadrée.
- **FDA Drug Safety Communication** (2011) : limitation de dose de la simvastatine avec l'amlodipine.
- **EMA** (2010) : interaction clopidogrel + inhibiteurs de la pompe à protons (oméprazole, ésoméprazole).

## À vérifier par le groupe

Le Thésaurus ANSM évolue d'une version à l'autre. Avant la soutenance, vérifier chaque niveau sur la version en vigueur, en priorité les lignes marquées `a_verifier = oui` dans `verite_terrain.csv` :

| Paire | Point à vérifier |
|---|---|
| simvastatine + amlodipine | présence dans le Thésaurus (la source utilisée est la FDA) |
| fluoxétine + tramadol | niveau exact (à prendre en compte ou précaution d'emploi) |
| digoxine + furosémide | niveau exact (digitaliques + hypokaliémiants) |
| allopurinol + azathioprine | association déconseillée ou contre-indication selon la version |
| sertraline + ibuprofène | niveau exact (ISRS + AINS) |

La liste `MARGE_ETROITE` (`src/connaissances.py`) et le niveau des règles R02, R07, R13 sont aussi à confirmer.
