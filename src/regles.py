"""Règles d'interaction et moteur d'alertes expliquées.

Deux familles de règles :
- règles expertes par classe (R01 à R18) : écrites et sourcées par le groupe ;
- règles génériques fondées sur le graphe (G1 à G3) : interaction pharmacocinétique,
  effet indésirable grave partagé, cible pharmacologique commune.

Chaque alerte indique son niveau, la ou les règles déclenchées, leur source et le
chemin dans le graphe (ou la ligne de table) qui justifie l'appartenance aux classes.
"""
from dataclasses import dataclass, field
from itertools import combinations
import time

import difflib

from connaissances import (SYNONYMES, CLASSES, GROUPES, EFFETS_GRAVES, ENZYMES_PK,
                           MARGE_ETROITE, normaliser, est_pharmacodynamique)

NIVEAUX = {4: "Contre-indication", 3: "Association déconseillée",
           2: "Précaution d'emploi", 1: "À prendre en compte"}

ANSM = "ANSM, Thésaurus des interactions médicamenteuses"

# ---------------------------------------------------------------------------
# Règles expertes par classe
# ---------------------------------------------------------------------------
REGLES_CLASSES = [
    dict(code="R01", nom="AVK + AINS", A="AVK", B="AINS", niveau=3,
         risque="majoration du risque hémorragique", source=f"{ANSM} : AVK + AINS"),
    dict(code="R02", nom="Anticoagulant + antiagrégant", A="ANTICOAGULANT", B="ANTIAGREGANT",
         niveau=1, risque="majoration du risque hémorragique",
         source=f"{ANSM} : anticoagulants oraux + antiagrégants plaquettaires"),
    dict(code="R03", nom="Deux anticoagulants", A="ANTICOAGULANT", B="ANTICOAGULANT", niveau=4,
         risque="risque hémorragique majeur (hors relais)",
         source="RCP Eliquis / Xarelto (EMA), rubrique 4.3 contre-indications"),
    dict(code="R04", nom="Statine CYP3A4 + inhibiteur puissant du CYP3A4", A="STATINE_3A4",
         B="INHIB_3A4_FORT", niveau=4, risque="rhabdomyolyse",
         source=f"{ANSM} : simvastatine + inhibiteurs puissants du CYP3A4 ; RCP Zocor"),
    dict(code="R05", nom="Dérivé nitré + IPDE5", A="NITRE", B="IPDE5", niveau=4,
         risque="hypotension sévère", source=f"{ANSM} ; RCP Viagra (EMA), rubrique 4.3"),
    dict(code="R06", nom="IMAO non sélectif + sérotoninergique", A="IMAO_NS",
         B="SEROTONINERGIQUE_LARGE", niveau=4, risque="syndrome sérotoninergique",
         source=f"{ANSM} : IMAO non sélectifs + ISRS"),
    dict(code="R07", nom="ISRS/IRSN + autre sérotoninergique", A="ISRS_IRSN", B="SEROTONINERGIQUE",
         niveau=1, risque="syndrome sérotoninergique, convulsions",
         source=f"{ANSM} : médicaments sérotoninergiques ; tramadol + ISRS"),
    dict(code="R08", nom="IEC/ARA2 + épargneur de potassium", A="SRAA", B="EPARGNEUR_K",
         niveau=3, risque="hyperkaliémie", source=f"{ANSM} : épargneurs de potassium + IEC / ARA II"),
    dict(code="R09", nom="Méthotrexate + AINS", A="METHOTREXATE", B="AINS", niveau=3,
         risque="toxicité hématologique du méthotrexate (doses > 20 mg/semaine)",
         source=f"{ANSM} : méthotrexate + AINS"),
    dict(code="R10", nom="Méthotrexate + antifolique", A="METHOTREXATE", B="ANTIFOLIQUE",
         niveau=3, risque="toxicité hématologique", source=f"{ANSM} : méthotrexate + triméthoprime"),
    dict(code="R11", nom="Digitalique + inhibiteur de la P-gp", A="DIGITALIQUE", B="INHIB_PGP",
         niveau=2, risque="surdosage digitalique",
         source=f"{ANSM} : digoxine + amiodarone, digoxine + macrolides"),
    dict(code="R12", nom="Deux torsadogènes", A="TORSADOGENE", B="TORSADOGENE", niveau=3,
         risque="torsades de pointes", source=f"{ANSM} : médicaments susceptibles de donner des torsades de pointes"),
    dict(code="R13", nom="Opioïde + benzodiazépine", A="OPIOIDE", B="BZD_HYPNOTIQUE", niveau=1,
         risque="dépression respiratoire",
         source=f"{ANSM} : morphiniques + benzodiazépines ; FDA Drug Safety Communication (2016)"),
    dict(code="R14", nom="Clopidogrel + inhibiteur du CYP2C19", A="CLOPIDOGREL", B="INHIB_2C19",
         niveau=3, risque="diminution de l'efficacité antiagrégante",
         source=f"{ANSM} : clopidogrel + oméprazole / ésoméprazole ; EMA (2010)"),
    dict(code="R15", nom="Deux AINS", A="AINS", B="AINS", niveau=3,
         risque="ulcère et hémorragie digestive", source=f"{ANSM} : AINS + autres AINS"),
    dict(code="R16", nom="IEC/ARA2 + AINS", A="SRAA", B="AINS", niveau=2,
         risque="insuffisance rénale aiguë", source=f"{ANSM} : AINS + IEC / ARA II"),
    dict(code="R17", nom="Lithium + AINS ou IEC/ARA2", A="LITHIUM", B=("AINS", "SRAA"),
         niveau=3, risque="surdosage en lithium", source=f"{ANSM} : lithium + AINS ; lithium + IEC / ARA II"),
    dict(code="R18", nom="Deux antiagrégants", A="ANTIAGREGANT", B="ANTIAGREGANT", niveau=1,
         risque="majoration du risque hémorragique", source=f"{ANSM} : antiagrégants plaquettaires entre eux"),
    # --- R19-R24 : règles reprises de la version d'Aziz (ordo_check), niveaux ramenés à l'échelle ANSM ---
    dict(code="R19", nom="ISRS/IRSN + AINS", A="ISRS_IRSN", B="AINS", niveau=1,
         risque="majoration du risque hémorragique (saignement digestif)",
         source=f"{ANSM} : ISRS + AINS ; RCP Cymbalta (FDA) §7.4"),
    dict(code="R20", nom="ISRS/IRSN + anticoagulant oral", A="ISRS_IRSN", B="ANTICOAG_ORAL", niveau=2,
         risque="majoration du risque hémorragique",
         source=f"{ANSM} : ISRS + anticoagulants oraux ; RCP Cymbalta (FDA) §7.4"),
    dict(code="R21", nom="Antiagrégant + AINS", A="ANTIAGREGANT", B="AINS", niveau=1,
         risque="majoration du risque hémorragique, notamment digestif",
         source=f"{ANSM} : antiagrégants plaquettaires + AINS ; RCP Plavix (FDA) §7.3"),
    dict(code="R22", nom="Digoxine + macrolide", A="DIGITALIQUE", B="MACROLIDE", niveau=2,
         risque="augmentation de la digoxinémie",
         source=f"{ANSM} : digoxine + clarithromycine / érythromycine ; RCP Lanoxin (FDA) §7.2"),
    dict(code="R23", nom="Potassium + diurétique épargneur de potassium", A="POTASSIUM", B="EPARGNEUR_K",
         niveau=4, risque="hyperkaliémie potentiellement létale (sauf hypokaliémie)",
         source=f"{ANSM} : potassium + diurétiques épargneurs de potassium ; RCP Aldactone (FDA) §7.1"),
    dict(code="R24", nom="Potassium + IEC/ARA2", A="POTASSIUM", B="SRAA", niveau=3,
         risque="hyperkaliémie (sauf hypokaliémie)",
         source=f"{ANSM} : potassium + IEC / ARA II"),
]

