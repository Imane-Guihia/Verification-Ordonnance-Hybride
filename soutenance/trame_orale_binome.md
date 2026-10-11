# Trame orale - OrdoGraph

Durée cible : **12 minutes**, puis 6 minutes de questions.  
Répartition : Étudiant·e A, 6 minutes environ ; Étudiant·e B, 6 minutes environ.

Le texte sert de guide. Ne le lisez pas mot à mot : retenez surtout les idées en gras et adaptez les phrases à votre manière de parler.

---

## Diapositive 1 - Titre (0:00 à 0:35)

**Étudiant·e A**

> Bonjour. Nous allons présenter **OrdoGraph**, un prototype de vérification d’ordonnances par graphe de connaissances et règles médicales. Notre objectif est de détecter des associations médicamenteuses à risque, de les hiérarchiser et surtout de les expliquer clairement.

> Le projet est pédagogique : il ne remplace pas un pharmacien ou un prescripteur. Il sert à montrer comment combiner des données de graphe et des règles documentées.

Transition : « Nous sommes partis d’un problème concret de prescription. »

## Diapositive 2 - Question clinique (0:35 à 1:25)

**Étudiant·e A**

> Une ordonnance peut contenir plusieurs médicaments. Certaines associations augmentent le risque de saignement, d’hyperkaliémie ou de dépression respiratoire. Le problème n’est donc pas seulement de produire une alerte, mais de produire une alerte utile.

> Nous avons retenu trois exigences : détecter les paires à risque, indiquer leur gravité, et justifier chaque alerte avec une règle et un chemin dans le graphe.

> Par exemple, Warfarin et Ibuprofen déclenchent une alerte majeure car ils appartiennent respectivement aux classes AVK et AINS, une association liée à un risque hémorragique.

Transition : « Pour obtenir ces propriétés, nous utilisons le graphe Hetionet. »

## Diapositive 3 - Données Hetionet (1:25 à 2:15)

**Étudiant·e A**

> Notre source principale est Hetionet v1.0, un graphe biomédical public de 47 031 nœuds et plus de deux millions de relations.

> Nous avons extrait quatre types de relations utiles : les classes pharmacologiques, les cibles génétiques, les effets indésirables et les maladies traitées. Les maladies traitées sont conservées dans les données, mais elles ne déclenchent pas directement d’alerte, car une indication commune ne signifie pas une interaction.

> Cette sélection limite la complexité et rend les explications plus simples à lire.

Transition : « Le graphe nous donne les propriétés ; les règles permettent ensuite de décider. »

## Diapositive 4 - Architecture (2:15 à 3:10)

**Étudiant·e A**

> Voici le fonctionnement général. On commence par une liste de médicaments, puis on normalise les noms. Par exemple, “Aspirin” est ramené à “Acetylsalicylic acid”, le nom utilisé dans Hetionet.

> Ensuite, le programme examine chaque paire de médicaments. Il recherche leurs classes, cibles et effets indésirables dans le graphe, puis applique les règles. Enfin, il fusionne les règles qui portent sur la même paire et affiche l’alerte la plus grave en premier.

> Cette fusion évite de multiplier les messages pour un seul problème clinique.

Transition : « Je vais maintenant montrer la première brique de code. »

## Diapositive 5 - Extraction du sous-graphe (3:10 à 4:00)

**Étudiant·e A**

> Cet extrait montre le chargement du sous-graphe. Nous conservons uniquement les relations PCiC, CbG, CcSE et CtD.

> La structure obtenue associe chaque médicament à ses classes, ses cibles et ses effets indésirables. Cela rend les vérifications rapides au moment de l’analyse d’une ordonnance.

> Le choix important ici est de ne pas confondre la présence d’une relation dans le graphe avec une décision clinique. Le graphe sert de preuve structurelle, mais la décision vient des règles.

Transition : « Ces règles sont la deuxième brique de notre système. »

## Diapositive 6 - Règles cliniques (4:00 à 5:05)

**Étudiant·e A**

> Nous avons écrit 11 règles cliniques sourcées. Cet exemple, R1, signale l’association entre un AVK et un AINS comme un risque hémorragique majeur.

> Chaque règle contient un type, une gravité, les propriétés recherchées sur les deux médicaments et une source médicale. Nous avons utilisé des informations de prescription FDA ou DailyMed et la recommandation UCSD pour les interactions avec la warfarine.

> Nous avons aussi ajouté deux règles exploratoires issues du graphe, mais elles sont explicitement marquées comme non vérifiées et de niveau information. Elles servent à proposer des hypothèses, pas à faire une recommandation clinique.

Transition : « Après la règle, il faut expliquer le résultat à l’utilisateur. »

