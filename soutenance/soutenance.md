# Trame de soutenance — 12 minutes (binôme)

| Temps | Intervenant | Diapositive et message |
|---:|---|---|
| 0:00–1:00 | A | Problème : détecter des risques sans saturer le prescripteur ; objectif et précaution « prototype pédagogique ». |
| 1:00–2:15 | A | Données : Hetionet, sous-graphe Compound–classes–cibles–effets ; pourquoi un graphe seul ne suffit pas. |
| 2:15–4:00 | A | Architecture : ordonnance → normalisation → paires → règle + chemin → fusion et tri. Montrer l’exemple Warfarin–Ibuprofen. |
| 4:00–5:15 | A | Onze règles cliniques sourcées ; deux hypothèses séparées et explicitement non cliniques. |
| 5:15–6:30 | B | Protocole : 20 ordonnances, cas standards, peu de données, règles et hors distribution ; vérité terrain documentée. |
| 6:30–8:15 | B | Résultats : F1 0,902 ; F1 0,936 après filtrage des hypothèses ; 1,10 alerte/ordonnance ; baseline F1 0,333. |
| 8:15–9:30 | B | Ablation : sans classes F1 0,486 → les classes portent le gain ; effets exploratoires = 3 FP. |
| 9:30–10:45 | B | Erreurs : deux FN dus aux manques du graphe ; Heparin hors distribution signalé inconnu, pas jugé sûr. |
| 10:45–12:00 | A + B | Limites et suite : validation indépendante par pharmacien, données patient/dose, version probabiliste/embeddings uniquement comme hypothèses. |

## Visuels à préparer

1. Un schéma simple de l’architecture (5 boîtes, de l’ordonnance à l’alerte).
2. Une capture de `python src/demo.py Warfarin Ibuprofen Duloxetine`.
3. Le tableau de résultats et le graphique en barres de l’ablation.
4. Une diapositive « limites » avec les deux FN, les trois FP exploratoires et le principe « absence d’arête ≠ absence de risque ».

## Questions probables

- **Pourquoi pas un LLM seul ?** Il ne fournit pas nativement une preuve de graphe reproductible ; notre baseline par liste de paires isole précisément le gain de généralisation des classes.
- **Les résultats sont-ils cliniquement valides ?** Non : ils évaluent une petite référence construite pour le projet. Ils montrent la faisabilité et non une performance clinique généralisable.
- **Pourquoi conserver R12/R13 ?** Pour montrer la capacité de génération d’hypothèses du graphe, en les distinguant strictement des règles validées et en les masquant par défaut.