REGLES_GRAPHE = [
    dict(code="G1", nom="Interaction pharmacocinétique (graphe)", niveau=2,
         source="Hetionet : classe d'inhibiteur/inducteur (PCiC) + liaison à l'enzyme (CbG) ; "
                "niveau 2 si la victime est à marge thérapeutique étroite, sinon 1"),
    dict(code="G2", nom="Effet indésirable grave partagé (graphe)", niveau=1,
         source="Hetionet : arêtes CcSE (SIDER) ; liste d'effets graves du groupe"),
    dict(code="G3", nom="Cible pharmacologique commune (graphe)", niveau=1,
         source="Hetionet : arêtes CbG, hors enzymes et transporteurs"),
]


# ---------------------------------------------------------------------------
# Structures
# ---------------------------------------------------------------------------
@dataclass
class Medicament:
    saisi: str
    nom: str | None = None   # nom DrugBank (Hetionet)
    id: str | None = None    # identifiant Hetionet, None si absent du graphe
    approx: bool = False     # True si reconnu par correspondance approchée (à confirmer)

    @property
    def reconnu(self):
        return self.nom is not None

    @property
    def dans_graphe(self):
        return self.id is not None


@dataclass
class Declenchement:
    code: str
    famille: str          # "classe" | "pk" | "effet" | "cible"
    niveau: int
    risque: str
    explication: list
    source: str


