"""Évaluation : jeu de test, référence non hybride, métriques, ablation, erreurs, robustesse."""
from pathlib import Path
import json
import time
import random

import pandas as pd

from connaissances import normaliser
from regles import Verificateur, NIVEAUX

DONNEES = Path(__file__).resolve().parent.parent / "donnees"


# ---------------------------------------------------------------------------
# Jeu de test
# ---------------------------------------------------------------------------
def charger_ordonnances(fichier="ordonnances.json"):
    return json.loads((DONNEES / fichier).read_text(encoding="utf-8"))


def charger_verite(fichier="verite_terrain.csv"):
    """{(ordonnance, frozenset{med_a, med_b}): niveau} + tableau complet."""
    v = pd.read_csv(DONNEES / fichier)
    attendu = {(r.ordonnance, frozenset((r.med_a, r.med_b))): int(r.niveau) for r in v.itertuples()}
    return attendu, v


# ---------------------------------------------------------------------------
# Systèmes à comparer : chacun renvoie {frozenset(paire): niveau} pour une ordonnance
# ---------------------------------------------------------------------------
def systeme_hybride(verif):
    def predire(meds):
        alertes, _, _ = verif.verifier(meds)
        return {frozenset((a.a.nom, a.b.nom)): a.niveau for a in alertes}
    return predire


def systeme_liste_paires(verif):
    """Référence non hybride : recherche exacte de la paire dans une liste d'interactions.

    Les noms sont reconnus avec le même dictionnaire de synonymes que le système hybride,
    pour que la comparaison porte sur le raisonnement et pas sur la reconnaissance des noms.
    """
    liste = pd.read_csv(DONNEES / "liste_paires_reference.csv")
    table = {}
    for r in liste.itertuples():
        a, b = verif.resoudre(r.med_a).nom, verif.resoudre(r.med_b).nom
        table[frozenset((a, b))] = int(r.niveau)

    def predire(meds):
        noms = [verif.resoudre(m).nom for m in meds]
        sortie = {}
        for i in range(len(noms)):
            for j in range(i + 1, len(noms)):
                p = frozenset((noms[i], noms[j]))
                if None not in p and p in table:
                    sortie[p] = table[p]
        return sortie
    return predire


# ---------------------------------------------------------------------------
# Métriques
# ---------------------------------------------------------------------------
def evaluer(predire, ordonnances=None, attendu=None):
    ordonnances = ordonnances or charger_ordonnances()
    if attendu is None:
        attendu, _ = charger_verite()
    tp = fp = fn = niveau_exact = niveau_proche = nb_alertes = 0
    details, duree = [], 0.0
    for o in ordonnances:
        t0 = time.perf_counter()
        pred = predire(o["medicaments"])
        duree += time.perf_counter() - t0
        att = {p: n for (oid, p), n in attendu.items() if oid == o["id"]}
        nb_alertes += len(pred)
        for p, n in pred.items():
            if p in att:
                tp += 1
                niveau_exact += n == att[p]
                niveau_proche += abs(n - att[p]) <= 1
                details.append((o["id"], p, "VP", n, att[p]))
            else:
                fp += 1
                details.append((o["id"], p, "FP", n, None))
        for p, n in att.items():
            if p not in pred:
                fn += 1
                details.append((o["id"], p, "FN", None, n))
    precision = tp / (tp + fp) if tp + fp else 0.0
    rappel = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * rappel / (precision + rappel) if precision + rappel else 0.0
    resume = {
        "VP": tp, "FP": fp, "FN": fn,
        "précision": round(precision, 3), "rappel": round(rappel, 3), "F1": round(f1, 3),
        "alertes / ordonnance": round(nb_alertes / len(ordonnances), 2),
        "niveau exact (VP)": round(niveau_exact / tp, 3) if tp else None,
        "niveau ±1 (VP)": round(niveau_proche / tp, 3) if tp else None,
        "ms / ordonnance": round(1000 * duree / len(ordonnances), 2),
    }
    det = pd.DataFrame(details, columns=["ordonnance", "paire", "statut", "niveau_prédit", "niveau_attendu"])
    det["paire"] = det["paire"].apply(lambda p: " + ".join(sorted(p)))
    return resume, det


