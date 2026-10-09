"""Vérifier une ordonnance en ligne de commande.

    python src/verifier.py warfarine ibuprofène oméprazole
    python src/verifier.py --complet Kardégic ramipril metformine
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from graphe import charger_graphe   # noqa: E402
from regles import Verificateur     # noqa: E402

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Vérification d'ordonnance par graphe et règles")
    p.add_argument("medicaments", nargs="+", help="noms des médicaments (DCI ou nom commercial)")
    p.add_argument("--complet", action="store_true", help="afficher aussi les signaux faibles du graphe")
    a = p.parse_args()
    print(Verificateur(charger_graphe(), concis=not a.complet).rapport(a.medicaments))
