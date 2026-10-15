# Trame orale — Vérification d'ordonnance hybride

Durée cible : **12 minutes**, puis questions.  
La trame suit les **14 diapositives** de `presentation_fusion.pptx`. Les chiffres cités sont ceux de la présentation fusionnée : 24 règles expertes, 3 règles du graphe, 40 ordonnances, 54 paires attendues, F1 de 0,92.

Ne lisez pas le texte mot à mot : gardez les idées principales et adaptez les phrases à votre façon de parler.

## Déroulé minuté

| Temps | Diapositive | Intervenant | Message principal |
|---:|---|---|---|
| 0:00–0:35 | 1. Titre | A | Présenter le projet, son objectif et son statut de prototype pédagogique. |
| 0:35–1:15 | 2. Le problème | A | Détecter des risques utiles sans créer de fatigue d'alerte. |
| 1:15–2:05 | 3. Les données | A | Hetionet est riche mais incomplet, d'où les compléments ATC et les synonymes. |
| 2:05–2:55 | 4. Architecture | A | Expliquer le passage ordonnance → paires → règles → alertes. |
| 2:55–3:50 | 5. Les règles | A | Distinguer règles expertes et signaux génériques du graphe. |
| 3:50–4:35 | 6. Une alerte expliquée | A | Montrer l'exemple warfarine + ibuprofène. |
| 4:35–5:20 | 7. Le protocole | A | Décrire le jeu de test et la référence non hybride. |
| 5:20–6:20 | 8. Résultat principal | B | Donner les métriques principales et le gain sur la référence. |
| 6:20–7:20 | 9. Ablation | B | Montrer la contribution de chaque brique. |
| 7:20–8:10 | 10. Évaluation croisée | B | Expliquer le biais d'auteur et pourquoi les scores restent optimistes. |
| 8:10–9:10 | 11. Analyse d'erreurs | B | Présenter les oublis et fausses alertes, sans les masquer. |
| 9:10–9:55 | 12. Bonus ProbLog | B | Présenter la pondération probabiliste comme un bonus. |
| 9:55–10:55 | 13. Limites et suite | B | Rappeler les limites cliniques et les améliorations nécessaires. |
| 10:55–12:00 | 14. En résumé | A + B | Conclure sur l'apport hybride et ouvrir les questions. |

---

## Diapositive 1 — Titre (0:00 à 0:35)

**Intervenant A**

> Bonjour. Nous allons présenter notre mini-projet d'IA hybride : un système de vérification d'ordonnance par graphe de connaissances et règles médicales.

> L'objectif est de signaler les associations médicamenteuses à risque, de les hiérarchiser et surtout d'expliquer chaque alerte. C'est un prototype pédagogique : il ne remplace pas la validation par un pharmacien ou un prescripteur.

Transition : « Nous sommes partis d'un problème simple à formuler, mais difficile à résoudre correctement. »

## Diapositive 2 — Le problème (0:35 à 1:15)

**Intervenant A**

> Une ordonnance peut contenir plusieurs médicaments, et certaines associations augmentent des risques comme le saignement, l'hyperkaliémie ou la toxicité.

> Le but ne consiste pas seulement à produire une alerte. Il faut détecter les paires à risque, donner leur niveau de gravité selon l'échelle de l'ANSM, puis expliquer la règle, la source et le chemin dans le graphe.

> La contrainte importante est la fatigue d'alerte : si le système alerte trop souvent pour des signaux faibles, le prescripteur peut finir par ignorer les alertes importantes.

Transition : « Pour obtenir du contexte sur les médicaments, nous utilisons Hetionet. »

## Diapositive 3 — Les données (1:15 à 2:05)

**Intervenant A**

> Notre source principale est Hetionet v1.0, un graphe biomédical public. Nous avons conservé 9 364 nœuds utiles parmi les 47 031 nœuds du graphe : médicaments, classes pharmacologiques, gènes et effets indésirables.

> Hetionet est utile, mais incomplet pour notre cas. Par exemple, seulement 47 % des médicaments y possèdent une classe pharmacologique exploitable. Certaines classes importantes, comme les statines, les IEC ou le potassium, sont absentes ou incomplètes. La warfarine n'a même aucun effet indésirable relié dans le graphe.

> Nous avons donc ajouté une table ATC de 28 classes, un dictionnaire de synonymes pour les DCI françaises et les noms commerciaux, 17 effets graves et une liste de 14 médicaments à marge thérapeutique étroite.

Transition : « Le graphe nous fournit des relations ; l'architecture combine ensuite ces relations avec des règles. »

## Diapositive 4 — Architecture (2:05 à 2:55)

**Intervenant A**

> Le système reçoit une ordonnance de deux à neuf médicaments. Il commence par reconnaître les noms, y compris les synonymes et certaines fautes de saisie.