# ---------------------------------------------------------------------------
# Ablation
# ---------------------------------------------------------------------------
CONFIGS_ABLATION = {
    "Hybride complet (concis)": {},
    "Hybride sans filtre anti-fatigue": {"concis": False},
    "– sans filtre « marge étroite » sur G1": {"filtre_marge": False},
    "+ corroboration G2+G3 (option)": {"corroboration": True},
    "– sans règles expertes (graphe seul)": {"familles": ("pk", "effet", "cible")},
    "– sans règle pharmacocinétique G1": {"familles": ("classe", "effet", "cible")},
    "– sans règles génériques G1-G3": {"familles": ("classe",)},
    "– sans règles reprises d'Aziz (R19-R24)": {"exclure": ("R19", "R20", "R21", "R22", "R23", "R24")},
    "– sans table ATC (classes du graphe seules)": {"avec_table": False},
    "– sans classes du graphe (table seule)": {"avec_classes_graphe": False},
    "– sans dictionnaire de synonymes": {"avec_synonymes": False},
}


def ablation(graphe):
    lignes = []
    for nom, opts in CONFIGS_ABLATION.items():
        res, _ = evaluer(systeme_hybride(Verificateur(graphe, **opts)))
        lignes.append({"configuration": nom, **res})
    base = Verificateur(graphe)
    res, _ = evaluer(systeme_liste_paires(base))
    lignes.append({"configuration": "Référence non hybride : liste de paires", **res})
    return pd.DataFrame(lignes).set_index("configuration")


def par_famille(graphe):
    """Contribution de chaque famille seule."""
    lignes = []
    for fam in ("classe", "pk", "effet", "cible"):
        for concis in (True, False):
            res, _ = evaluer(systeme_hybride(Verificateur(graphe, familles=(fam,), concis=concis)))
            lignes.append({"famille seule": fam, "mode": "concis" if concis else "complet", **res})
    return pd.DataFrame(lignes)


# ---------------------------------------------------------------------------
# Analyse d'erreurs : attribuer chaque erreur à une brique
# ---------------------------------------------------------------------------
def analyser_erreurs(graphe):
    verif = Verificateur(graphe)
    complet = Verificateur(graphe, concis=False)
    ordos = {o["id"]: o["medicaments"] for o in charger_ordonnances()}
    _, det = evaluer(systeme_hybride(verif))
    lignes = []
    for r in det[det.statut != "VP"].itertuples():
        meds = ordos[r.ordonnance]
        noms = r.paire.split(" + ")
        alertes, mm, _ = (complet if r.statut == "FN" else verif).verifier(meds)
        alerte = next((a for a in alertes if sorted((a.a.nom, a.b.nom)) == noms), None)
        if r.statut == "FN":
            objets = {m.nom: m for m in mm}
            if any(n in objets and not objets[n].dans_graphe for n in noms):
                cause = "Graphe : médicament absent, et aucune règle par classe"
            elif alerte is not None:
                cause = f"Filtre anti-fatigue : seulement {', '.join(alerte.regles)} (niveau 1, masqué)"
            else:
                cause = "Règle manquante : aucune règle experte, rien dans le graphe"
        else:
            codes = alerte.regles if alerte else []
            expert = [d for d in alerte.declenchements if d.famille == "classe"] if alerte else []
            if expert and any("PCiC" in e for d in expert for e in d.explication):
                cause = f"Classe du graphe trop large ({', '.join(d.code for d in expert)})"
            elif expert:
                cause = f"Règle experte ({', '.join(d.code for d in expert)}) : absente de la vérité terrain"
            else:
                cause = f"Règle générique du graphe trop large ({', '.join(codes)})"
        lignes.append({"ordonnance": r.ordonnance, "paire": r.paire, "erreur": r.statut,
                       "niveau attendu": r.niveau_attendu, "niveau prédit": r.niveau_prédit,
                       "brique responsable": cause})
    return pd.DataFrame(lignes)