@dataclass
class Alerte:
    a: Medicament
    b: Medicament
    declenchements: list = field(default_factory=list)

    @property
    def niveau(self):
        return max(d.niveau for d in self.declenchements)

    @property
    def regles(self):
        return [d.code for d in self.declenchements]

    def paire(self):
        return tuple(sorted((self.a.nom, self.b.nom)))

    def texte(self, numero=None):
        """Format détaillé d'une alerte, adapté à la lecture dans le terminal."""
        titre = f"ALERTE {numero} — {NIVEAUX[self.niveau].upper()}" if numero else NIVEAUX[self.niveau].upper()
        lignes = [titre, f"Paire concernée : {self.a.saisi} + {self.b.saisi}"]
        for d in sorted(self.declenchements, key=lambda d: -d.niveau):
            lignes.extend([f"Risque : {d.risque}",
                           f"Règle {d.code} ({NIVEAUX[d.niveau]})"])
            for e in d.explication:
                lignes.append(f"  - {e}")
            lignes.append(f"Source : {d.source}")
        return "\n".join(lignes)


# ---------------------------------------------------------------------------
# Moteur
# ---------------------------------------------------------------------------
TOUTES_FAMILLES = ("classe", "pk", "effet", "cible")


class Verificateur:
    """Vérifie une ordonnance à partir du graphe et des règles.

    Options (pour l'ablation) :
        familles             : familles de règles actives
        avec_table           : utiliser la table ATC complémentaire
        avec_classes_graphe  : utiliser les classes du graphe (PCiC)
        avec_synonymes       : reconnaître DCI françaises et noms commerciaux
        concis               : masquer les alertes génériques de niveau 1 (anti-fatigue)
        filtre_marge         : G1 au niveau 2 seulement si la « victime » est à marge
                               thérapeutique étroite (sinon niveau 1)
        corroboration        : (option, désactivée par défaut) en mode concis, garder une alerte
                               générique de niveau 1 si au moins deux règles du graphe la soutiennent
        approx               : reconnaître les noms mal orthographiés (correspondance approchée)
        exclure              : codes de règles expertes à désactiver (ablation)
    """

    def __init__(self, graphe, familles=TOUTES_FAMILLES, avec_table=True,
                 avec_classes_graphe=True, avec_synonymes=True, concis=True,
                 filtre_marge=True, corroboration=False, approx=True, exclure=()):
        self.G = graphe
        self.familles = set(familles)
        self.avec_table, self.avec_classes_graphe = avec_table, avec_classes_graphe
        self.avec_synonymes, self.concis = avec_synonymes, concis
        self.filtre_marge, self.corroboration, self.approx = filtre_marge, corroboration, approx
        self.exclure = set(exclure)
        tous_noms = {n for c in CLASSES.values() for n in c["table"]}
        self._noms_table = {normaliser(n): n for n in tous_noms}
        self._vocabulaire = dict(self._noms_table)
        self._vocabulaire.update({normaliser(n): n for n in graphe.noeuds[graphe.noeuds.kind == "Compound"].name})
        if avec_synonymes:
            self._vocabulaire.update(SYNONYMES)

    # -- reconnaissance des médicaments ------------------------------------
    def resoudre(self, saisi):
        cle = normaliser(saisi)
        nom = SYNONYMES.get(cle) if self.avec_synonymes else None
        approx = False
        if nom is None:
            i = self.G.id_de(saisi)
            if i is not None:
                nom = self.G.nom[i]
            elif cle in self._noms_table:
                nom = self._noms_table[cle]
        if nom is None and self.approx:
            proche = difflib.get_close_matches(cle, self._vocabulaire, n=1, cutoff=0.85)
            if proche:
                nom, approx = self._vocabulaire[proche[0]], True
        if nom is None:
            return Medicament(saisi)
        return Medicament(saisi, nom, self.G.id_de(nom), approx)

    # -- appartenance aux classes, avec sa preuve --------------------------
    def preuve_classe(self, med, classe):
        """Chaîne expliquant pourquoi med appartient à la classe (ou None)."""
        if classe in GROUPES:
            for c in GROUPES[classe]:
                p = self.preuve_classe(med, c)
                if p:
                    return p
            return None
        defn = CLASSES[classe]
        if self.avec_classes_graphe and med.dans_graphe:
            communes = sorted(self.G.classes(med.id) & set(defn["pcic"]))
            if communes:
                return f"{med.nom} ←[PCiC]— « {communes[0]} » ⇒ {defn['libelle']}"
        if self.avec_table and med.nom in defn["table"]:
            return f"{med.nom} ∈ {defn['libelle']} (table ATC {defn['table'][med.nom]})"
        return None

    # -- règles -------------------------------------------------------------
    def _regles_classes(self, x, y):
        sortie = []
        for r in REGLES_CLASSES:
            if r["code"] in self.exclure:
                continue
            cibles_b = r["B"] if isinstance(r["B"], tuple) else (r["B"],)
            for a, b in ((x, y), (y, x)):
                pa = self.preuve_classe(a, r["A"])
                pb = next((p for c in cibles_b if (p := self.preuve_classe(b, c))), None)
                if pa and pb:
                    sortie.append(Declenchement(r["code"], "classe", r["niveau"], r["risque"],
                                                [pa, pb], r["source"]))
                    break
        return sortie

    def _regle_pk(self, x, y):
        if not (x.dans_graphe and y.dans_graphe):
            return []
        expl, victimes = [], set()
        for a, b in ((x, y), (y, x)):
            classes_a, cibles_b = self.G.classes(a.id), self.G.cibles(b.id)
            for enzyme, (inhib, induc) in ENZYMES_PK.items():
                if enzyme not in cibles_b:
                    continue
                for cl, effet in ((inhib, "inhibe"), (induc, "induit")):
                    if cl and cl in classes_a:
                        expl.append(f"{a.nom} ←[PCiC]— « {cl} » ; {b.nom} —[CbG]→ {enzyme} "
                                    f"⇒ {a.nom} {effet} l'élimination de {b.nom}")
                        victimes.add(b.nom)
        if not expl:
            return []
        etroites = sorted(victimes & MARGE_ETROITE)
        if not self.filtre_marge:
            niveau = 2
        elif etroites:
            niveau = 2
            expl.append(f"{', '.join(etroites)} : marge thérapeutique étroite ⇒ niveau relevé")
        else:
            niveau = 1
        return [Declenchement("G1", "pk", niveau, "modification des concentrations (pharmacocinétique)",
                              expl[:4], REGLES_GRAPHE[0]["source"])]

    def _regle_effet(self, x, y):
        if not (x.dans_graphe and y.dans_graphe):
            return []
        communs = sorted(self.G.effets(x.id) & self.G.effets(y.id) & set(EFFETS_GRAVES),
                         key=lambda e: -EFFETS_GRAVES[e])
        if not communs:
            return []
        # Niveau 1 : un effet partagé dans SIDER est un signal faible (les listes d'effets
        # sont longues et non pondérées par la fréquence) -> masqué en mode concis.
        niveau = 1
        expl = [f"{x.nom} —[CcSE]→ {e} ←[CcSE]— {y.nom}" for e in communs[:3]]
        return [Declenchement("G2", "effet", niveau, "cumul d'effets indésirables graves : "
                              + ", ".join(communs[:3]), expl, REGLES_GRAPHE[1]["source"])]

    def _regle_cible(self, x, y):
        if not (x.dans_graphe and y.dans_graphe):
            return []
        communes = sorted(g for g in self.G.cibles(x.id) & self.G.cibles(y.id)
                          if est_pharmacodynamique(g))
        if not communes:
            return []
        expl = [f"{x.nom} —[CbG]→ {g} ←[CbG]— {y.nom}" for g in communes[:3]]
        return [Declenchement("G3", "cible", 1, "action sur une même cible : " + ", ".join(communes[:3]),
                              expl, REGLES_GRAPHE[2]["source"])]

    # -- analyse d'une ordonnance -----------------------------------------
    def verifier(self, ordonnance):
        """Renvoie (alertes triées par gravité, médicaments, avertissements)."""
        meds = [self.resoudre(s) for s in ordonnance]
        avert = []
        for m in meds:
            if not m.reconnu:
                avert.append(f"« {m.saisi} » non reconnu : interactions NON vérifiées pour ce médicament.")
            elif m.approx:
                avert.append(f"« {m.saisi} » interprété comme {m.nom} : à confirmer.")
            if m.reconnu and not m.dans_graphe:
                avert.append(f"{m.nom} absent du graphe : seules les règles par classe (table) s'appliquent.")
        alertes = []
        connus = [m for m in meds if m.reconnu]
        for x, y in combinations(connus, 2):
            if x.nom == y.nom:
                continue
            decl = []
            if "classe" in self.familles:
                decl += self._regles_classes(x, y)
            if "pk" in self.familles:
                decl += self._regle_pk(x, y)
            if "effet" in self.familles:
                decl += self._regle_effet(x, y)
            if "cible" in self.familles:
                decl += self._regle_cible(x, y)
            if self.concis:
                generiques = {d.famille for d in decl if d.famille != "classe"}
                corroboree = self.corroboration and len(generiques) >= 2
                decl = [d for d in decl
                        if d.famille == "classe" or d.niveau >= 2 or corroboree]
            if decl:
                alertes.append(Alerte(x, y, decl))
        alertes.sort(key=lambda a: -a.niveau)
        return alertes, meds, avert

    def rapport(self, ordonnance):
        """Texte lisible pour le prescripteur."""
        t0 = time.perf_counter()
        alertes, meds, avert = self.verifier(ordonnance)
        duree = (time.perf_counter() - t0) * 1000
        lignes = ["=" * 68,
                  "             VÉRIFICATION D'ORDONNANCE",
                  "=" * 68,
                  "Médicaments analysés : " + ", ".join(
                      m.saisi + (f" → {m.nom}" if m.nom and m.nom.lower() != m.saisi.lower() else "")
                      for m in meds)]
        if avert:
            lignes += ["", "AVERTISSEMENTS"]
            lignes += [f"! {a}" for a in avert]
        if not alertes:
            lignes += ["", "RÉSULTAT : aucune interaction détectée par les règles.",
                       "Cela ne garantit pas l'absence de risque clinique."]
        else:
            repartition = []
            for niveau in sorted({a.niveau for a in alertes}, reverse=True):
                n = sum(a.niveau == niveau for a in alertes)
                repartition.append(f"{n} {NIVEAUX[niveau].lower()}")
            lignes += ["", f"RÉSUMÉ : {len(alertes)} alerte(s) détectée(s) — " + "; ".join(repartition),
                       "-" * 68]
            for i, alerte in enumerate(alertes, start=1):
                lignes += [alerte.texte(i), "-" * 68]
        lignes.append(f"Analyse terminée en {duree:.1f} ms")
        return "\n".join(lignes)