> Il examine ensuite toutes les paires de médicaments. Pour chaque paire, il applique deux familles : les règles expertes par classe, puis les règles génériques issues du graphe.

> Enfin, il fusionne les règles déclenchées pour une même paire, trie les alertes par gravité et affiche la règle, la source et le chemin qui justifie l'alerte.

> Le filtre anti-fatigue conserve systématiquement les règles expertes. Pour les signaux génériques du graphe, il conserve seulement les alertes de niveau au moins égal à 2.

Transition : « Regardons maintenant ce que vérifient concrètement ces règles. »

## Diapositive 5 — Les règles (2:55 à 3:50)

**Intervenant A**

> Nous avons 24 règles expertes et 3 règles issues du graphe. Les règles R01 à R18 concernent des classes connues pour interagir, par exemple AVK plus AINS, statine plus inhibiteur du CYP3A4, ou dérivé nitré plus IPDE5.

> Les règles R19 à R24, ajoutées lors de la fusion, couvrent notamment ISRS ou IRSN avec AINS ou anticoagulant, antiagrégant avec AINS, digoxine avec macrolide et potassium avec épargneur de potassium.

> La règle G1 détecte un mécanisme pharmacocinétique : un médicament inhibe ou induit une enzyme à laquelle l'autre médicament est lié. G2 et G3 cherchent un effet grave partagé ou une cible commune. Ces deux dernières restent au niveau 1 et sont masquées en mode concis.

> Les sources comprennent le Thésaurus ANSM, la classification ATC de l'OMS, des RCP de l'EMA et des étiquettes FDA.

Transition : « Voici à quoi ressemble une alerte produite par le programme. »

## Diapositive 6 — Une alerte expliquée (3:50 à 4:35)

**Intervenant A**

> Dans cet exemple, nous saisissons warfarine, ibuprofène et oméprazole. Le système détecte une association déconseillée entre la warfarine et l'ibuprofène.

> La règle R01 indique une majoration du risque hémorragique. L'explication montre que la warfarine appartient à la classe des antivitamines K et que l'ibuprofène appartient à la classe des AINS. La source est le Thésaurus ANSM.

> Nous signalons aussi explicitement les limites de couverture. Par exemple, la fluindione, ou Previscan, peut être absente du graphe mais reste classée grâce à la table ATC. À l'inverse, un médicament réellement inconnu est signalé comme non vérifié.

Transition : « Après le fonctionnement, voyons comment nous l'avons évalué. »

## Diapositive 7 — Le protocole (4:35 à 5:20)

**Intervenant A**

> Nous avons fusionné les jeux du binôme pour obtenir 40 ordonnances et 54 paires à risque attendues. Chaque membre a fourni 20 ordonnances. Le jeu inclut trois ordonnances sans interaction et deux cas avec un médicament absent du graphe.

> Nous comparons le système hybride à une référence non hybride : une simple liste de 26 paires connues. Cette référence ne possède ni graphe ni classes pharmacologiques.

> Nous mesurons la précision, le rappel, le F1, l'exactitude du niveau, le nombre d'alertes par ordonnance, la cohérence et le temps de calcul. Nous avons également mené une évaluation croisée avant fusion et cinq cas de généralisation hors table.

> Seize paires et leurs niveaux restent à confirmer sur la version courante du Thésaurus ANSM.

Transition : « Je laisse maintenant la parole à B pour les résultats. »

## Diapositive 8 — Résultat principal (5:20 à 6:20)

**Intervenant B**

> Sur les 54 interactions attendues, le système hybride en trouve 48 et produit deux fausses alertes. Il atteint une précision de 0,96, un rappel de 0,89 et un F1 de 0,92.

> La configuration concise produit en moyenne 1,25 alerte par ordonnance. C'est le compromis retenu entre couverture et fatigue d'alerte.

> La référence par liste de paires a une précision de 1,00, mais un rappel de seulement 0,39 et un F1 de 0,56. Elle ne se trompe pas sur les paires qu'elle connaît, mais elle rate environ six interactions sur dix parce qu'elle ne généralise pas aux classes de médicaments.

Transition : « L'ablation aide à comprendre d'où vient ce résultat. »

## Diapositive 9 — Ablation (6:20 à 7:20)

**Intervenant B**

> L'hybride complet atteint un F1 de 0,92. Quand nous retirons le filtre de marge thérapeutique étroite, le F1 descend à 0,81. Sans les règles R19 à R24, il tombe à 0,80. Sans la table ATC, il tombe à 0,71.

> Ces résultats montrent que la table complémentaire et les règles ajoutées lors de la fusion apportent une couverture importante face aux manques du graphe.

> Un graphe seul, avec seulement G1 à G3, atteint 0,31. Et si nous supprimons le filtre anti-fatigue, le rappel monte à 0,94, mais le système produit 70 fausses alertes sur 40 ordonnances. Le filtre améliore donc directement l'utilité de la sortie.

