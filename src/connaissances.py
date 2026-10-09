"""Connaissances expertes ajoutées au graphe Hetionet.

Trois éléments :
1. SYNONYMES : DCI françaises et noms commerciaux -> nom DrugBank utilisé dans Hetionet.
2. CLASSES   : classes thérapeutiques utilisées par les règles. Chaque classe réunit
               - des classes pharmacologiques du graphe (arêtes PCiC),
               - une table complémentaire (classification ATC de l'OMS) pour les
                 médicaments que le graphe ne classe pas.
3. EFFETS_GRAVES et préfixes de gènes « non pharmacodynamiques » (enzymes, transporteurs).

Sources : WHO Collaborating Centre for Drug Statistics Methodology, ATC/DDD Index
(https://atcddd.fhi.no/atc_ddd_index/) ; ANSM, Thésaurus des interactions
médicamenteuses (https://ansm.sante.fr). Voir donnees/sources.md.
"""
import unicodedata


def normaliser(texte):
    """Minuscules, sans accents, sans espaces superflus."""
    t = unicodedata.normalize("NFKD", str(texte)).encode("ascii", "ignore").decode()
    return " ".join(t.lower().replace("-", " ").split())


# ---------------------------------------------------------------------------
# 1. Synonymes (clé normalisée -> nom Hetionet / DrugBank)
# ---------------------------------------------------------------------------
_SYN = {
    # anticoagulants / antiagrégants
    "warfarine": "Warfarin", "coumadine": "Warfarin",
    "acenocoumarol": "Acenocoumarol", "sintrom": "Acenocoumarol",
    "fluindione": "Fluindione", "previscan": "Fluindione",
    "apixaban": "Apixaban", "eliquis": "Apixaban",
    "rivaroxaban": "Rivaroxaban", "xarelto": "Rivaroxaban",
    "dabigatran": "Dabigatran etexilate", "pradaxa": "Dabigatran etexilate",
    "enoxaparine": "Enoxaparin", "lovenox": "Enoxaparin",
    "aspirine": "Acetylsalicylic acid", "acide acetylsalicylique": "Acetylsalicylic acid",
    "kardegic": "Acetylsalicylic acid", "aspegic": "Acetylsalicylic acid",
    "clopidogrel": "Clopidogrel", "plavix": "Clopidogrel",
    "ticagrelor": "Ticagrelor", "brilique": "Ticagrelor", "prasugrel": "Prasugrel",
    # AINS
    "ibuprofene": "Ibuprofen", "advil": "Ibuprofen", "nurofen": "Ibuprofen",
    "ketoprofene": "Ketoprofen", "profenid": "Ketoprofen", "bi profenid": "Ketoprofen",
    "naproxene": "Naproxen", "apranax": "Naproxen",
    "diclofenac": "Diclofenac", "voltarene": "Diclofenac",
    "celecoxib": "Celecoxib", "celebrex": "Celecoxib", "indometacine": "Indomethacin",
    "meloxicam": "Meloxicam", "mobic": "Meloxicam", "piroxicam": "Piroxicam", "feldene": "Piroxicam",
    "ticlopidine": "Ticlopidine",
    # statines / inhibiteurs CYP3A4
    "simvastatine": "Simvastatin", "zocor": "Simvastatin",
    "atorvastatine": "Atorvastatin", "tahor": "Atorvastatin",
    "lovastatine": "Lovastatin", "pravastatine": "Pravastatin", "elisor": "Pravastatin",
    "rosuvastatine": "Rosuvastatin", "crestor": "Rosuvastatin",
    "clarithromycine": "Clarithromycin", "zeclar": "Clarithromycin",
    "erythromycine": "Erythromycin", "ketoconazole": "Ketoconazole",
    "itraconazole": "Itraconazole", "sporanox": "Itraconazole",
    "fluconazole": "Fluconazole", "triflucan": "Fluconazole",
    "ritonavir": "Ritonavir", "norvir": "Ritonavir",
    # nitrés / IPDE5
    "trinitrine": "Nitroglycerin", "nitroglycerine": "Nitroglycerin", "natispray": "Nitroglycerin",
    "isosorbide mononitrate": "Isosorbide Mononitrate", "monicor": "Isosorbide Mononitrate",
    "isosorbide dinitrate": "Isosorbide Dinitrate", "risordan": "Isosorbide Dinitrate",
    "sildenafil": "Sildenafil", "viagra": "Sildenafil",
    "tadalafil": "Tadalafil", "cialis": "Tadalafil", "vardenafil": "Vardenafil",
    # psychotropes / antalgiques
    "fluoxetine": "Fluoxetine", "prozac": "Fluoxetine",
    "sertraline": "Sertraline", "zoloft": "Sertraline",
    "paroxetine": "Paroxetine", "deroxat": "Paroxetine",
    "citalopram": "Citalopram", "seropram": "Citalopram",
    "escitalopram": "Escitalopram", "seroplex": "Escitalopram",
    "phenelzine": "Phenelzine", "tranylcypromine": "Tranylcypromine",
    "linezolide": "Linezolid", "zyvoxid": "Linezolid",
    "tramadol": "Tramadol", "contramal": "Tramadol", "topalgic": "Tramadol",
    "morphine": "Morphine", "skenan": "Morphine",
    "oxycodone": "Oxycodone", "oxycontin": "Oxycodone",
    "fentanyl": "Fentanyl", "durogesic": "Fentanyl", "codeine": "Codeine",
    "diazepam": "Diazepam", "valium": "Diazepam",
    "alprazolam": "Alprazolam", "xanax": "Alprazolam",
    "lorazepam": "Lorazepam", "temesta": "Lorazepam",
    "zolpidem": "Zolpidem", "stilnox": "Zolpidem",
    "lithium": "Lithium", "teralithe": "Lithium",
    "haloperidol": "Haloperidol", "haldol": "Haloperidol",
    "paracetamol": "Acetaminophen", "doliprane": "Acetaminophen", "dafalgan": "Acetaminophen",
    "efferalgan": "Acetaminophen",
    # cardio / rein
    "lisinopril": "Lisinopril", "zestril": "Lisinopril",
    "enalapril": "Enalapril", "renitec": "Enalapril",
    "ramipril": "Ramipril", "triatec": "Ramipril",
    "perindopril": "Perindopril", "coversyl": "Perindopril",
    "losartan": "Losartan", "cozaar": "Losartan", "valsartan": "Valsartan", "tareg": "Valsartan",
    "spironolactone": "Spironolactone", "aldactone": "Spironolactone",
    "eplerenone": "Eplerenone", "inspra": "Eplerenone", "amiloride": "Amiloride",
    "furosemide": "Furosemide", "lasilix": "Furosemide",
    "hydrochlorothiazide": "Hydrochlorothiazide", "esidrex": "Hydrochlorothiazide",
    "digoxine": "Digoxin",
    "amiodarone": "Amiodarone", "cordarone": "Amiodarone",
    "sotalol": "Sotalol", "sotalex": "Sotalol",
    "quinidine": "Quinidine", "verapamil": "Verapamil", "isoptine": "Verapamil",
    "bisoprolol": "Bisoprolol", "cardensiel": "Bisoprolol", "detensiel": "Bisoprolol",
    "atenolol": "Atenolol", "amlodipine": "Amlodipine", "amlor": "Amlodipine",
    # divers
    "methotrexate": "Methotrexate", "novatrex": "Methotrexate", "imeth": "Methotrexate",
    "trimethoprime": "Trimethoprim",
    "omeprazole": "Omeprazole", "mopral": "Omeprazole",
    "esomeprazole": "Esomeprazole", "inexium": "Esomeprazole",
    "pantoprazole": "Pantoprazole", "inipomp": "Pantoprazole", "eupantol": "Pantoprazole",
    "allopurinol": "Allopurinol", "zyloric": "Allopurinol",
    "azathioprine": "Azathioprine", "imurel": "Azathioprine",
    "colchicine": "Colchicine",
    "metformine": "Metformin", "glucophage": "Metformin",
    "glibenclamide": "Glyburide", "daonil": "Glyburide", "gliclazide": "Gliclazide",
    "levothyroxine": "Levothyroxine", "levothyrox": "Levothyroxine",
    "amoxicilline": "Amoxicillin", "clamoxyl": "Amoxicillin",
    "prednisone": "Prednisone", "cortancyl": "Prednisone",
    "prednisolone": "Prednisolone", "solupred": "Prednisolone",
    "dompéridone": "Domperidone", "domperidone": "Domperidone", "motilium": "Domperidone",
    "hydroxychloroquine": "Hydroxychloroquine", "plaquenil": "Hydroxychloroquine",
    "ondansetron": "Ondansetron", "zophren": "Ondansetron",
    "carbamazepine": "Carbamazepine", "tegretol": "Carbamazepine",
    "rifampicine": "Rifampicin", "rifadine": "Rifampicin",
    "ciprofloxacine": "Ciprofloxacin", "ciflox": "Ciprofloxacin",
    "theophylline": "Theophylline",
}
SYNONYMES = {normaliser(k): v for k, v in _SYN.items()}