# ---------------------------------------------------------------------------
# Robustesse : variantes de saisie des noms
# ---------------------------------------------------------------------------
def _faute(nom, rng):
    if len(nom) < 5:
        return nom
    i = rng.randrange(1, len(nom) - 1)
    return nom[:i] + nom[i] + nom[i:]   # lettre doublée


VARIANTES = {
    "saisie d'origine": lambda n, rng: n,
    "MAJUSCULES": lambda n, rng: n.upper(),
    "sans accents": lambda n, rng: normaliser(n),
    "faute de frappe (lettre doublée)": _faute,
}


def robustesse(graphe):
    lignes = []
    reglages = {"synonymes + approché": dict(avec_synonymes=True, approx=True),
                "synonymes seuls": dict(avec_synonymes=True, approx=False),
                "aucun (noms du graphe)": dict(avec_synonymes=False, approx=False)}
    for nom, f in VARIANTES.items():
        for nom_reglage, opts in reglages.items():
            verif = Verificateur(graphe, **opts)
            rng = random.Random(0)
            ordos = [{**o, "medicaments": [f(m, rng) for m in o["medicaments"]]} for o in charger_ordonnances()]
            resolus = [verif.resoudre(m) for o in ordos for m in o["medicaments"]]
            res, _ = evaluer(systeme_hybride(verif), ordonnances=ordos)
            lignes.append({"variante de saisie": nom, "reconnaissance": nom_reglage,
                           "non reconnus": sum(not m.reconnu for m in resolus),
                           "reconnus « à confirmer »": sum(m.approx for m in resolus),
                           "rappel": res["rappel"], "précision": res["précision"]})
    return pd.DataFrame(lignes)


def tableau_regles():
    from regles import REGLES_CLASSES, REGLES_GRAPHE
    def fmt(x):
        return " ou ".join(x) if isinstance(x, tuple) else x
    lignes = [{"code": r["code"], "type": "classe (experte)", "condition": f"{fmt(r['A'])} + {fmt(r['B'])}",
               "niveau": NIVEAUX[r["niveau"]], "risque": r["risque"], "source": r["source"]}
              for r in REGLES_CLASSES]
    lignes += [{"code": r["code"], "type": "graphe (générique)", "condition": r["nom"],
                "niveau": NIVEAUX[r["niveau"]], "risque": "—", "source": r["source"]}
               for r in REGLES_GRAPHE]
    return pd.DataFrame(lignes)


# ---------------------------------------------------------------------------
# Bonus ProbLog : classement des paires et calibration
# ---------------------------------------------------------------------------
def scores_problog(graphe):
    """Tableau (ordonnance, paire, P(alerte), attendu 0/1) pour toutes les paires."""
    from itertools import combinations
    from problog_regles import probabilites
    verif = Verificateur(graphe)
    attendu, _ = charger_verite()
    lignes = []
    for o in charger_ordonnances():
        probas = probabilites(verif, o["medicaments"])
        noms = sorted({m.nom for m in (verif.resoudre(s) for s in o["medicaments"]) if m.reconnu})
        for a, b in combinations(noms, 2):
            p = frozenset((a, b))
            lignes.append({"ordonnance": o["id"], "paire": f"{a} + {b}",
                           "P(alerte)": round(probas.get(p, 0.0), 3),
                           "attendu": int((o["id"], p) in attendu)})
    return pd.DataFrame(lignes)


