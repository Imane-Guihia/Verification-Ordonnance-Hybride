"""Deuxième référence non hybride (optionnelle) : un petit LLM local interrogé SANS graphe.

Nécessite Ollama (https://ollama.com) lancé localement avec un petit modèle, par ex. :
    ollama pull llama3.2:3b
    ollama serve

Utilisation :
    from reference_llm import systeme_llm, ollama_disponible
    if ollama_disponible():
        res, det = evaluer(systeme_llm(verif, modele="llama3.2:3b"))
"""
import json
import re
import urllib.request

URL = "http://localhost:11434/api/generate"

CONSIGNE = """Tu es pharmacien. Voici une ordonnance : {meds}.
Liste UNIQUEMENT les paires de médicaments qui présentent une interaction médicamenteuse
cliniquement significative. Réponds en JSON, sans texte autour, au format :
[{{"a": "médicament 1", "b": "médicament 2", "niveau": 1-4}}]
(4 = contre-indication, 3 = association déconseillée, 2 = précaution d'emploi,
1 = à prendre en compte). Réponds [] s'il n'y a aucune interaction."""


def ollama_disponible(timeout=2):
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=timeout)
        return True
    except Exception:
        return False


def interroger(meds, modele="llama3.2:3b", timeout=120):
    corps = json.dumps({"model": modele, "prompt": CONSIGNE.format(meds=", ".join(meds)),
                        "stream": False, "options": {"temperature": 0}}).encode()
    req = urllib.request.Request(URL, corps, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        texte = json.loads(r.read())["response"]
    bloc = re.search(r"\[.*\]", texte, re.S)
    try:
        return json.loads(bloc.group(0)) if bloc else []
    except json.JSONDecodeError:
        return []


def systeme_llm(verif, modele="llama3.2:3b"):
    """Même interface que les autres systèmes : {frozenset(paire): niveau}.

    Les noms renvoyés par le LLM sont ramenés aux noms du graphe avec le même
    dictionnaire de synonymes que le système hybride.
    """
    def predire(meds):
        sortie = {}
        for item in interroger(meds, modele):
            try:
                a, b = verif.resoudre(item["a"]).nom, verif.resoudre(item["b"]).nom
                niveau = int(item.get("niveau", 2))
            except (KeyError, TypeError, ValueError):
                continue
            if a and b and a != b:
                sortie[frozenset((a, b))] = min(max(niveau, 1), 4)
        return sortie
    return predire