# ---------------------------------------------------------------------------
# 2. Classes thérapeutiques : classes du graphe (PCiC) + table ATC complémentaire
# ---------------------------------------------------------------------------
CLASSES = {
    "AVK": {
        "libelle": "antivitamines K",
        "pcic": ["Vitamin K Inhibitors"],
        "table": {"Warfarin": "B01AA03", "Acenocoumarol": "B01AA07",
                  "Fluindione": "B01AA12", "Phenprocoumon": "B01AA04"},
    },
    "AOD": {
        "libelle": "anticoagulants oraux directs",
        "pcic": [],
        "table": {"Apixaban": "B01AF02", "Rivaroxaban": "B01AF01",
                  "Dabigatran etexilate": "B01AE07"},
    },
    "HEPARINE": {
        "libelle": "héparines",
        "pcic": ["Heparin, Low-Molecular-Weight"],
        "table": {"Enoxaparin": "B01AB05"},
    },
    "ANTIAGREGANT": {
        "libelle": "antiagrégants plaquettaires",
        "pcic": ["Decreased Platelet Aggregation", "P2Y12 Receptor Antagonists"],
        "table": {"Acetylsalicylic acid": "B01AC06", "Clopidogrel": "B01AC04",
                  "Ticagrelor": "B01AC24", "Prasugrel": "B01AC22"},
    },
    "AINS": {
        "libelle": "anti-inflammatoires non stéroïdiens",
        "pcic": ["Nonsteroidal Anti-inflammatory Compounds"],
        "table": {"Ibuprofen": "M01AE01", "Naproxen": "M01AE02",
                  "Ketoprofen": "M01AE03", "Diclofenac": "M01AB05"},
    },
    "STATINE_3A4": {
        "libelle": "statines métabolisées par le CYP3A4",
        "pcic": [],
        "table": {"Simvastatin": "C10AA01", "Lovastatin": "C10AA02", "Atorvastatin": "C10AA05"},
    },
    "INHIB_3A4_FORT": {
        "libelle": "inhibiteurs puissants du CYP3A4",
        "pcic": [],
        "table": {"Clarithromycin": "J01FA09", "Erythromycin": "J01FA01",
                  "Ketoconazole": "J02AB02", "Itraconazole": "J02AC02", "Ritonavir": "J05AE03"},
    },
    "NITRE": {
        "libelle": "dérivés nitrés",
        "pcic": ["Nitrates"],
        "table": {"Nitroglycerin": "C01DA02", "Isosorbide Dinitrate": "C01DA08",
                  "Isosorbide Mononitrate": "C01DA14"},
    },
    "IPDE5": {
        "libelle": "inhibiteurs de la phosphodiestérase de type 5",
        "pcic": ["Phosphodiesterase 5 Inhibitors"],
        "table": {"Sildenafil": "G04BE03", "Tadalafil": "G04BE08", "Vardenafil": "G04BE09"},
    },
    "ISRS": {
        "libelle": "inhibiteurs sélectifs de la recapture de la sérotonine",
        "pcic": ["Serotonin Uptake Inhibitors"],
        "table": {"Fluoxetine": "N06AB03", "Citalopram": "N06AB04", "Paroxetine": "N06AB05",
                  "Sertraline": "N06AB06", "Escitalopram": "N06AB10"},
    },
    "IMAO_NS": {
        "libelle": "IMAO non sélectifs",
        "pcic": [],
        "table": {"Phenelzine": "N06AF03", "Tranylcypromine": "N06AF04"},
    },
    "SEROTONINERGIQUE": {
        "libelle": "autres médicaments sérotoninergiques",
        "pcic": [],
        "table": {"Tramadol": "N02AX02", "Linezolid": "J01XX08"},
    },
    "IEC": {
        "libelle": "inhibiteurs de l'enzyme de conversion",
        "pcic": [],
        "table": {"Enalapril": "C09AA02", "Lisinopril": "C09AA03",
                  "Perindopril": "C09AA04", "Ramipril": "C09AA05"},
    },
    "ARA2": {
        "libelle": "antagonistes des récepteurs de l'angiotensine II",
        "pcic": ["Angiotensin 2 Receptor Antagonists", "Angiotensin 2 Type 1 Receptor Antagonists"],
        "table": {"Losartan": "C09CA01", "Valsartan": "C09CA03"},
    },
    "EPARGNEUR_K": {
        "libelle": "diurétiques épargneurs de potassium",
        "pcic": ["Aldosterone Antagonists"],
        "table": {"Spironolactone": "C03DA01", "Eplerenone": "C03DA04", "Amiloride": "C03DB01"},
    },
    "METHOTREXATE": {
        "libelle": "méthotrexate",
        "pcic": [],
        "table": {"Methotrexate": "L04AX03"},
    },
    "ANTIFOLIQUE": {
        "libelle": "autres antifoliques",
        "pcic": ["Dihydrofolate Reductase Inhibitors"],
        "table": {"Trimethoprim": "J01EA01"},
    },
    "DIGITALIQUE": {
        "libelle": "digitaliques",
        "pcic": ["Cardiac Glycosides"],
        "table": {"Digoxin": "C01AA05"},
    },
    "INHIB_PGP": {
        "libelle": "inhibiteurs de la glycoprotéine P",
        "pcic": ["P-Glycoprotein Inhibitors"],
        "table": {},
    },
    "TORSADOGENE": {
        "libelle": "médicaments torsadogènes",
        "pcic": [],
        "table": {"Amiodarone": "C01BD01", "Sotalol": "C07AA07", "Quinidine": "C01BA01",
                  "Haloperidol": "N05AD01", "Citalopram": "N06AB04", "Escitalopram": "N06AB10",
                  "Domperidone": "A03FA03", "Hydroxychloroquine": "P01BA02",
                  "Erythromycin": "J01FA01"},
    },
    "OPIOIDE": {
        "libelle": "opioïdes",
        "pcic": ["Full Opioid Agonists", "Partial Opioid Agonists", "Opioid Agonists"],
        "table": {"Morphine": "N02AA01", "Oxycodone": "N02AA05", "Fentanyl": "N02AB03",
                  "Codeine": "R05DA04", "Tramadol": "N02AX02"},
    },
    "BZD_HYPNOTIQUE": {
        "libelle": "benzodiazépines et apparentés",
        "pcic": ["Benzodiazepines"],
        "table": {"Diazepam": "N05BA01", "Lorazepam": "N05BA06", "Alprazolam": "N05BA12",
                  "Zolpidem": "N05CF02"},
    },
    "INHIB_2C19": {
        "libelle": "inhibiteurs du CYP2C19",
        "pcic": ["Cytochrome P450 2C19 Inhibitors"],
        "table": {"Omeprazole": "A02BC01", "Esomeprazole": "A02BC05"},
    },
    "CLOPIDOGREL": {
        "libelle": "clopidogrel",
        "pcic": [],
        "table": {"Clopidogrel": "B01AC04"},
    },
    "LITHIUM": {
        "libelle": "lithium",
        "pcic": [],
        "table": {"Lithium": "N05AN01"},
    },
}