## Diapositive 7 - Explication des alertes (5:05 à 6:00)

**Étudiant·e A**

> Pour chaque alerte, le programme retourne la paire de médicaments, la gravité, les identifiants des règles déclenchées, le chemin dans le graphe et la source.

> Avec Warfarin et Ibuprofen, l’utilisateur voit les deux classes pharmacologiques, la règle R1 et la source UCSD. Cette trace est importante pour l’explicabilité : l’utilisateur peut comprendre pourquoi l’alerte apparaît, au lieu de recevoir un simple score opaque.

> Je passe maintenant à la partie évaluation.

---

## Diapositive 8 - Protocole d’évaluation (6:00 à 6:55)

**Étudiant·e B**

> Nous avons construit 20 ordonnances de test, avec 25 paires attendues et des sources associées. Nous avons volontairement inclus des cas faciles, des cas avec peu de données et un cas hors distribution avec l’héparine, absente du graphe.

> Notre baseline non hybride est une simple liste de paires connues. Elle reconnaît seulement les interactions présentes explicitement dans la liste. À l’inverse, notre système peut généraliser à une classe pharmacologique.

> Nous avons aussi réalisé une ablation : nous retirons une brique, puis nous mesurons la perte de performance.

Transition : « Voici les résultats globaux. »

## Diapositive 9 - Résultats principaux (6:55 à 8:05)

**Étudiant·e B**

> Avec toutes les alertes, le système atteint un F1 de 0,902. Les règles exploratoires apportent cependant trois faux positifs.

> Quand nous n’affichons que les alertes au moins modérées, la précision devient 1,0, le rappel est de 0,88, et le F1 atteint 0,936. Nous retenons donc cette configuration pour la démonstration, car elle réduit la fatigue d’alerte.

> La baseline par liste de paires atteint un F1 de seulement 0,333. Elle est précise, mais son rappel est faible car elle ne généralise pas au-delà des paires écrites à l’avance.

Transition : « L’ablation permet de comprendre quelle brique apporte ce résultat. »

## Diapositive 10 - Ablation (8:05 à 9:10)

**Étudiant·e B**

> L’ablation la plus importante est le retrait des règles par classes. Le F1 tombe alors de 0,902 à 0,486. Les classes pharmacologiques portent donc l’essentiel de la couverture sur notre jeu de test.

> Retirer les règles de cibles ne change pas le score global ici. Cela ne veut pas dire qu’elles sont inutiles : notre jeu de test est petit et ne contient qu’un cas principal de ce type, la combinaison PDE5 et nitrates.

> Enfin, retirer les règles basées sur les effets indésirables enlève les faux positifs exploratoires et conduit à un F1 de 0,936.

Transition : « Il est important de ne pas cacher les erreurs du système. »

## Diapositive 11 - Analyse d’erreurs (9:10 à 10:20)

**Étudiant·e B**

> Nous avons deux faux négatifs. Ils viennent du graphe : Sertraline ne possède pas de classe pharmacologique exploitable dans notre sous-graphe, et Potassium chloride n’a pas la classe utile pour déclencher la règle avec Spironolactone.

> Les trois faux positifs viennent d’une seule règle, R13, qui repère des effets indésirables graves communs. Comme elle n’est pas validée cliniquement, nous la classons comme hypothèse et nous la masquons dans la configuration retenue.

> Le point central est le suivant : une absence d’arête dans Hetionet ne prouve jamais qu’il n’existe pas de risque clinique.

Transition : « Nous terminons avec les limites et la suite. »

## Diapositive 12 - Conclusion et limites (10:20 à 12:00)

**Étudiant·e A**

> OrdoGraph montre qu’un système hybride peut produire des alertes hiérarchisées et explicables. Dans la configuration retenue, il atteint un F1 de 0,936 sur notre jeu de test, tout en n’affichant en moyenne qu’environ une alerte par ordonnance.

> Ses limites sont importantes : le jeu de test est petit, le graphe est incomplet, et nous ne modélisons ni les doses, ni la durée, ni les caractéristiques du patient.

> La suite naturelle serait de faire annoter un jeu de test indépendant par un pharmacien, puis d’évaluer les règles exploratoires séparément. Merci, nous sommes prêts à répondre à vos questions.

---

## Répartition conseillée des questions

| Sujet de question | Personne qui répond d’abord |
|---|---|
| Graphe Hetionet, chargement, classes et cibles | Étudiant·e A |
| Sources médicales, gravité et règles | Étudiant·e A |
| Jeu de test, métriques et baseline | Étudiant·e B |
| Ablation, erreurs et limites | Étudiant·e B |
| Question clinique délicate | Répondre avec prudence : prototype pédagogique, vérifier la source clinique à jour |
