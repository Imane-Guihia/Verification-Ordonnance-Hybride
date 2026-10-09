"""Bonus : version ProbLog avec des règles pondérées.

Chaque règle reçoit un poids = croyance a priori que l'interaction est cliniquement
pertinente. ProbLog combine les preuves (ou bruité) et renvoie P(alerte) pour chaque
paire, ce qui permet de classer les alertes et de mesurer la calibration.

Poids fixés A PRIORI (avant toute évaluation), d'après le niveau ANSM et la nature
de la preuve :
    règle experte : CI 0,95 · déconseillée 0,90 · précaution 0,80 · à prendre en compte 0,60
    G1 (pharmacocinétique) : 0,40 par enzyme si victime à marge étroite, 0,15 sinon
    G2 (effet grave partagé) : 0,05 par effet
    G3 (cible commune)       : 0,15 par cible
"""
from itertools import combinations
import re

from problog.program import PrologString
from problog import get_evaluatable

from connaissances import CLASSES, GROUPES, EFFETS_GRAVES, ENZYMES_PK, MARGE_ETROITE, est_pharmacodynamique
from regles import REGLES_CLASSES

POIDS_NIVEAU = {4: 0.95, 3: 0.90, 2: 0.80, 1: 0.60}
P_PK_ETROITE, P_PK, P_EFFET, P_CIBLE = 0.40, 0.15, 0.05, 0.15


def atome(texte):
    return "a_" + re.sub(r"[^a-z0-9]+", "_", texte.lower()).strip("_")


def _regles_problog():
    lignes = []
    for groupe, membres in GROUPES.items():
        for m in membres:
            lignes.append(f"classe(X, {atome(groupe)}) :- classe(X, {atome(m)}).")
    for r in REGLES_CLASSES:
        p = POIDS_NIVEAU[r["niveau"]]
        bs = r["B"] if isinstance(r["B"], tuple) else (r["B"],)
        for b in bs:
            lignes.append(f"{p}::expert(X, Y) :- classe(X, {atome(r['A'])}), classe(Y, {atome(b)}), X \\= Y.")
    lignes += [
        f"{P_PK_ETROITE}::pk(X, Y) :- inhibe(X, E), lie(Y, E), marge(Y), X \\= Y.",
        f"{P_PK}::pk(X, Y) :- inhibe(X, E), lie(Y, E), \\+ marge(Y), X \\= Y.",
        f"{P_EFFET}::effet(X, Y) :- cause(X, S), cause(Y, S), X \\= Y.",
        f"{P_CIBLE}::cible(X, Y) :- cible_pd(X, G), cible_pd(Y, G), X \\= Y.",
        "alerte(X, Y) :- expert(X, Y).", "alerte(X, Y) :- expert(Y, X).",
        "alerte(X, Y) :- pk(X, Y).", "alerte(X, Y) :- pk(Y, X).",
        "alerte(X, Y) :- effet(X, Y).", "alerte(X, Y) :- cible(X, Y).",
    ]
    return lignes


def programme(verif, meds):
    """Construit le programme ProbLog d'une ordonnance (faits + règles + requêtes)."""
    G = verif.G
    objets = [m for m in (verif.resoudre(s) for s in meds) if m.reconnu]
    faits = []
    for m in objets:
        x = atome(m.nom)
        for c in CLASSES:
            if verif.preuve_classe(m, c):
                faits.append(f"classe({x}, {atome(c)}).")
        if m.nom in MARGE_ETROITE:
            faits.append(f"marge({x}).")
        if m.dans_graphe:
            classes_g, cibles = G.classes(m.id), G.cibles(m.id)
            for enzyme, (inhib, induc) in ENZYMES_PK.items():
                if enzyme in cibles:
                    faits.append(f"lie({x}, {atome(enzyme)}).")
                if (inhib and inhib in classes_g) or (induc and induc in classes_g):
                    faits.append(f"inhibe({x}, {atome(enzyme)}).")
            for e in G.effets(m.id) & set(EFFETS_GRAVES):
                faits.append(f"cause({x}, {atome(e)}).")
            for g in cibles:
                if est_pharmacodynamique(g):
                    faits.append(f"cible_pd({x}, {atome(g)}).")
    noms = sorted({m.nom for m in objets})
    requetes = [f"query(alerte({atome(a)}, {atome(b)}))." for a, b in combinations(noms, 2)]
    # déclarations pour les prédicats éventuellement sans faits
    vides = [f"{p} :- fail." for p in ("classe(_, _)", "marge(_)", "lie(_, _)", "inhibe(_, _)",
                                         "cause(_, _)", "cible_pd(_, _)")]
    texte = "\n".join(vides + faits + _regles_problog() + requetes)
    return texte, noms


def probabilites(verif, meds):
    """{frozenset(paire de noms DrugBank): P(alerte)} pour toutes les paires de l'ordonnance."""
    texte, noms = programme(verif, meds)
    if len(noms) < 2:
        return {}
    res = get_evaluatable().create_from(PrologString(texte)).evaluate()
    par_atome = {atome(n): n for n in noms}
    sortie = {}
    for terme, p in res.items():
        a, b = (str(t) for t in terme.args)
        sortie[frozenset((par_atome[a], par_atome[b]))] = float(p)
    return sortie
