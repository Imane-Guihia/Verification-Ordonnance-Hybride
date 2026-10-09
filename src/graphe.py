"""Chargement de Hetionet v1.0 et extraction du sous-graphe « ordonnance ».

Sujet 3 – Vérification d'ordonnance par graphe et règles.
Remplaçable par le module hetionet_utils.py fourni par l'enseignant.

Sous-graphe gardé :
    nœuds  : Compound, Pharmacologic Class, Gene, Side Effect, Disease
    arêtes : PCiC (classe contient médicament), CbG (médicament se lie à un gène),
             CcSE (médicament cause un effet indésirable), CtD (médicament traite une maladie)
"""
from pathlib import Path
import urllib.request

import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
URLS = {
    "hetionet-v1.0-nodes.tsv":
        "https://github.com/hetio/hetionet/raw/main/hetnet/tsv/hetionet-v1.0-nodes.tsv",
    "hetionet-v1.0-edges.sif.gz":
        "https://media.githubusercontent.com/media/hetio/hetionet/main/hetnet/tsv/hetionet-v1.0-edges.sif.gz",
}
ARETES_UTILES = ["PCiC", "CbG", "CcSE", "CtD"]
NOEUDS_UTILES = ["Compound", "Pharmacologic Class", "Gene", "Side Effect", "Disease"]


# ---------------------------------------------------------------------------
# Chargement
# ---------------------------------------------------------------------------
def telecharger(dossier=DATA):
    """Télécharge les deux fichiers TSV de Hetionet s'ils sont absents."""
    dossier = Path(dossier)
    dossier.mkdir(parents=True, exist_ok=True)
    for nom, url in URLS.items():
        chemin = dossier / nom
        if not chemin.exists():
            print("Téléchargement de", nom, "...")
            urllib.request.urlretrieve(url, chemin)
    return dossier


def charger_hetionet(dossier=DATA):
    """Renvoie (noeuds, aretes) du graphe complet : 47 031 nœuds, 2 250 197 arêtes."""
    dossier = telecharger(dossier)
    noeuds = pd.read_csv(dossier / "hetionet-v1.0-nodes.tsv", sep="\t")
    aretes = pd.read_csv(dossier / "hetionet-v1.0-edges.sif.gz", sep="\t")
    return noeuds, aretes


def extraire_sous_graphe(noeuds, aretes):
    """Garde seulement les nœuds et arêtes utiles à la vérification d'ordonnance."""
    a = aretes[aretes.metaedge.isin(ARETES_UTILES)].copy()
    ids = set(a.source) | set(a.target)
    n = noeuds[noeuds.kind.isin(NOEUDS_UTILES) & noeuds.id.isin(ids)].copy()
    # tous les médicaments sont gardés, même sans arête utile (cas « absent du graphe »)
    n = pd.concat([n, noeuds[(noeuds.kind == "Compound") & ~noeuds.id.isin(n.id)]])
    return n.reset_index(drop=True), a.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Base de connaissances : un dictionnaire par médicament
# ---------------------------------------------------------------------------
class Graphe:
    """Accès simple au sous-graphe : classes, cibles, effets, maladies d'un médicament."""

    def __init__(self, noeuds, aretes):
        self.noeuds, self.aretes = noeuds, aretes
        self.nom = dict(zip(noeuds.id, noeuds.name))
        comp = noeuds[noeuds.kind == "Compound"]
        self._par_nom = {n.lower(): i for i, n in zip(comp.id, comp.name)}

        def grouper(metaedge, cle, valeur):
            s = aretes[aretes.metaedge == metaedge]
            return s.groupby(cle)[valeur].apply(set).to_dict()

        self._classes = grouper("PCiC", "target", "source")   # médicament -> classes
        self._cibles = grouper("CbG", "source", "target")     # médicament -> gènes
        self._effets = grouper("CcSE", "source", "target")    # médicament -> effets
        self._maladies = grouper("CtD", "source", "target")   # médicament -> maladies

    # -- recherche --------------------------------------------------------
    def id_de(self, nom):
        """Identifiant Hetionet d'un médicament à partir de son nom (insensible à la casse)."""
        return self._par_nom.get(nom.strip().lower())

    def chercher(self, motif):
        """Médicaments dont le nom contient le motif."""
        return sorted(n for n in self._par_nom if motif.lower() in n)

    # -- voisinages (renvoient des noms lisibles) -------------------------
    def classes(self, med):
        return {self.nom[x] for x in self._classes.get(med, ())}

    def cibles(self, med):
        return {self.nom[x] for x in self._cibles.get(med, ())}

    def effets(self, med):
        return {self.nom[x] for x in self._effets.get(med, ())}

    def maladies(self, med):
        return {self.nom[x] for x in self._maladies.get(med, ())}

    def fiche(self, nom):
        """Résumé d'un médicament : ce que le graphe sait (et ne sait pas)."""
        med = self.id_de(nom)
        if med is None:
            return {"médicament": nom, "dans_le_graphe": False}
        return {
            "médicament": self.nom[med],
            "id": med,
            "dans_le_graphe": True,
            "classes": sorted(self.classes(med)),
            "nb_cibles": len(self.cibles(med)),
            "nb_effets": len(self.effets(med)),
            "maladies_traitées": sorted(self.maladies(med)),
        }

    def couverture(self):
        """Part des médicaments ayant au moins une arête de chaque type."""
        total = (self.noeuds.kind == "Compound").sum()
        lignes = []
        for code, d in [("PCiC (classe)", self._classes), ("CbG (cible)", self._cibles),
                        ("CcSE (effet)", self._effets), ("CtD (maladie)", self._maladies)]:
            lignes.append({"type d'arête": code, "médicaments couverts": len(d),
                           "total": int(total), "couverture": round(len(d) / total, 3)})
        return pd.DataFrame(lignes)


def charger_graphe(dossier=DATA):
    """Raccourci : téléchargement + extraction + objet Graphe."""
    noeuds, aretes = charger_hetionet(dossier)
    return Graphe(*extraire_sous_graphe(noeuds, aretes))