# Groupes de classes (pour écrire des règles plus courtes)
GROUPES = {
    "ANTICOAGULANT": ["AVK", "AOD", "HEPARINE"],
    "SRAA": ["IEC", "ARA2"],
    "SEROTONINERGIQUE_LARGE": ["ISRS", "SEROTONINERGIQUE"],
}


# ---------------------------------------------------------------------------
# 3. Effets indésirables graves (nom Hetionet -> niveau de l'alerte générique)
# ---------------------------------------------------------------------------
EFFETS_GRAVES = {
    "Haemorrhage": 2, "Gastrointestinal haemorrhage": 2,
    "Hyperkalaemia": 2, "Rhabdomyolysis": 2, "Serotonin syndrome": 2,
    "Torsade de pointes": 2, "Electrocardiogram QT prolonged": 2, "Long QT syndrome": 2,
    "Respiratory depression": 2, "Lithium toxicity": 2, "Hypoglycaemia": 2,
    "Agranulocytosis": 2, "Pancytopenia": 2,
    "Renal failure acute": 1, "Hypotension": 1, "Bradycardia": 1, "Convulsion": 1,
}

# Gènes de métabolisme et de transport : liaison commune = pas une cible d'action commune
PREFIXES_NON_PD = ("CYP", "UGT", "GST", "SULT", "NAT", "CES", "FMO", "ABC",
                   "SLCO", "SLC22A", "SLC15A", "SLC47A")