Transition : « Nous avons aussi vérifié le risque de biais lié à la construction du jeu de test. »

## Diapositive 10 — Évaluation croisée avant la fusion (7:20 à 8:10)

**Intervenant B**

> Avant la fusion, chaque version était meilleure sur son propre jeu de test. La version d'Imane passe de 0,83 sur son jeu à 0,76 sur celui d'Aziz. La version d'Aziz passe de 0,94 sur son jeu à 0,38 sur celui d'Imane.

> La leçon est claire : lorsqu'une même personne construit les règles et les données de test, le score peut être optimiste.

> Après fusion, les règles R19 à R24 ont été ajoutées après consultation des ordonnances d'Aziz. Le F1 de 0,98 sur ces ordonnances reste donc optimiste. Nous l'indiquons explicitement plutôt que de présenter ce score comme une validation indépendante.

Transition : « Regardons maintenant les erreurs restantes. »

## Diapositive 11 — Analyse d'erreurs (8:10 à 9:10)

**Intervenant B**

> Nous attribuons les huit erreurs à une brique précise. Trois oublis viennent du filtre anti-fatigue. Par exemple, le graphe relie allopurinol et azathioprine à une cible commune, XDH, mais le signal de niveau 1 est masqué.

> Trois autres oublis viennent de règles manquantes : digoxine avec furosémide et simvastatine avec amlodipine ne sont pas couverts par les règles disponibles ni par le graphe.

> Nous avons aussi deux fausses alertes. La première vient d'une classe trop large : le graphe classe l'aspirine comme AINS, sans considérer son usage à dose antiagrégante. La seconde vient de G1 : le graphe ne code pas la force de l'inhibition de l'oméprazole sur la warfarine.

> L'absence d'arête dans Hetionet ne prouve donc jamais l'absence de risque clinique.

Transition : « La diapositive suivante présente le bonus probabiliste. »

## Diapositive 12 — Bonus ProbLog (9:10 à 9:55)

**Intervenant B**

> En bonus, nous avons traduit les règles en une version pondérée avec ProbLog. L'idée est de classer les alertes par probabilité, et non de remplacer les règles cliniques par une décision opaque.

> Sur 152 paires, cette version obtient une AUC de 0,93 et une erreur de calibration de 0,07. Au seuil de 0,5, elle conserve 47 des 48 vraies alertes.

> Les poids ont été fixés avant l'évaluation. La pondération sert principalement à ordonner les alertes ; la tranche de probabilité entre 0,2 et 0,4 reste surestimée.

Transition : « Ces résultats doivent être interprétés avec prudence, car le prototype a des limites importantes. »

## Diapositive 13 — Limites et suite (9:55 à 10:55)

**Intervenant B**

> Notre première limite est la couverture : Hetionet date de 2017, il est incomplet et statique. Le système ne modélise ni les doses, ni les données patient, ni l'intensité réelle des inhibiteurs enzymatiques.

> La vérité terrain a été construite par le binôme. Seize niveaux restent à confirmer, et certaines règles ainsi que le filtre ont été ajoutés après l'analyse du jeu de test. Les résultats ne constituent donc pas une validation clinique.

> La suite consiste à faire annoter un jeu de test indépendant par un pharmacien, à intégrer les doses et la force des inhibiteurs, puis à apprendre ou recalibrer les poids ProbLog. Les embeddings, comme TransE, resteraient des générateurs d'hypothèses et non une recommandation clinique directe.

Transition : « Nous terminons avec le message principal du projet. »

## Diapositive 14 — En résumé (10:55 à 12:00)

**Intervenants A puis B**

**A :**

> Notre apport principal est de combiner les règles et le graphe : les règles donnent une gravité et une source explicites, tandis que le graphe aide à généraliser au-delà d'une liste de paires figée.

**B :**

> Sur notre jeu fusionné, cette approche atteint un F1 de 0,92 contre 0,56 pour la référence, avec 1,25 alerte par ordonnance et une explication pour chaque alerte.

**A :**

> Nous insistons néanmoins sur le fait qu'il s'agit d'un prototype pédagogique. Une validation indépendante par un professionnel de santé reste indispensable.

> Merci pour votre attention, nous sommes prêts à répondre à vos questions.

---

## Répartition conseillée des questions

| Sujet | Répond en premier |
|---|---|
| Hetionet, sous-graphe, synonymes, classes et architecture | A |
| Règles, sources médicales, niveaux de gravité | A |
| Métriques, ablation, évaluation croisée, ProbLog | B |
| Limites, biais du jeu de test, généralisation | B |
| Question clinique précise | Réponse prudente : prototype pédagogique, vérification nécessaire dans une source clinique à jour |