def metriques_probabilistes(df, seuils=(0.3, 0.5, 0.7), n_bins=5):
    import numpy as np
    from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
    y, p = df["attendu"].to_numpy(), df["P(alerte)"].to_numpy()
    # ECE : écart moyen entre confiance et fréquence observée, par tranche de probabilité
    bornes = np.linspace(0, 1, n_bins + 1)
    ece, fiabilite = 0.0, []
    for lo, hi in zip(bornes[:-1], bornes[1:]):
        masque = (p >= lo) & (p < hi) if hi < 1 else (p >= lo) & (p <= hi)
        if masque.any():
            ece += masque.mean() * abs(p[masque].mean() - y[masque].mean())
            fiabilite.append({"tranche": f"[{lo:.1f} ; {hi:.1f}]", "paires": int(masque.sum()),
                              "P moyenne": round(p[masque].mean(), 3),
                              "fréquence observée": round(y[masque].mean(), 3)})
    resume = {"paires": len(df), "positives": int(y.sum()),
              "AUC": round(roc_auc_score(y, p), 3),
              "précision moyenne (AP)": round(average_precision_score(y, p), 3),
              "Brier": round(brier_score_loss(y, p), 3), "ECE": round(ece, 3)}
    seuil_lignes = []
    for s in seuils:
        pred = p >= s
        tp = int((pred & (y == 1)).sum()); fp = int((pred & (y == 0)).sum()); fn = int((~pred & (y == 1)).sum())
        pr = tp / (tp + fp) if tp + fp else 0.0; rc = tp / (tp + fn) if tp + fn else 0.0
        seuil_lignes.append({"seuil": s, "VP": tp, "FP": fp, "FN": fn, "précision": round(pr, 3),
                             "rappel": round(rc, 3), "F1": round(2 * pr * rc / (pr + rc), 3) if pr + rc else 0.0})
    return resume, pd.DataFrame(fiabilite), pd.DataFrame(seuil_lignes)


def generalisation(graphe):
    """Médicaments classés par le graphe mais absents de la table ATC du groupe."""
    ordos = charger_ordonnances("ordonnances_generalisation.json")
    attendu, _ = charger_verite("verite_generalisation.csv")
    lignes = []
    for nom, opts in {"Hybride (graphe + table)": {}, "Table ATC seule": {"avec_classes_graphe": False},
                      "Classes du graphe seules": {"avec_table": False}}.items():
        res, _ = evaluer(systeme_hybride(Verificateur(graphe, **opts)), ordos, attendu)
        lignes.append({"configuration": nom, **res})
    res, _ = evaluer(systeme_liste_paires(Verificateur(graphe)), ordos, attendu)
    lignes.append({"configuration": "Référence : liste de paires", **res})
    return pd.DataFrame(lignes).set_index("configuration")


# ---------------------------------------------------------------------------
# Fusion : résultats par origine du jeu de test, et test de cohérence
# (test de cohérence repris de la version d'Aziz, ordo_check)
# ---------------------------------------------------------------------------
def par_origine(graphe):
    """Hybride et référence, séparément sur les ordonnances d'Imane (O..) et d'Aziz (P..)."""
    ordos = charger_ordonnances()
    attendu, _ = charger_verite()
    lignes = []
    for nom_jeu, filtre in [("ordonnances d'Imane (O01-O20)", "Imane"),
                            ("ordonnances d'Aziz (P01-P20)", "Aziz"), ("jeu fusionné (40)", None)]:
        sous = [o for o in ordos if filtre is None or o.get("origine") == filtre]
        ids = {o["id"] for o in sous}
        att = {k: v for k, v in attendu.items() if k[0] in ids}
        for nom_sys, f in [("Hybride", systeme_hybride(Verificateur(graphe))),
                           ("Référence : liste de paires", systeme_liste_paires(Verificateur(graphe)))]:
            res, _ = evaluer(f, sous, att)
            lignes.append({"jeu de test": nom_jeu, "système": nom_sys, "paires attendues": len(att), **res})
    return pd.DataFrame(lignes)


def coherence(graphe, n_permutations=5, graine=0):
    """Même ordonnance, médicaments dans un autre ordre : les alertes et leurs niveaux doivent être identiques."""
    verif = Verificateur(graphe)
    rng = random.Random(graine)
    total = incoherents = 0
    for o in charger_ordonnances():
        def signature(meds):
            alertes, _, _ = verif.verifier(meds)
            return sorted((tuple(sorted((a.a.nom, a.b.nom))), a.niveau, tuple(sorted(a.regles))) for a in alertes)
        ref = signature(o["medicaments"])
        for _ in range(n_permutations):
            meds = list(o["medicaments"])
            rng.shuffle(meds)
            total += 1
            incoherents += signature(meds) != ref
    return {"ordonnances": len(charger_ordonnances()), "permutations testées": total,
            "résultats incohérents": incoherents}