GENES_NON_PD = {"ALB", "ORM1", "ORM2"}

# Enzymes / transporteurs utilisés par la règle pharmacocinétique générique :
# classe Hetionet (inhibiteur ou inducteur) -> gène lié par le médicament « victime »
ENZYMES_PK = {
    "CYP3A4": ("Cytochrome P450 3A4 Inhibitors", "Cytochrome P450 3A4 Inducers"),
    "CYP2C9": ("Cytochrome P450 2C9 Inhibitors", "Cytochrome P450 2C9 Inducers"),
    "CYP2C19": ("Cytochrome P450 2C19 Inhibitors", "Cytochrome P450 2C19 Inducers"),
    "CYP2D6": ("Cytochrome P450 2D6 Inhibitors", None),
    "CYP1A2": ("Cytochrome P450 1A2 Inhibitors", "Cytochrome P450 1A2 Inducers"),
    "ABCB1": ("P-Glycoprotein Inhibitors", None),
}


# Médicaments à marge thérapeutique étroite (ou à toxicité dose-dépendante grave) :
# une hausse modeste de leur concentration suffit à provoquer une toxicité.
# Utilisé pour filtrer la règle pharmacocinétique G1.
# Source : ANSM, Thésaurus (interactions imposant une surveillance de l'INR, de la
# glycémie ou des concentrations plasmatiques). Liste à valider par le groupe.
MARGE_ETROITE = {
    "Warfarin", "Acenocoumarol", "Fluindione", "Phenprocoumon",   # AVK : INR
    "Digoxin", "Lithium", "Theophylline", "Carbamazepine",         # dosages plasmatiques
    "Colchicine", "Methotrexate", "Azathioprine", "Mercaptopurine",
    "Glyburide", "Gliclazide",                                     # hypoglycémie
}


def est_pharmacodynamique(gene):
    return gene not in GENES_NON_PD and not gene.startswith(PREFIXES_NON_PD)
