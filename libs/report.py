""" Fonctions permettant de créer un rapport """

import os.path
import numpy as np
import pandas as pd

##################################################
def get_distribution_types(analysis: dict):
    """
    Récupère la liste des distributions testées
    :param analysis: Résultat de l'analyse
    :return: liste des distributions
    """
    types = []
    for a in analysis['Analysis']:
        types.append(a.type)
    return types

##################################################
def make_report(distribution: np.ndarray, analysis: dict, name: str = "Report", path: str = ""):
    """
    Créé un rapport markdown
    :param distribution: Distribution originale
    :param analysis: Résultat de l'analyse
    :param name: Nom du rapport
    :param path: Chemin du rapport
    """
    dist_types = get_distribution_types(analysis)
    valid_name = name.replace(" ", "_")
    md_txt = f"# Analyse de la distribution\n\n"
    md_txt += (f"Distribution de {len(distribution)} samples ({type(distribution[0])}) "
               f"comparé avec {len(dist_types)} distributions : {', '.join(t for t in dist_types)}\n")

    # Ajout de la figure
    md_txt += f"\n## Figures de comparaison entre la distribution actuelle et celles générées\n\n"
    fig = analysis["Figure"]
    fig.tight_layout()
    fig.savefig(os.path.join(path, f"{valid_name}-001.png"), bbox_inches="tight")
    md_txt += f"![Comparaison]({valid_name}-001.png)\n"

    # Ajout du dataframe sous format de tabelau
    md_txt += f"\n## Récapitulatif des comparaisons entre la distribution actuelle et celles générées\n\n"
    md_txt += analysis["Dataframe"].to_markdown(index=False) + "\n"

    # Ajout du blabla pour chaque distribution
    md_txt += f"\n## Comparaison distribution par distribution.\n\n"
    for i in range(len(dist_types)):
        md_txt += f"\n### Distribution Originale VS {dist_types[i]}\n\n"
        a = analysis['Analysis'][i]
        md_txt += f"Paramètres de la distribution {dist_types[i]} : {a.params}\n\n"
        md_txt += f"Resultats : \n\n"
        for test, value in a.results.items():
            md_txt += f"* {test} : {value}\n"
        md_txt += f"\n"

    # Enregistrement en .md
    with open(os.path.join(path, name+".md"), 'w', encoding='utf-8') as f:
        f.write(md_txt)
    # Enregistrement du md en pdf ?
